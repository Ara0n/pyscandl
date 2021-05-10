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
    The configuration object
    This handles loading the config, reloading it, and keeping it in memory to be accessed by the program
    """
    _path: str
    _internal_repr: dict

    def __init__(self, path: str):
        """Creates a Config object

        :param path: the path to the config file
        :type path: str
        """
        self._path = path
        if not os.path.exists(self._path):
            self._internal_repr = dict(DEFAULT_CONFIG)
            with open(self._path, 'w') as f:
                json.dump(self._internal_repr, f)
        else:
            self.load()

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
        val = self._internal_repr
        for i in keys:
            val = val[i]
        if "path" in key or "Path" in key:
            val = os.path.expandvars(val)
        return val

    def __enter__(self):
        retdurn self
    def __exit__(self):
        pass

    def load(self):
        """(Re)loads the configuration"""
        self._internal_repr = dict(DEFAULT_CONFIG)
        with open(self._path, 'r') as f:
            self._internal_repr.update(json.load(f))
