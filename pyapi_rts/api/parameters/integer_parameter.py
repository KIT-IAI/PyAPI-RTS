# LGPL-3.0 License
# Copyright (c) 2023 KIT-IAI-ESA

from pyapi_rts.api.parameters.parameter import Parameter


class IntegerParameter(Parameter):
    """
    A parameter containing an integer number.
    """

    default = 0

    def __init__(self, key: str, value: int, from_str: bool = False) -> None:
        """
        A parameter containing an integer number.

        :param key: The key of the parameter
        :type key: str
        :param value: The value of the parameter
        :type value: int
        :raises Exception: If the value is not an integer
        """
        if (not isinstance(value, int)) and (not from_str and isinstance(value, str)):
            raise Exception("value is not an integer")

        super().__init__(key, value, from_str)
        self._value: int

    def get_value(self) -> int:
        """
        Returns the value of the parameter.

        :return: The value of the parameter
        :rtype: int
        """
        return super().get_value()

    def get_value_as_int(self) -> int:
        """
        Returns the value of the parameter as an integer.

        :return: The value of the parameter.
        :rtype: int
        """
        return self._value

    def set_value(self, value: int) -> bool:
        """
        Sets the value of the parameter.

        :param value: The value of the parameter
        :type value: int
        :return: Success of the operation
        :rtype: bool
        """
        if not isinstance(value, int):
            return False
        super().set_value(value)
        return True

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
        try:
            self._value = int(value)
        except ValueError:
            return False
        if str(int(value)) != value:
            return False
        self._value = int(value)
        return True

    def __str__(self) -> str:
        return str(self._value)
