import os
import json

CONFIG_FILE = 'config.json'
GPT4_KEY = 'gpt_4_key'

def initialize_config():
    """
    Checks if a configuration file already exists. If not, it prompts the user to enter a GPT-4 key and saves this key in a new configuration file.
    If the file already exists, no action is taken.
    """
    if not os.path.exists(CONFIG_FILE):
        gpt4_key = input("Please enter your GPT-4 key: ")
        with open(CONFIG_FILE, 'w') as config_file:
            json.dump({GPT4_KEY: gpt4_key}, config_file)
        print(f"Configuration saved in {CONFIG_FILE}. Please restart the application.")
        exit()

def load_config():
    """
    Reads the configuration file and returns its content as a dictionary.
    """
    with open(CONFIG_FILE, 'r') as config_file:
        config = json.load(config_file)
    return config

def get_gpt4_key():
    """
    Retrieves the GPT-4 key from the configuration file. It uses the load_config() method to read the file and returns the key as a string.
    """
    config = load_config()
    return config[GPT4_KEY]
