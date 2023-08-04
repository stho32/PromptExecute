import os
import sys
import hashlib
import json
from library.chatgpt import call_gpt_4

CONFIG_FILE = "config.json"

def get_config():
    # Check if config file exists
    if not os.path.isfile(CONFIG_FILE):
        # Ask user for GPT-4 key
        gpt4_key = input("Please enter your GPT-4 API key: ")
        # Write the key to the config file
        with open(CONFIG_FILE, 'w') as config_file:
            json.dump({"gpt_4_key": gpt4_key}, config_file)
        print(f"GPT-4 key saved in {CONFIG_FILE}. Please rerun the application.")
        sys.exit(0)
    
    # Read config file
    with open(CONFIG_FILE, 'r') as config_file:
        config = json.load(config_file)
    return config

def process_file(filepath, openaikey):
    # Check if checksum file exists
    checksum_file = filepath + ".checksum"
    new_checksum = hashlib.md5(open(filepath, 'rb').read()).hexdigest()

    if os.path.isfile(checksum_file):
        with open(checksum_file, 'r') as f:
            old_checksum = f.read().strip()
        if old_checksum == new_checksum:
            print(f"No changes detected in {filepath}. Skipping...")
            return
    print(f"Processing {filepath}...")
    
    # Prepare prompt
    preparedPrompt = []
    with open(filepath, 'r') as f:
        for line in f:
            if line.startswith("#include"):
                include_file = line.split("#include", 1)[1].strip()
                if os.path.isfile(include_file):
                    with open(include_file, 'r') as inc_f:
                        preparedPrompt.append(inc_f.read())
                else:
                    print(f"Warning: Included file {include_file} not found.")
            else:
                preparedPrompt.append(line)
    preparedPrompt = "\n".join(preparedPrompt)
    
    # Call GPT-4
    result = call_gpt_4(openaikey, preparedPrompt)
    
    # Write result to output file
    output_file = filepath + ".output"
    with open(output_file, 'w') as f:
        f.write(result)
    print(f"Output written to {output_file}.")
    
    # Update checksum
    with open(checksum_file, 'w') as f:
        f.write(new_checksum)
    print(f"Updated checksum in {checksum_file}.")

def walk_directory(directory, openaikey):
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith(".prompt"):
                filepath = os.path.join(root, file)
                process_file(filepath, openaikey)

def main():
    config = get_config()
    openaikey = config["gpt_4_key"]

    # Get directory from command line argument or use current directory
    directory = sys.argv[1] if len(sys.argv) > 1 else os.getcwd()
    print(f"Scanning directory: {directory}")

    walk_directory(directory, openaikey)

if __name__ == "__main__":
    main()