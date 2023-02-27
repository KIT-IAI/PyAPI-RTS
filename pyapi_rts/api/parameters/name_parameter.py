# LGPL-3.0 License
# Copyright (c) 2023 KIT-IAI-ESA

from pyapi_rts.api.parameters.parameter import Parameter


class NameParameter(Parameter):
    """
    A parameter containing a string representing a name.
    """

    default = ""

    def __init__(self, key: str, value: str, from_str: bool = False) -> None:
        if (not isinstance(value, str)) and (not from_str and isinstance(value, str)):
            raise Exception("value is not a string")
        self._value: str
        super().__init__(key, value, from_str)

    def get_value(self) -> str:
        """
        Returns the value of the parameter.

        :return: The value of the parameter
        :rtype: str
        """
        return super().get_value()

    def set_value(self, value: str) -> bool:
        """
        Sets the value of the parameter.

        :param value: The value of the parameter
        :type value: str
        :return: Success of the operation
        :rtype: bool
        """
        super().set_value(value)
        return True

    def get_value_as_int(self) -> str:
        """
        Returns the value of the parameter as an integer.

        :return: The value of the parameter.
        :rtype: str
        """
        return -1  # Not possible.

    def set_str(self, value: str) -> bool:
        """
        Sets the value of the parameter from a string.

        :param value: The value of the parameter as a string
        :type value: str
        :return: Success of the operation
        :rtype: bool
        """
        if not isinstance(value, str) or value.startswith("$"):
            return False
        if isinstance(value, str):
            self._value = value
            return True
        return False

    def __str__(self) -> str:
        return self._value
