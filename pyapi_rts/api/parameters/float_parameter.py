# LGPL-3.0 License
# Copyright (c) 2023 KIT-IAI-ESA

from pyapi_rts.api.parameters.parameter import Parameter


class FloatParameter(Parameter):
    """
    A parameter containing a floating point number.
    """

    default = 0.0

    def __init__(self, key: str, value: float, from_str: bool = False) -> None:
        """
        Initializes the parameter.

        :param key: The key of the parameter
        :type key: str
        :param value: The value of the parameter
        :type value: float
        :raises Exception: If the value is not a float
        """
        if (not from_str and isinstance(value, str)) and float(value) != value:
            raise Exception("value is not a floating point number")
        super().__init__(key, value, from_str)
        self._value: float

    def get_value(self) -> float:
        """
        Returns the value of the parameter.

        :return: The value of the parameter
        :rtype: float
        """
        return super().get_value()

    def set_value(self, value: float) -> bool:
        """
        Sets the value of the parameter.

        :param value: The value of the parameter
        :type value: float
        :return: Success of the operation
        :rtype: bool
        """
        try:
            if float(value) != value:
                return False
        except ValueError as _:
            return False

        super().set_value(value)
        return True

    def get_value_as_int(self) -> int:
        return int(self._value)

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
            self._value = float(value)
        except TypeError:
            return False
        except ValueError:
            return False
        return True

    def __str__(self) -> str:
        return str(self._value)
