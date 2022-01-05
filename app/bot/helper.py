import json

def load_config_file(path):
    with open(path, 'r') as file:
        config = json.load(file)
        print('Config File Loaded!')
    return config