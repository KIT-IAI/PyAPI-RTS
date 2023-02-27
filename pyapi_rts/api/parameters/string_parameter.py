# LGPL-3.0 License
# Copyright (c) 2023 KIT-IAI-ESA

from pyapi_rts.api.parameters.parameter import Parameter


class StringParameter(Parameter):
    """
    A parameter that contains a string
    """

    default = ""

    def __init__(self, key: str, value: str, from_str: bool = False) -> None:
        self._value: str
        if value is None:
            super().__init__(key, StringParameter.default, from_str)
        elif not isinstance(value, str):
            raise Exception("value is not a string")
        else:
            super().__init__(key, value, from_str)

    def get_value(self) -> str:
        """
        Returns the value of the parameter

        :return: The value of the parameter
        :rtype: str
        """
        return super().get_value()

    def set_value(self, value: str) -> bool:
        """
        Sets the value of the parameter

        :param value: The value to set
        :type value: str
        :return: True if the value was set, False otherwise
        :rtype: bool
        """
        super().set_value(str(value))
        return True

    def get_value_as_int(self) -> int:
        """
        Returns the value of the parameter as an integer.

        :return: The value of the parameter.
        :rtype: int
        """
        if self._value.isdigit() or self._value.replace(".", "").isdigit():
            return int(self._value)
        return -1  # Not possible.

    def set_str(self, value: str) -> bool:
        """
        Sets the value of the parameter to the given string

        :param value: The value to set
        :type value: str
        :return: True if the value was set, False otherwise
        :rtype: bool
        """
        if not isinstance(value, str) or value.startswith("$"):
            return False
        if isinstance(value, str):
            self._value = value
        return True

    def __str__(self) -> str:
        return self._value
