# LGPL-3.0 License
# Copyright (c) 2023 KIT-IAI-ESA

from typing import Any
from pyapi_rts.api.parameters.parameter import Parameter


class StringParameter(Parameter[str]):
    """
    A parameter that contains a string
    """

    def __init__(self, value: str) -> None:
        if value is None:
            super().__init__("")
        elif not isinstance(value, str):
            raise TypeError("value is not a string")
        else:
            super().__init__(value)

    @Parameter.value.setter
    def value(self, value: Any) -> None:
        """
        Sets the value of the parameter

        :param value: The value to set
        :type value: str
        """
        self._value = str(value)

    @classmethod
    def _parse_str(cls, value: str) -> str:
        if value is None:
            return ""
        if not isinstance(value, str):
            raise TypeError
        if value.startswith("$"):
            raise ValueError
        return value

    def __str__(self) -> str:
        return self._value
