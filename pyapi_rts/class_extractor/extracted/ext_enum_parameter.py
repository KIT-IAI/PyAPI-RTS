# LGPL-3.0 License
# Copyright (c) 2023 KIT-IAI-ESA


class ExtEnumParameter:
    """
    A parameter that contains an enumeration
    """

    def __init__(self, name: str) -> None:
        """
        Initializes the parameter

        :param name: Name of the parameter
        :type name: str
        """
        #: Available options for the value of the parameter
        self.options: list[str] = []
        #: Name of the enum parameter
        self.__name: str = name
        #: Type of the parameter
        self._type = f"{self.__name.title()}EnumParameter".format()

    @property
    def enum_type(self) -> str:
        """
        The type of the parameter

        :return: Type of the parameter
        :rtype: str
        """
        return self._type

    def write(self) -> list[str]:
        """
        Writes the parameter to a list of lines

        :return: list of lines
        :rtype: list[str]
        """
        lst = []
        lst.append("ENUM")
        lst.append(self.__name)
        for opt in self.options:
            lst.append(opt)
        lst.append("END")
        return lst

    @classmethod
    def read(cls, lst: list[str]) -> "ExtEnumParameter":
        """
        Reads the parameter from a list of lines

        :param lst: list of lines
        :type lst: list[str]
        :return: Read EnumParameter
        :rtype: ExtEnumParameter
        """
        ext_enum = ExtEnumParameter(lst[1])
        for opt in lst[2:-1]:
            ext_enum.options.append(opt)
        return ext_enum

    @property
    def name(self) -> str:
        """
        Name of the parameter

        :return: Name of the parameter
        :rtype: str
        """
        return self.__name

    def set_name(self, name: str) -> None:
        """
        Sets the name of the parameter

        :param name: Name of the parameter
        :type name: str
        """
        self.__name = name
        self._type = f"{self.__name.title()}EnumParameter"

    def __eq__(self, __o: "ExtEnumParameter") -> bool:
        """
        Checks if the parameter is equal to another parameter

        :param __o: Other parameter
        :type __o: ExtEnumParameter
        :return: True if equal, False otherwise
        :rtype: bool
        """
        return self.options == __o.options

    @property
    def options_hash(self) -> int:
        """
        Hash over the options in their specific order

        :return: Hash
        :rtype: int
        """
        return hash(tuple(self.options))
