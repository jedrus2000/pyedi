from typing import Dict, List


config: "PediConfiguration" = None


class PediConfiguration:
    USERSYSIMPORTPATH = "usersysimportpath"
    DIRECTORIES = "directories"
    USERSYSABS = "usersysabs"
    NOT_IMPORT = "not_import"

    def __init__(self):
        self._config: Dict = dict()
        pass

    def _default_dict(self):
        return {
            "settings": {
                "max_number_errors": 10,
                "debug": False,
                "readrecorddebug": False,
                "maxfilesizeincoming": 5_000_000,
            }
        }

    # @property
    def get(self, keys: List[str]):
        return ""

    def add(self, keys: List[str], value: str):
        return ""
