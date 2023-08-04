import os
import hashlib
import json
import argparse
from library.chatgpt import call_gpt_4

CONFIG_FILE = "config.json"
PROMPT_EXTENSION = ".prompt"
CHECKSUM_EXTENSION = ".prompt.checksum"
OUTPUT_EXTENSION = ".output"
INCLUDE_PREFIX = "#include"
WRITE_TO_PREFIX = "#write-to"
CODE_BLOCK = "```"

def create_checksum(file_path):
    hasher = hashlib.md5()
    with open(file_path, 'rb') as file:
        buf = file.read()
        hasher.update(buf)
    return hasher.hexdigest()

def write_checksum(file_path, checksum):
    with open(file_path + CHECKSUM_EXTENSION, 'w') as file:
        file.write(checksum)

def read_config():
    if not os.path.exists(CONFIG_FILE):
        gpt_4_key = input("Please enter your GPT-4 key: ")
        with open(CONFIG_FILE, 'w') as file:
            json.dump({"gpt_4_key": gpt_4_key}, file)
        print(f"Configuration file {CONFIG_FILE} has been created.")
        exit(0)
    else:
        with open(CONFIG_FILE, 'r') as file:
            config = json.load(file)
        return config["gpt_4_key"]

def process_prompt_file(file_path, gpt_4_key):
    print(f"Processing {file_path}...")

    checksum = create_checksum(file_path)
    if os.path.exists(file_path + CHECKSUM_EXTENSION):
        with open(file_path + CHECKSUM_EXTENSION, 'r') as file:
            old_checksum = file.read()
        if old_checksum == checksum:
            print(f"No changes detected in {file_path}. Skipping...")
            return
    write_checksum(file_path, checksum)

    prepared_prompt = []
    output_file_name = None
    with open(file_path, 'r') as file:
        for line in file:
            if line.startswith(INCLUDE_PREFIX):
                include_file = line[len(INCLUDE_PREFIX):].strip()
                with open(include_file, 'r') as inc_file:
                    prepared_prompt.append(inc_file.read())
            elif line.startswith(WRITE_TO_PREFIX):
                output_file_name = line[len(WRITE_TO_PREFIX):].strip()
            else:
                prepared_prompt.append(line)

    response = call_gpt_4(gpt_4_key, ''.join(prepared_prompt))
    with open(file_path + OUTPUT_EXTENSION, 'w') as file:
        file.write(response)

    if output_file_name:
        post_process_output(response, output_file_name)

def post_process_output(output, output_file_name):
    print(f"Post processing output to {output_file_name}...")
    code_block_contents = output[output.find(CODE_BLOCK)+len(CODE_BLOCK):output.rfind(CODE_BLOCK)]
    with open(output_file_name, 'w') as file:
        file.write(code_block_contents)

def walk_directory(directory, gpt_4_key):
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith(PROMPT_EXTENSION):
                process_prompt_file(os.path.join(root, file), gpt_4_key)

def main():
    parser = argparse.ArgumentParser(description='Walks through a directory structure looking for .prompt files.')
    parser.add_argument('directory', nargs='?', default=os.getcwd())
    args = parser.parse_args()

    gpt_4_key = read_config()
    walk_directory(args.directory, gpt_4_key)

if __name__ == "__main__":
    main()
