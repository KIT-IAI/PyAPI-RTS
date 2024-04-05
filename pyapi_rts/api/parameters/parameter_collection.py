# LGPL-3.0 License
# Copyright (c) 2023 KIT-IAI-ESA

from typing import Any
from pyapi_rts.api.parameters.parameter import Parameter


class ParameterCollection:
    """A collection of specific parameters with certain keys and types"""

    def __init__(self) -> None:
        self._dict: dict[str, Parameter] = {}

    def as_dict(self) -> dict[str, Parameter]:
        return self._dict

    def get_value(self, key: str) -> Any | None:
        """
        Returns the value of the parameter with the given key.
        """
        param = self._dict.get(key)
        if param is not None:
            return param.value
        return None

    def has_key(self, key: str) -> bool:
        """
        Checks if any parameter in collection has a given key

        :param key: The key to check for
        :type key: str
        :return: True if any parameter in collection has a given key
        :rtype: bool
        """
        return key in self._dict

    def set_value(self, key: str, value: Any) -> None:
        """
        Tries to set parameter with given key to a value

        :param key: The key of the parameter to set
        :type key: str
        :param value: The value to set the parameter to
        :type value: Any
        """
        param = self._dict.get(key)
        if param is not None:
            param.value = value
        else:
            raise KeyError

    def write_parameters(self) -> list[str]:
        """
        Returns all parameters as list

        :return: All parameters as list
        :rtype: list[str]
        """
        lines = []
        for key, param in self._dict.items():
            lines.append(f"{key}\t:{param}")
        return lines

    def read_parameters(self, dictionary: dict[str, str]) -> None:
        """
        Reads the parameters from a dictionary

        :param dictionary: The dictionary to read the parameters from
        :type dictionary: dict[str, str]
        """
        for key, param in self._dict.items():
            param.set_str(dictionary.get(key), is_init=True)
