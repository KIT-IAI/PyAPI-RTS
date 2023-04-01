# LGPL-3.0 License
# Copyright (c) 2023 KIT-IAI-ESA

from enum import Enum
import re
from typing import Any


class ParameterBoundProperty:
    """
    A property that can be bound to a parameter or an explicit value.
    """

    SINGLE_VALUE_BRACKETS_PATTERN = re.compile(r"\$\((\s*[A-z_\-\d\.]+)\s*\)")
    MULTIPLICATION_PATTERN = re.compile(
        r"\$\((.*\s)?(-?[A-z_\d\.]+)\s*(\*)\s*(-?[A-z_\d\.]+)(.*)\)"
    )  # groups: rest, left, operator, right, rest
    OPERATOR_PATT = re.compile(
        r"\$\((-?.*?)\s*([+%-])\s*(-?[A-z_\d\.]+)\s*\)"
    )  # groups: left, operator, rest
    INNER_BRACKET_PATTERN = re.compile(
        r"\$\((.*)\((.*)\)(.*)\)"
    )  # groups: rest-l, brackets content, rest-r

    def __init__(self, value: Any | str, _type: type) -> None:
        self.__value = value
        self.__type = _type

    def __resolve(self, string: str, dictionary: dict) -> Any:
        """
        Resolves a description of a parameter bound property.

        :param string: The description of the parameter bound property
        :type string: str
        :param dictionary: The dictionary of a component's parameters
        :type dictionary: dict, optional
        :return: The resolved value of the parameter bound property
        :rtype: Any
        """
        if len(string.strip()) == 0:
            return 0

        if string.strip().replace("-", "").isnumeric():
            return float(string.strip())

        if string[0] == "$" and not "(" in string:
            if not string[1:].strip() in dictionary:
                return 0
            value = dictionary[string[1:].strip()].value
            if isinstance(value, Enum):
                return list(value.__class__).index(value)
            else:
                return value

        if self.SINGLE_VALUE_BRACKETS_PATTERN.match(string):
            if string[2:-1].strip().replace("-", "").isdigit():
                return int(string[2:-1].strip())
            return self.__resolve(f"${string[2:-1].strip()}", dictionary)

        if self.INNER_BRACKET_PATTERN.match(string):
            groups = self.INNER_BRACKET_PATTERN.match(string).groups()
            inner = self.__resolve(f"$({groups[1]})", dictionary)
            return self.__resolve(f"$({groups[0]}{inner}{groups[2]})", dictionary)

        if self.MULTIPLICATION_PATTERN.match(string):
            groups = self.MULTIPLICATION_PATTERN.match(string).groups()
            res = self.__resolve(f"$({groups[1]})", dictionary) * self.__resolve(
                f"$({groups[3]})", dictionary
            )
            left = groups[0] if groups[0] is not None else ""
            right = groups[4] if groups[4] is not None else ""
            return self.__resolve(f"$({left} {res} {right})", dictionary)

        if self.OPERATOR_PATT.match(string):
            groups = self.OPERATOR_PATT.match(string).groups()
            res = (
                int(groups[2])
                if groups[2].replace("-", "").isdigit()
                else self.__resolve("$" + groups[2], dictionary)
            )
            if groups[1] == "+":
                res = self.__resolve(f"$({groups[0]})", dictionary) + res
            elif groups[1] == "-":
                res = self.__resolve(f"$({groups[0]})", dictionary) - res
            elif groups[1] == "%":
                res = self.__resolve(f"$({groups[0]})", dictionary) % res
            return res

        return 0

    def get_value(self, dictionary: dict = None) -> Any | str:
        """
        Returns the value of the parameter bound property.

        :param dictionary: The dictionary of a component's parameters
        :type dictionary: dict, optional
        :return: The value of the property
        :rtype: Any | str
        """
        if dictionary is None:
            dictionary = {}
        if isinstance(self.__value, str) and self.__value.startswith("$"):
            return self.__resolve(str(self.__value), dictionary)
        return self.__value

    def get_direct_value(self) -> Any:
        """
        Returns the value of the parameter bound property.

        :return: The value of the property
        :rtype: Any
        """
        return self.__value

    def set_value(self, value: Any | str):
        """
        Sets the value of the parameter bound property.

        :param value: The value of the property
        :type value: Any | str
        """
        if (
            isinstance(self.__value, str) and self.__value.startswith("p_")
        ) or self.__type == type(value):
            self.__value = value

    def __str__(self) -> str:
        """
        Returns Python code generating this object.

        :return: Python code generating this ParameterBoundProperty
        :rtype: str
        """
        first_arg = (
            str(self.__value)
            if not isinstance(self.__value, str)
            else f'"{self.__value}"'
        )
        return f"ParameterBoundProperty({first_arg},{self.__type.__name__})"

    def __eq__(self, __o: object) -> bool:
        """
        Returns whether this ParameterBoundProperty is equal to another object.

        :param __o: The object to compare to
        :type __o: object
        :return: Whether this ParameterBoundProperty is equal to another object
        :rtype: bool
        """
        if not isinstance(__o, ParameterBoundProperty):
            return False
        return self.__value == __o.__value and self.__type == __o.__type
