
import os
import sys
import json
import hashlib
from library.chatgpt import call_gpt_4
from library.interface_creator import extract_functions

CONFIG_FILE = "config.json"
GPT4_KEY = "gpt_4_key"
PROMPT_EXT = ".prompt"
CHECKSUM_EXT = ".prompt.checksum"
COMPLETED_EXT = ".prompt.completed"
OUTPUT_EXT = ".prompt.output"
INTERFACE_EXT = ".interface"

def get_gpt4_key():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE) as f:
            config = json.load(f)
            return config.get(GPT4_KEY)
    else:
        key = input("Please enter your GPT-4 key: ")
        with open(CONFIG_FILE, 'w') as f:
            json.dump({GPT4_KEY: key}, f)
        print(f"Config file {CONFIG_FILE} has been created.")
        sys.exit(0)

def process_prompt_file(filepath, gpt4_key):
    print(f"Processing file: {filepath}")
    with open(filepath) as f:
        lines = f.readlines()

    checksum = hashlib.md5(''.join(lines).encode()).hexdigest()
    checksum_file = filepath + CHECKSUM_EXT

    if os.path.exists(checksum_file):
        with open(checksum_file) as f:
            old_checksum = f.read().strip()
        if old_checksum == checksum:
            print(f"No changes in {filepath}. Skipping.")
            return
    with open(checksum_file, 'w') as f:
        f.write(checksum)

    prepared_prompt = ""
    output_file_name = ""
    create_interface = False

    for line in lines:
        if line.startswith("#include"):
            include_file = os.path.join(os.path.dirname(filepath), line.split()[1].strip())
            with open(include_file) as f:
                prepared_prompt += f.read()
        elif line.startswith("#write-to"):
            output_file_name = os.path.join(os.path.dirname(filepath), line.split()[1].strip())
        elif line.startswith("#create-interface"):
            create_interface = True
        else:
            prepared_prompt += line

    with open(filepath + COMPLETED_EXT, 'w') as f:
        f.write(prepared_prompt)

    gpt4_output = call_gpt_4(gpt4_key, prepared_prompt)

    with open(filepath + OUTPUT_EXT, 'w') as f:
        f.write(gpt4_output)

    if output_file_name:
        post_process(gpt4_output, output_file_name, create_interface)

def post_process(gpt4_output, output_file_name, create_interface):
    print(f"Post processing for: {output_file_name}")
    lines = gpt4_output.split('\n')
    code_lines = []

    start = False
    for line in lines:
        if line.strip() == "```":
            start = not start
            continue
        if start:
            code_lines.append(line)

    with open(output_file_name, 'w') as f:
        f.write('\n'.join(code_lines))

    if create_interface:
        interface_content = extract_functions('\n'.join(code_lines), output_file_name)
        with open(output_file_name + INTERFACE_EXT, 'w') as f:
            f.write(interface_content)

def walk_directory(directory, gpt4_key):
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith(PROMPT_EXT):
                process_prompt_file(os.path.join(root, file), gpt4_key)

def main():
    directory = sys.argv[1] if len(sys.argv) > 1 else os.getcwd()
    gpt4_key = get_gpt4_key()
    if not gpt4_key:
        print("GPT-4 key is not found in the config file.")
        sys.exit(1)
    walk_directory(directory, gpt4_key)

if __name__ == "__main__":
    main()
