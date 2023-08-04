import os
import sys
import hashlib
import json
from library.chatgpt import call_gpt_4

CONFIG_FILE = "config.json"
PROMPT_EXT = ".prompt"
CHECKSUM_EXT = ".prompt.checksum"
OUTPUT_EXT = ".output"


def read_config():
    if not os.path.exists(CONFIG_FILE):
        gpt_4_key = input("Please enter your GPT-4 key: ")
        with open(CONFIG_FILE, 'w') as config_file:
            json.dump({"gpt_4_key": gpt_4_key}, config_file)
        print(f"Config file {CONFIG_FILE} created.")
        sys.exit(0)

    with open(CONFIG_FILE, 'r') as config_file:
        config = json.load(config_file)
    return config


def calculate_checksum(file_path):
    hasher = hashlib.md5()
    with open(file_path, 'rb') as file:
        buf = file.read()
        hasher.update(buf)
    return hasher.hexdigest()


def process_file(file_path, gpt_4_key):
    checksum_file = file_path + CHECKSUM_EXT
    new_checksum = calculate_checksum(file_path)

    if os.path.exists(checksum_file):
        with open(checksum_file, 'r') as f:
            old_checksum = f.read().strip()
        if old_checksum == new_checksum:
            print(f"No changes detected in {file_path}")
            return
    else:
        print(f"No checksum file detected for {file_path}. Processing file.")

    with open(checksum_file, 'w') as f:
        f.write(new_checksum)

    prepared_prompt = []
    output_file_name = None

    with open(file_path, 'r') as file:
        for line in file:
            if line.startswith("#include"):
                include_file_path = line.strip().split(" ")[1]
                with open(include_file_path, 'r') as include_file:
                    prepared_prompt.append(include_file.read())
            elif line.startswith("#write-to"):
                output_file_name = line.strip().split(" ")[1]
            else:
                prepared_prompt.append(line.strip())

    prepared_prompt = "\n".join(prepared_prompt)
    output = call_gpt_4(gpt_4_key, prepared_prompt)

    with open(file_path + OUTPUT_EXT, 'w') as output_file:
        output_file.write(output)

    if output_file_name:
        post_process_output(output, output_file_name)


def post_process_output(output, output_file_name):
    start = output.find("```")
    end = output.rfind("```")
    content = output[start:end].strip("`")

    with open(output_file_name, 'w') as output_file:
        output_file.write(content)


def main():
    config = read_config()
    root_dir = sys.argv[1] if len(sys.argv) > 1 else os.getcwd()
    for dirpath, _, filenames in os.walk(root_dir):
        for filename in filenames:
            if filename.endswith(PROMPT_EXT):
                file_path = os.path.join(dirpath, filename)
                print(f"Processing file: {file_path}")
                process_file(file_path, config["gpt_4_key"])


if __name__ == "__main__":
    main()