# LGPL-3.0 License
# Copyright (c) 2023 KIT-IAI-ESA

from abc import ABC, abstractmethod
from typing import TypeVar, Generic

T = TypeVar('T')

class Parameter(Generic[T], ABC):
    """
    Base class for all parameters
    """

    def __init__(self, value: T) -> None:
        self._value: T = value
        self._default: T = value

    @classmethod
    def from_str(cls, value: str) -> "Parameter":
        return cls(cls._parse_str(value, True))

    @property
    def default(self) -> T:
        """
        Get the default value of the parameter

        :return: The default value of the parameter
        :rtype: T
        """
        return self._default

    @property
    def value(self) -> T:
        """
        Get the value of the parameter

        :return: The value of the parameter
        :rtype: T
        """
        return self._value

    @value.setter
    @abstractmethod
    def value(self, value: T) -> None:
        """
        Set the value of the parameter

        :param value: The value to set
        :type value: T
        """
        ...

    def reset(self) -> None:
        """
        Reset the parameter to its default value.
        """
        self._value = self._default

    def set_str(self, value: str, is_init: bool = False) -> None:
        """
        Set the value of the parameter from a string

        :param value: The value to set
        :type value: str
        :param is_init: True if the method is used for initialization (e.g. by reading a file).
        :type is_init: bool
        """
        self._value = self._parse_str(value, is_init)

    def set_draft_var(self, name: str) -> None:
        """
        Set the value of the parameter to the name of a draft variable.

        :param name: The name of the draft var; starting with '$'.
        :type name: str
        """
        if not isinstance(name, str):
            raise TypeError("Draft var name must be of type str.")
        if not name.startswith("$"):
            raise ValueError("Draft var name must start with '$'.")
        self._value = name

    @classmethod
    @abstractmethod
    def _parse_str(cls, value: str, is_init: bool = False) -> T:
        ...