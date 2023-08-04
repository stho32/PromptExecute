use std::collections::HashMap;
use std::fs::File;
use std::io::{Read, Write};
use std::path::Path;

use md5::Md5;
use serde::{Deserialize, Serialize};
use walkdir::WalkDir;

use reqwest::Client;
use tokio::io::AsyncWriteExt;

#[derive(Serialize, Deserialize, Debug)]
struct Config {
    gpt_4_key: String,
}

// Function to handle GPT-4 API requests
async fn gpt_4_request(api_key: &str, prompt: &str) -> Result<String, reqwest::Error> {
    let client = Client::new();
    let mut map = HashMap::new();
    map.insert("prompt", prompt);

    let res = client
        .post("https://api.openai.com/v4/engines/davinci-codex/completions")
        .header("Authorization", format!("Bearer {}", api_key))
        .json(&map)
        .send()
        .await?;

    let response_body: HashMap<String, String> = res.json().await?;
    Ok(response_body["choices"].clone())
}

fn calculate_md5<T: AsRef<Path>>(path: T) -> std::io::Result<String> {
    let mut file = File::open(path)?;
    let mut buffer = Vec::new();
    file.read_to_end(&mut buffer)?;

    let digest = Md5::digest(&buffer);
    Ok(format!("{:x}", digest))
}

fn main() -> std::io::Result<()> {
    let config_path = "./config.json";
    let mut config: Config;

    if Path::new(config_path).exists() {
        let file = File::open(config_path)?;
        config = serde_json::from_reader(file)?;
    } else {
        println!("Please enter your GPT-4 key:");
        let mut gpt_4_key = String::new();
        std::io::stdin().read_line(&mut gpt_4_key)?;

        config = Config { gpt_4_key };
        let file = File::create(config_path)?;
        serde_json::to_writer(file, &config)?;
        return Ok(());
    }

    let paths = WalkDir::new(".")
        .into_iter()
        .filter_map(|entry| entry.ok())
        .filter(|entry| entry.path().is_file() && entry.path().extension().unwrap() == "prompt");

    for path in paths {
        let prompt_path = path.path();
        let prompt_checksum_path = prompt_path.with_extension("prompt.checksum");
        let prompt_output_path = prompt_path.with_extension("prompt.output");

        let calculated_checksum = calculate_md5(prompt_path)?;
        let mut existing_checksum = String::new();

        if prompt_checksum_path.exists() {
            let mut file = File::open(prompt_checksum_path)?;
            file.read_to_string(&mut existing_checksum)?;
        }

        if calculated_checksum != existing_checksum {
            let mut file = File::create(prompt_checksum_path)?;
            file.write_all(calculated_checksum.as_bytes())?;

            let mut prompt = String::new();
            let mut file = File::open(prompt_path)?;
            file.read_to_string(&mut prompt)?;

            let prepared_prompt: Vec<String> = prompt
                .lines()
                .map(|line| {
                    if line.starts_with("#include") {
                        let include_path = line[8..].trim();
                        let mut included_file = String::new();
                        if let Ok(mut file) = File::open(include_path) {
                            let _ = file.read_to_string(&mut included_file);
                        }
                        included_file
                    } else {
                        line.to_string()
                    }
                })
                .collect();

            let result = futures::executor::block_on(gpt_4_request(&config.gpt_4_key, &prepared_prompt.join("\n")))?;

            let mut file = File::create(prompt_output_path)?;
            file.write_all(result.as_bytes())?;
        }
    }

    Ok(())
}
