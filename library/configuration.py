import json
import os

CONFIG_FILE = "config.json"
GPT_4_KEY = "gpt_4_key"

def initialize_config():
    """
    This function checks if a configuration file already exists. 
    If not, it prompts the user to enter a GPT-4 key and saves this key in a new configuration file. 
    If the file already exists, no action is taken.
    """
    if not os.path.exists(CONFIG_FILE):
        gpt_4_key = input("Please enter your GPT-4 key: ")
        with open(CONFIG_FILE, 'w') as f:
            json.dump({GPT_4_KEY: gpt_4_key}, f)
        print("Configuration file created. Please restart the application.")
        exit()

def load_config():
    """
    This function reads the configuration file and returns its content as a dictionary.
    """
    with open(CONFIG_FILE, 'r') as f:
        config = json.load(f)
    return config

def get_gpt4_key():
    """
    This function retrieves the GPT-4 key from the configuration file. 
    It uses the load_config method to read the file and returns the key as a string.
    """
    config = load_config()
    return config[GPT_4_KEY]