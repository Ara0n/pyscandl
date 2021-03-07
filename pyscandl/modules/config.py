import json
import os
import platform
from typing import Union, Dict, List



DEFAULT_CONFIG = {
    "autodl": {
        "downloadPath": f"{'%HOMEDRIVE%%HOMEPATH%' if platform.system() == 'Windows' else '$HOME'}/Documents/pyscandl/autodl",
        "downloadType": "pdf",
        "tiny": False,
        "quiet": False,
    },
    "manual": {
        "downloadPath": f"{'%HOMEDRIVE%%HOMEPATH%' if platform.system() == 'Windows' else '$HOME'}/Documents/pyscandl",
        "downloadType": "pdf",
        "tiny": False,
        "quiet": False,
    }

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

    def __getitem__(self, key: str) -> jsonType:
        """Defines a [] for getting elements from the config

        The key is given in a form category.subcategory.subsubcategory.etc.value
        for example ``"autodl.downloadPath"``
        
        :param key: the key for the value
        :type key: str
        :return: the configured value
        :rtype: jsonType
        """
        keys = key.split(".")
        val = self.internal_repr
        for i in keys:
            val = val[i]
        if "path" in key or "Path" in key:
            val = os.path.expandvars(val)
        return val


    def read(self):
        self.internal_repr = dict(DEFAULT_CONFIG)
        with open(self.path, 'r') as f:
            self.internal_repr.update(json.load(f))


    
    def write(self):
        with open(self.path, 'w') as f:
            json.dump(self.internal_repr, f)