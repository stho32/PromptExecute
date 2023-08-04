import os
import json
import hashlib
import requests

# Configuration
def load_config():
    config_path = 'config.json'
    if not os.path.exists(config_path):
        api_key = input("Enter your GPT-4 key:")
        with open(config_path, 'w') as f:
            json.dump({'gpt_4_key': api_key}, f)
        print("Config saved. Please rerun the program.")
        exit()
    else:
        with open(config_path, 'r') as f:
            config = json.load(f)
        return config['gpt_4_key']

# Checksum calculation
def get_checksum(file_path):
    with open(file_path, 'rb') as f:
        data = f.read()
    return hashlib.md5(data).hexdigest()

# Process each file
def process_file(api_key, file_path):
    prompt = []
    with open(file_path, 'r') as f:
        for line in f.readlines():
            if line.startswith('#include'):
                with open(line.split('#include')[1].strip(), 'r') as inc_file:
                    prompt.append(inc_file.read())
            else:
                prompt.append(line)

    # Call GPT-4 API
    result = call_gpt_4(api_key, ''.join(prompt))

    # Save the output
    with open(f"{file_path}.output", 'w') as f:
        f.write(result)

# Function to call GPT-4 API
def call_gpt_4(api_key, prompt):
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }
    data = {
        'prompt': prompt,
        'max_tokens': 100
    }
    response = requests.post('https://api.openai.com/v4/engines/davinci-codex/completions', headers=headers, data=json.dumps(data))
    response.raise_for_status()
    return response.json()['choices'][0]['text']

def main():
    api_key = load_config()

    for root, dirs, files in os.walk('.'):
        for file in files:
            if file.endswith('.prompt'):
                file_path = os.path.join(root, file)
                checksum_file = f"{file_path}.checksum"
                new_checksum = get_checksum(file_path)
                old_checksum = ''

                if os.path.exists(checksum_file):
                    with open(checksum_file, 'r') as f:
                        old_checksum = f.read()

                if new_checksum != old_checksum:
                    with open(checksum_file, 'w') as f:
                        f.write(new_checksum)
                    process_file(api_key, file_path)

if __name__ == "__main__":
    main()
