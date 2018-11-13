from itertools import chain
import os
from typing import Dict, List


class PyEdiConfig:
    USERSYSIMPORTPATH = "usersysimportpath"
    DIRECTORIES = "directories"
    USERSYSABS = "usersysabs"
    NOT_IMPORT = "not_import"
    BOTSPATH = "botspath"
    USERSYS = "usersys"

    def __init__(self):
        self._config: Dict = dict()
        self.config = self._default_dict()

    @property
    def config(self):
        return self._config

    @config.setter
    def config(self, value):
        self._config = dict(chain(self._config.items(), value.items()))  # override old _config with calue
        self._update_config_paths()

    def _default_dict(self):
        return {
            "settings": {
                "max_number_errors": 10,
                "debug": False,
                "readrecorddebug": False,
                "maxfilesizeincoming": 5_000_000,
                "get_checklevel": 1,
            },
            self.DIRECTORIES: {
                self.BOTSPATH: None,  # 'directories','botspath': absolute path for bots directory
                "config": "",
                "data": "",  # 'directories','config': absolute path for config directory
                self.USERSYS: "usersys",
                self.USERSYSIMPORTPATH: None,
            },
            self.NOT_IMPORT: set()
        }

    def _update_config_paths(self):
        self._config[self.DIRECTORIES][self.BOTSPATH] = os.path.abspath(os.path.dirname(__file__))
        usersys = self._config[self.DIRECTORIES][self.USERSYS]
        self._config[self.DIRECTORIES][self.USERSYSIMPORTPATH] = os.path.normpath(usersys).replace(os.sep, '.')
        self._config[self.DIRECTORIES][self.USERSYSABS] = os.path.abspath(self._config[self.DIRECTORIES][self.USERSYSIMPORTPATH])

    def _get_last_key_value_in_chain(self, keys: List[str]):
        key = None
        v = self._config
        for key in keys:
            v = v[key]
            if not isinstance(v, dict):
                break
        return key, v

    def get(self, keys: List[str]):
        '''
        get value from config

        :param keys:
        :return:
        '''
        _, v = self._get_last_key_value_in_chain(keys)
        return v

    def set(self, keys: List[str], value):
        param = self._config
        *loopkeys, last_key = keys
        for key in loopkeys:
            param = param[key]
        param[last_key] = value

    def add(self, keys: List[str], value: str):
        '''
        adds value to param (set or list) in config

        :param keys:
        :param value:
        :return:
        '''
        _, v = self._get_last_key_value_in_chain(keys)
        if isinstance(v, list):
            v.append(value)
        elif isinstance(v, set):
            v.add(v)
        else:
            raise NotImplemented(f"Adding value to config property type: {type(v)} ")


config: PyEdiConfig = PyEdiConfig()
