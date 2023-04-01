# LGPL-3.0 License
# Copyright (c) 2023 KIT-IAI-ESA

from typing import Any


class ExtParameter:
    """
    An intermediate parameter
    """

    __forbidden_names = ["del"]

    def __init__(
        self,
        key: str,
        name: str,
        _type: str,
        default: Any,
        description: str = "",
        minimum: str = "",
        maximum: str = "",
    ) -> None:
        """
        Initialize the parameter

        :param key: Key of the parameter
        :type key: str
        :param name: Name of the parameter
        :type name: str
        :param _type: Type of the parameter
        :type _type: str
        :param default: Default value of the parameter
        :type default: Any
        :param description: Description of the parameter, defaults to ""
        :type description: str, optional
        """
        #: Key of the parameter
        self.key: str = key
        #: Name of the parameter
        self.name: str = name
        if name in self.__forbidden_names:
            self.name = "_" + name
        #: Type of the parameter
        self._type: str = _type
        #: Default value of the parameter
        self.default: Any = default
        #: Description of the parameter
        self.description: str = description
        self.minimum = minimum
        self.maximum = maximum

    @property
    def comp_type(self):
        """
        The type of the component
        """
        return self._type

    def set_type(self, _type: str) -> None:
        """
        Set the type of the parameter

        :param _type: Type of the parameter
        :type _type: str
        """
        self._type = _type

    def get_args(self) -> str:
        args = f"'{self.default}'"
        if self.minimum != "":
            args += f", minimum='{self.minimum}'"
        if self.maximum != "":
            args += f", maximum='{self.maximum}'"
        return args
