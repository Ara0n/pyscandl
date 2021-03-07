import json
import os
import platform
from typing import Union, Dict, List



DEFAULT_CONFIG = {
    "autodl": {
        "downloadPath": f"{'%HOMEDRIVE%%HOMEPATH%' if platform.system() == 'Windows' else '$HOME'}/Documents/Books",
        "downloadType": "pdf",
        "tiny": False,
    },
}

jsonType = Union[int, float, bool, str, dict, list]

class Config(object):
    """    
    """
    path: str
    internal_repr: dict

    def __init__(self, path: str):
        """Creates a Config object

        :param path: the path to the config file
        :type path: str
        """
        self.path = path
        self.internal_repr = {}

    def get(self, key: str) -> jsonType:
        """Gets a value from the config

        :param key: the key to the value
        :type key: str
        :return: the associated value
        :rtype: any
        """
        return self.internal_repr[key]
        

    def set(self, key: str, value: jsonType):
        """Set a value in the config

        :param key: the key to the value
        :type key: str
        :param value: the value to write
        :type value: any
        """
        self.internal_repr[key] = value

    def read(self):
        self.internal_repr = dict(DEFAULT_CONFIG)
        with open(self.path, 'r') as f:
            self.internal_repr.update(json.load(f))

    @staticmethod
    def _expandpath(path: str) -> str:
        pass

    
    def write(self):
        with open(self.path, 'w') as f:
            json.dump(self.internal_repr, f)