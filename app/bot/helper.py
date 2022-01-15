import json

def load_config_file(path):
    with open(path, 'r') as file:
        config = json.load(file)
        print('Config File Loaded!')
    return config

def clean_trade_dict(dct):
    """Clean Kucoin trade responce. Replace None and Boolean data types to save in SQL"""
    result = dct.copy()

    for key, value in dct.items():
        if value is None:
            value = ''
        elif value is False or value is True:    
            value = value*1
        result[key] = value
    return result