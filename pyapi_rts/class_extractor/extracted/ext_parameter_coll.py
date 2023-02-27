# LGPL-3.0 License
# Copyright (c) 2023 KIT-IAI-ESA

from typing import Any

from .ext_parameter import ExtParameter
from ..utils import valid_file_name


class ExtParameterColl:
    """
    A named collection of parameters.
    """

    def __init__(self, name: str) -> None:
        """
        Initializes the ExtParameterColl object.

        :param name: The name of the collection.
        :type name: str
        """
        #: The name of the collection.
        self.name = name
        #: The parameters in the collection.
        self.parameters: list[ExtParameter] = []

    def write(self) -> list[str]:
        """
        Writes the ExtParameterColl object to a list of strings.

        :return: Lines of strings.
        :rtype: list[str]
        """
        lst = []
        lst.append("COLL")
        lst.append(self.name)
        for param in self.parameters:
            lst += param.write()
        lst.append("END")
        return lst

    @classmethod
    def read(self, lst: list[str]) -> Any:
        """
        Reads an ExtParameterColl object from a list of strings.

        :param lst: The list of strings.
        :type lst: list[str]
        :return: The ExtParameterColl object.
        :rtype: ExtParameterColl
        """
        epc = ExtParameterColl(lst[1])
        for line in lst[2:-1]:
            epc.parameters.append(ExtParameter.read([line]))
        return epc

    @property
    def type_name(self):
        """
        The type name of the ExtParameterColl object.

        :return: The type name.
        :rtype: str
        """
        return (
            valid_file_name(self.name.title()) + "ParameterCollection"
        )

    def __eq__(self, __o: object) -> bool:
        return isinstance(__o, ExtParameterColl) and set(
            map((lambda p: p.key), self.parameters)
        ) == set(map((lambda p: p.key), __o.parameters))
