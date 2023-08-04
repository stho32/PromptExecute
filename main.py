import os
import json
import hashlib
import argparse
from pathlib import Path
from library.chatgpt import call_gpt_4
from library.interface_creator import extract_functions
import re

CONFIG_FILE = 'config.json'
GPT4_KEY = 'gpt_4_key'

def read_config():
    if not os.path.exists(CONFIG_FILE):
        gpt_4_key = input('Please enter GPT-4 key: ')
        with open(CONFIG_FILE, 'w') as config_file:
            json.dump({GPT4_KEY: gpt_4_key}, config_file)
        print('Configuration saved. Exiting...')
        exit()
    else:
        with open(CONFIG_FILE, 'r') as config_file:
            config = json.load(config_file)
        return config

def create_checksum(file_path):
    hash_md5 = hashlib.md5()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()

def process_file(file_path, openai_key):
    checksum_file = f'{file_path}.checksum'
    output_file = f'{file_path}.output'
    completed_file = f'{file_path}.completed'
    file_checksum = create_checksum(file_path)

    if os.path.exists(checksum_file):
        with open(checksum_file, 'r') as f:
            old_checksum = f.read().strip()

        if old_checksum == file_checksum:
            print(f'File {file_path} has not changed.')
            return

    print(f'Processing file: {file_path}')
    with open(checksum_file, 'w') as f:
        f.write(file_checksum)

    with open(file_path, 'r') as f:
        lines = f.readlines()

    prepared_prompt = ''
    output_file_name = None
    create_interface = False

    for line in lines:
        line = line.strip()
        if line.startswith('#include'):
            include_file = os.path.join(os.path.dirname(file_path), line.split('#include ')[1])
            with open(include_file, 'r') as f:
                prepared_prompt += f.read()
        elif line.startswith('#write-to'):
            output_file_name = os.path.join(os.path.dirname(file_path), line.split('#write-to ')[1])
        elif line.startswith('#create-interface'):
            create_interface = True
        else:
            prepared_prompt += line

    with open(completed_file, 'w') as f:
        f.write(prepared_prompt)

    result = call_gpt_4(openai_key, prepared_prompt)

    with open(output_file, 'w') as f:
        f.write(result)

    if output_file_name:
        post_process_output(result, output_file_name, create_interface)

def post_process_output(output, output_file_name, create_interface):
    matches = re.findall('```python(.*?)```', output, re.DOTALL)
    file_content = '\n'.join(matches)
    
    with open(output_file_name, 'w') as f:
        f.write(file_content)

    if create_interface:
        interface = extract_functions(file_content, output_file_name)
        with open(f"{output_file_name}.interface", 'w') as f:
            f.write(interface)

def walk_dir(dir_path, openai_key):
    for root, dirs, files in os.walk(dir_path):
        for file in files:
            if file.endswith('.prompt'):
                process_file(os.path.join(root, file), openai_key)

def main():
    config = read_config()
    openai_key = config.get(GPT4_KEY)

    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--directory", help="Directory to walk through", default='.')
    args = parser.parse_args()
    dir_path = args.directory

    walk_dir(dir_path, openai_key)

if __name__ == "__main__":
    main()
