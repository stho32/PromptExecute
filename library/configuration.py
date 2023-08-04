import os
import json

CONFIG_FILE = 'config.json'
GPT_4_KEY_FIELD = 'gpt_4_key'

def initialize_config():
    """
    Initialize the config.json file by asking the user for a GPT-4 key.
    If the file already exists, it is not modified.
    """
    if not os.path.exists(CONFIG_FILE):
        gpt_4_key = input("Please enter your GPT-4 API Key: ")
        config = {GPT_4_KEY_FIELD: gpt_4_key}
        with open(CONFIG_FILE, 'w') as f:
            json.dump(config, f)
        print(f"Configuration saved in {CONFIG_FILE}. Please restart the application.")
        exit()

def load_config():
    """
    Load the configuration from the config.json file into a dictionary.
    """
    with open(CONFIG_FILE, 'r') as f:
        config = json.load(f)
    return config

def get_gpt_4_key():
    """
    Retrieve the GPT-4 API Key from the config.json file.
    """
    config = load_config()
    return config.get(GPT_4_KEY_FIELD)
