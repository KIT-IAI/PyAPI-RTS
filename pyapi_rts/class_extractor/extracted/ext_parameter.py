# LGPL-3.0 License
# Copyright (c) 2023 KIT-IAI-ESA

from typing import Any


class ExtParameter:
    """
    An intermediate parameter
    """

    __forbidden_names = ["del"]

    def __init__(
        self, key: str, name: str, _type: str, default: Any, description: str = ""
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

    def write(self) -> list[str]:
        """
        Write the parameter to a list of lines

        :return: list of lines
        :rtype: list[str]
        """
        return ["{0}:{1}:{2}:{3}".format(self.key, self.name, self._type, self.default)]

    @classmethod
    def read(cls, line: list[str]) -> "ExtParameter":
        """
        Read the parameter from a list of lines

        :param line: list of lines
        :type line: list[str]
        :return: Read parameter
        :rtype: ExtParameter
        """
        split = line[0].split(":")
        return ExtParameter(split[0], split[1], split[2], split[3])
