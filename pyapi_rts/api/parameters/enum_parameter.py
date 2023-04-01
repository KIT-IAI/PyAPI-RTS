# LGPL-3.0 License
# Copyright (c) 2023 KIT-IAI-ESA

from enum import Enum
from typing import TypeVar, Generic
from pyapi_rts.api.parameters.parameter import Parameter

S = TypeVar('S', bound=Enum)

class EnumParameter(Parameter[S], Generic[S]):
    """
    An abstract parameter containing a generic Enum.
    """

    def __init__(self, value: S) -> None:
        """
        A parameter containing an Enum.

        :param value: The value of the parameter
        :type value: S
        :raises TypeError: If the value is not an Enum
        """
        if not isinstance(value, Enum):
            raise TypeError("value is not an Enum")

        super().__init__(value)

    @property
    def index(self) -> int:
        """Get the value of the parameter as the index in the Enum.

        :return: The index of the value
        :rtype: int
        """
        return list(type(self._value)).index(self._value)

    def __str__(self) -> str:
        return str(self._value.value)
