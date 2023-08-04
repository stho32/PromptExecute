
import os
import json

CONFIG_FILE = 'config.json'
GPT4_KEY = 'gpt_4_key'

def initialize_config():
    """
    Initialize the configuration file.
    If the config file does not exist, ask the user for the GPT-4 key and create the config file.
    If the config file exists, do nothing.
    """
    if not os.path.exists(CONFIG_FILE):
        gpt4_key = input('Please enter your GPT-4 key: ')
        config = {GPT4_KEY: gpt4_key}
        with open(CONFIG_FILE, 'w') as f:
            json.dump(config, f)
        print(f'Configuration file {CONFIG_FILE} has been created. Please restart the application.')
        exit()

def load_config():
    """
    Load the configuration file into a dictionary.
    Return the dictionary.
    """
    with open(CONFIG_FILE, 'r') as f:
        config = json.load(f)
    return config

def get_gpt4_key():
    """
    Retrieve the GPT-4 key from the configuration file.
    Return the GPT-4 key.
    """
    config = load_config()
    return config.get(GPT4_KEY)


from configuration import initialize_config, get_gpt4_key

# Initialize the configuration file
initialize_config()

# Get the GPT-4 key
gpt4_key = get_gpt4_key()
