# LGPL-3.0 License
# Copyright (c) 2023 KIT-IAI-ESA

from pyapi_rts.api.parameters.parameter import Parameter


class HexParameter(Parameter[int]):
    """
    A parameter containing an integer number but works with hex strings.
    """

    def __init__(self, value: str, minimum: str | None = None, maximum: str | None = None) -> None:
        """
        A parameter containing an integer number.

        :param value: The value of the parameter
        :type value: int
        :raises Exception: If the value is not an integer
        """
        if not isinstance(value, str):
            raise TypeError("value is not a hex string")
        int_value = self._parse_str(value, True)
        super().__init__(int_value)
        if minimum == 'None':
            int_minimum = None
        else:
            int_minimum = self._parse_str(minimum, True)
        if maximum == 'None':
            int_maximum = None
        else:
            int_maximum = self._parse_str(maximum, True)
        self._minimum = int_minimum
        self._maximum = int_maximum

    @classmethod
    def from_str(
        cls, value: str, minimum: str | None = None, maximum: str | None = None
    ) -> "HexParameter":
        _min = cls._parse_str(minimum) if minimum is not None else None
        _max = cls._parse_str(maximum) if maximum is not None else None
        return cls(cls._parse_str(value, True), _min, _max)

    @Parameter.value.setter  # type: ignore
    def value(self, value: str) -> None:
        """
        Sets the value of the parameter.

        :param value: The value of the parameter
        :type value: str
        """
        if not isinstance(value, str):
            raise TypeError
        int_value = int(f'0x{value}')
        if self._minimum is not None and int_value < self._minimum:
            raise ValueError("value is too small")
        if self._maximum is not None and int_value > self._maximum:
            raise ValueError("value is too big")
        self._value = int_value

    @property
    def minimum(self) -> int | None:
        return self._minimum

    @property
    def maximum(self) -> int | None:
        return self._maximum

    def set_within_limits(self, value: str) -> int:
        """
        Sets the value of the parameter within the parameter limits. Returns the value that was set.

        :param value: The value of the parameter
        :type value: str
        :return: The value the parameter was set to
        :rtype: int
        """
        if not isinstance(value, str):
            raise TypeError
        int_value = int(f'0x{value}')
        if self._minimum is not None and int_value < self._minimum:
            self._value = self._minimum
        elif self._maximum is not None and int_value > self._maximum:
            self._value = self._maximum
        else:
            self._value = int_value
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
        int_val = int(f'0x{value}')
        return int_val

    def __str__(self) -> str:
        return hex(self._value)
