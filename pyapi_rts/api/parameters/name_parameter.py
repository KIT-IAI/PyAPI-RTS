# LGPL-3.0 License
# Copyright (c) 2023 KIT-IAI-ESA

from pyapi_rts.api.parameters.parameter import Parameter


class NameParameter(Parameter[str]):
    """
    A parameter containing a string representing a name.
    """

    def __init__(self, value: str) -> None:
        if (not isinstance(value, str)):
            raise TypeError("value is not a string")
        super().__init__(value)

    @Parameter.value.setter
    def value(self, value: str) -> bool:
        """
        Sets the value of the parameter.

        :param value: The value of the parameter
        :type value: str
        :return: Success of the operation
        :rtype: bool
        """
        if not isinstance(value, str):
            raise TypeError
        self._value = value

    @classmethod
    def _parse_str(cls, value: str, is_init: bool = False) -> str:
        if not isinstance(value, str):
            raise TypeError
        if not is_init and value.startswith("$"):
            raise ValueError("Implicit setting of draft variables is forbidden!")
        return value

    def __str__(self) -> str:
        return self._value
