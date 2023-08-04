import os
import sys
import json
import hashlib
from library.chatgpt import call_gpt_4

CONFIG_FILE = 'config.json'
GPT_KEY = 'gpt_4_key'
PROMPT_EXT = '.prompt'
CHECKSUM_EXT = '.checksum'
COMPLETED_EXT = '.completed'
OUTPUT_EXT = '.output'

def get_config():
    if not os.path.exists(CONFIG_FILE):
        gpt_key = input("Please enter your GPT-4 key: ")
        with open(CONFIG_FILE, 'w') as f:
            json.dump({GPT_KEY: gpt_key}, f)
        print(f"Configuration saved in {CONFIG_FILE}. Please restart the application.")
        sys.exit(0)

    with open(CONFIG_FILE, 'r') as f:
        return json.load(f)

def compute_checksum(file_path):
    hasher = hashlib.md5()
    with open(file_path, 'rb') as f:
        buf = f.read()
        hasher.update(buf)
    return hasher.hexdigest()

def process_file(file_path, openaikey):
    print(f"Processing file: {file_path}")
    checksum_file = file_path + CHECKSUM_EXT
    completed_file = file_path + COMPLETED_EXT
    old_checksum = ''
    if os.path.exists(checksum_file):
        with open(checksum_file, 'r') as f:
            old_checksum = f.read().strip()

    new_checksum = compute_checksum(file_path)
    if old_checksum != new_checksum:
        with open(checksum_file, 'w') as f:
            f.write(new_checksum)

        preparedPrompt, outputFileName = prepare_prompt(file_path)
        with open(completed_file, 'w') as f:
            f.write('\n'.join(preparedPrompt))

        output = call_gpt_4(openaikey, '\n'.join(preparedPrompt))
        with open(file_path + OUTPUT_EXT, 'w') as f:
            f.write(output)

        if outputFileName:
            post_process(output, outputFileName)

def prepare_prompt(file_path):
    preparedPrompt = []
    outputFileName = None
    with open(file_path, 'r') as f:
        for line in f.readlines():
            if line.startswith('#include'):
                include_file = os.path.join(os.path.dirname(file_path), line.split('#include')[1].strip())
                with open(include_file, 'r') as inc_f:
                    preparedPrompt.extend(inc_f.readlines())
            elif line.startswith('#write-to'):
                outputFileName = os.path.join(os.path.dirname(file_path), line.split('#write-to')[1].strip())
            else:
                preparedPrompt.append(line.strip())
    return preparedPrompt, outputFileName

def post_process(output, outputFileName):
    print(f"Post-processing output to: {outputFileName}")
    content = output.split('```')[1]
    with open(outputFileName, 'w') as f:
        f.write(content)

def main():
    config = get_config()
    openaikey = config.get(GPT_KEY, '')
    if not openaikey:
        print(f"No {GPT_KEY} found in {CONFIG_FILE}. Please add it and restart the application.")
        sys.exit(0)

    directory = sys.argv[1] if len(sys.argv) > 1 else os.getcwd()
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith(PROMPT_EXT):
                process_file(os.path.join(root, file), openaikey)

if __name__ == "__main__":
    main()
