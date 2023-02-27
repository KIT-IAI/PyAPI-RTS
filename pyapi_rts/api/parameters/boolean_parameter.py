# LGPL-3.0 License
# Copyright (c) 2023 KIT-IAI-ESA

from pyapi_rts.api.parameters.parameter import Parameter


class BooleanParameter(Parameter):
    """
    A boolean parameter
    """

    def __init__(self, key: str, value: bool, from_str: bool = False) -> None:
        if bool(value) != value and (not from_str and isinstance(value, str)):
            raise Exception("value is not a boolean")
        super().__init__(key, value, from_str)
        self._value: bool

    def get_value(self) -> bool:
        """
        Get the value of the parameter

        :return: The value of the parameter
        :rtype: bool
        """
        return super().get_value()

    def set_value(self, value: bool) -> bool:
        """
        Set the value of the parameter

        :param value: The value to set
        :type value: bool
        :return: Success of the operation
        :rtype: bool
        """
        if not isinstance(value, bool):
            return False
        super().set_value(value)
        return True

    def set_str(self, value: str) -> bool:
        """
        Set the value of the parameter from a string

        :param value: The value to set
        :type value: str
        :return: Success of the operation
        :rtype: bool
        """
        if not isinstance(value, str) or value.startswith("$"):
            return False
        try:
            self._value = bool(value)
        except ValueError:
            return False
        return True

    def __str__(self) -> str:
        return str(self._value)
