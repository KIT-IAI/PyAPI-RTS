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
            if value is not None and not (isinstance(value, str) and value.startswith("$")):
                raise TypeError("value is not a floating point number")
            super().__init__(value)
        else:
            super().__init__(float(value))
        self._minimum = minimum
        self._maximum = maximum

    @classmethod
    def from_str(cls, value: str, minimum: str = None, maximum: str = None) -> "FloatParameter":
        _min = cls._parse_str(minimum) if minimum is not None else None
        _max = cls._parse_str(maximum) if maximum is not None else None
        return cls(cls._parse_str(value, True), _min, _max)

    @Parameter.value.setter
    def value(self, value: float) -> None:
        """
        Sets the value of the parameter.

        :param value: The value of the parameter
        :type value: float
        """
        if not isinstance(value, (int, float)):
            raise TypeError
        if self._minimum is not None and value < self._minimum:
            raise ValueError("value is too small")
        if self._maximum is not None and value > self._maximum:
            raise ValueError("value is too big")
        self._value = value

    @property
    def minimum(self) -> float | None:
        return self._minimum

    @property
    def maximum(self) -> float | None:
        return self._maximum

    def set_within_limits(self, value: float) -> float:
        """
        Sets the value of the parameter within the parameter limits. Returns the value that was set.

        :param value: The value of the parameter
        :type value: float
        :return: The value the parameter was set to
        :rtype: float
        """
        if not isinstance(value, (int, float)):
            raise TypeError
        if self._minimum is not None and value < self._minimum:
            self._value = self._minimum
        elif self._maximum is not None and value > self._maximum:
            self._value = self._maximum
        else:
            self._value = value
        return self._value

    @classmethod
    def _parse_str(cls, value: str, is_init: bool = False) -> float | str:
        if not isinstance(value, str):
            raise TypeError
        if value.startswith("$"):
            if not is_init:
                raise ValueError("Implicit setting of draft variables is forbidden!")
            else:
                return value
        if value in ('""', "None"):
            return None
        return float(value)

    def __str__(self) -> str:
        return str(self._value)
