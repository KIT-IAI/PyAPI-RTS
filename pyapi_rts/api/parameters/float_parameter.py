# LGPL-3.0 License
# Copyright (c) 2023 KIT-IAI-ESA

from pyapi_rts.api.parameters.parameter import Parameter


class FloatParameter(Parameter[float]):
    """
    A parameter containing a floating point number.
    """

    def __init__(self, value: float, minimum: float = None, maximum: float = None) -> None:
        """
        Initializes the parameter.

        :param value: The value of the parameter
        :type value: float
        :raises Exception: If the value is not a float
        """
        if not isinstance(value, (float, int)):
            raise TypeError("value is not a floating point number")
        super().__init__(float(value))
        self._minimum = minimum
        self._maximum = maximum

    @classmethod
    def from_str(cls, value: str, minimum: str = None, maximum: str = None) -> "FloatParameter":
        _min = cls._parse_str(minimum) if minimum is not None else None
        _max = cls._parse_str(maximum) if maximum is not None else None
        return cls(cls._parse_str(value), _min, _max)

    @Parameter.value.setter
    def value(self, value: float) -> None:
        """
        Sets the value of the parameter.

        :param value: The value of the parameter
        :type value: float
        """
        if not isinstance(value, (int, float)):
            raise TypeError
        self._value = value

    @classmethod
    def _parse_str(cls, value: str) -> float:
        if not isinstance(value, str):
            raise TypeError
        if value.startswith("$"):
            raise ValueError
        return float(value)

    def __str__(self) -> str:
        return str(self._value)
