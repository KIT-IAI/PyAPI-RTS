# LGPL-3.0 License
# Copyright (c) 2023 KIT-IAI-ESA

from typing import Any
from pyapi_rts.api.parameters.parameter import Parameter


class ParameterCollection:
    """
    A collection of specific parameters with certain keys and types
    """

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
            return param.get_value()
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

    def set_value(self, key: str, value: Any) -> bool:
        """
        Tries to set parameter with given key to a value

        :param key: The key of the parameter to set
        :type key: str
        :param value: The value to set the parameter to
        :type value: Any
        :return: True if parameter was set, False if not
        :rtype: bool
        """
        param = self._dict.get(key)
        if param is not None:
            return param.set_value(value)
        return False

    def set_str(self, key: str, value: str) -> bool:
        """
        Tries to set parameter with given key to a value

        :param key: The key of the parameter to set
        :type key: str
        :param value: The string representation of the value to set the parameter to
        :type value: str
        :return: True if parameter was set, False if not
        :rtype: bool
        """
        param = self._dict.get(key)
        if param is not None:
            param.set_str(value)
            return True
        return False

    def _write_parameters(self) -> list[str]:
        """
        Returns all parameters as list

        :return: All parameters as list
        :rtype: list[str]
        """
        lines = []
        for key, param in self._dict.items():
            lines.append(f"{key}\t:{param}")
        return lines

    def _read_parameters(self, dictionary: dict[str, str]) -> None:
        """
        Reads the parameters from a dictionary

        :param dictionary: The dictionary to read the parameters from
        :type dictionary: dict[str, str]
        """
        for key, param in self._dict.items():
            param.set_str(dictionary.get(key))
