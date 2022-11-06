import os
import json
import os.path

data_path = 'D:/!GitClones/assistant_bot/data/'
file_name = 'config.json'

config = None

config_dict = {
    "token": "",
    "database": {
        "host": "127.0.0.1",
        "port": "5432",
        "database": "postgres",
        "user": "postgres",
        "password": ""
    },
    "onlinegdb": {
        "email": "",
        "password": ""
    }
}

class ConfigNode():
    def __init__(self, node: dict):
        for key, value in node.items():
            if (type(value) != dict):
                self.__setattr__(str(key), value)
            else:
                self.__setattr__(str(key), ConfigNode(value))

def load():
    global config
    if not os.path.exists(data_path + file_name):
        if not os.path.exists(data_path):
            print('Creating new data folder')
            os.makedirs(data_path)
        with open(data_path + file_name, 'w') as file:
            print('Creating new config.json')
            json.dump(config_dict, file, indent=4)
    with open(data_path + file_name, 'r') as file:
        print('Loading config.json')
        raw_config = json.load(file)
    config = ConfigNode(raw_config)

def reload():
    global config
    with open(data_path + file_name, 'r') as file:
        print('Loading config.json')
        raw_config = json.load(file)
    config = ConfigNode(raw_config)

load()