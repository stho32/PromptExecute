import os
import json

CONFIG_FILE = 'config.json'
GPT_4_KEY = 'gpt_4_key'

def initialize_config():
    """
    Initialize the configuration file.
    If the config.json file does not exist, ask the user for the GPT-4 key, write it into the config.json file and exit the application.
    If the config.json file exists, read the configuration into variables.
    """
    if not os.path.isfile(CONFIG_FILE):
        gpt_4_key = input('Please enter your GPT-4 key: ')
        with open(CONFIG_FILE, 'w') as file:
            json.dump({GPT_4_KEY: gpt_4_key}, file)
        print('Configuration saved. Please restart the application.')
        exit(0)
    else:
        with open(CONFIG_FILE, 'r') as file:
            config = json.load(file)
        return config

def get_gpt_4_key():
    """
    Retrieve the GPT-4 API key from the configuration file.
    """
    config = initialize_config()
    return config[GPT_4_KEY]
