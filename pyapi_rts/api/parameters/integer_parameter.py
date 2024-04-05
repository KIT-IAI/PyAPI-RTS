# LGPL-3.0 License
# Copyright (c) 2023 KIT-IAI-ESA

from pyapi_rts.api.parameters.parameter import Parameter


class IntegerParameter(Parameter[int]):
    """
    A parameter containing an integer number.
    """

    def __init__(self, value: int, minimum: int | None = None, maximum: int | None = None) -> None:
        """
        A parameter containing an integer number.

        :param value: The value of the parameter
        :type value: int
        :raises Exception: If the value is not an integer
        """
        if not isinstance(value, int):
            raise TypeError("value is not an integer")
        super().__init__(value)
        self._minimum = minimum
        self._maximum = maximum

    @classmethod
    def from_str(
        cls, value: str, minimum: str | None = None, maximum: str | None = None
    ) -> "IntegerParameter":
        _min = cls._parse_str(minimum) if minimum is not None else None
        _max = cls._parse_str(maximum) if maximum is not None else None
        return cls(cls._parse_str(value, True), _min, _max)

    @Parameter.value.setter  # type: ignore
    def value(self, value: int) -> None:
        """
        Sets the value of the parameter.

        :param value: The value of the parameter
        :type value: int
        """
        if not isinstance(value, int):
            raise TypeError
        if self._minimum is not None and value < self._minimum:
            raise ValueError("value is too small")
        if self._maximum is not None and value > self._maximum:
            raise ValueError("value is too big")
        self._value = value

    @property
    def minimum(self) -> int | None:
        return self._minimum

    @property
    def maximum(self) -> int | None:
        return self._maximum

    def set_within_limits(self, value: int) -> int:
        """
        Sets the value of the parameter within the parameter limits. Returns the value that was set.

        :param value: The value of the parameter
        :type value: int
        :return: The value the parameter was set to
        :rtype: int
        """
        if not isinstance(value, int):
            raise TypeError
        if self._minimum is not None and value < self._minimum:
            self._value = self._minimum
        elif self._maximum is not None and value > self._maximum:
            self._value = self._maximum
        else:
            self._value = value
        return self._value

    @classmethod
    def _parse_str(cls, value: str, is_init: bool = False) -> int | str:
        if not isinstance(value, str):
            raise TypeError
        if value.startswith("$"):
            if not is_init:
                raise ValueError("Implicit setting of draft variables is forbidden!")
            else:
                return value
        flt_val = float(value)  # for cases like 1e6
        int_val = int(flt_val)
        if int_val != flt_val:
            raise ValueError("Value is not an integer number")
        return int_val

    def __str__(self) -> str:
        return str(self._value)
