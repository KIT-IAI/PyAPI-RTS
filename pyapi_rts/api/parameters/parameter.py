# LGPL-3.0 License
# Copyright (c) 2023 KIT-IAI-ESA

from typing import Any


class Parameter:
    """
    Base class for all parameters
    """

    #: Default value for the parameter
    default: Any = None

    def __init__(self, key: str, value: Any, from_str: bool = False) -> None:
        #: The key of the parameter
        self.key: str = key
        #: The value of the parameter
        self._value: Any = None
        # Whether the value should be set from a string
        if from_str:
            self.set_str(value)
        else:
            self._value = value

    def get_value(self) -> Any:
        """
        Get the value of the parameter

        :return: The value of the parameter
        :rtype: Any
        """
        return self._value

    def get_value_as_int(self) -> int:
        """
        Get the value of the parameter as an integer

        :return: The value of the parameter as an integer
        :rtype: int
        """
        raise NotImplementedError("Not implemented. Use get_value()")

    def set_value(self, value: Any) -> bool:
        """
        Set the value of the parameter

        :param value: The value to set
        :type value: Any
        :return: Success of the operation
        :rtype: bool
        """
        self._value = value
        return True

    def set_str(self, value: str) -> bool:
        """
        Set the value of the parameter from a string

        :param value: The value to set
        :type value: str
        :return: Success of the operation
        :rtype: bool
        """
        return False

    def __str__(self) -> str:
        raise Exception("Abstract class, don't call")
