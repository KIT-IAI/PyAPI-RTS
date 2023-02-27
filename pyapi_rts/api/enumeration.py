# LGPL-3.0 License
# Copyright (c) 2023 KIT-IAI-ESA

from enum import Enum
import re
import string

from pyapi_rts.api.internals.dfxblock import DfxBlock


class EnumerationStyle(str, Enum):
    Integer = "Integer"
    Hex = "Hex"
    lowercase = "lowercase"
    uppercase = "uppercase"


class Enumeration(DfxBlock):
    """
    Enumeration settings for a component.
    There can be multiple enumerators in one file, but they
    work with internal UUIDs, not easy to reproduce.
    """

    _title_regex = re.compile(r"^ENUMERATION:\s?\n?$")

    """
    The global counter for the components enumerators by name
    """
    counter: dict = {}

    def __init__(self) -> None:
        #: Is the enumeration feature activated?
        self.is_active: bool = False
        #: The style of the enumeration value.
        self.style: EnumerationStyle = EnumerationStyle.Integer
        #: The enumeration string inserted into the name parameter.
        self.enumeration_string: str = "#"
        #: The enumeration value as integer
        self.value: int = 0
        super().__init__()

    def read_block(self, block: list[str], name: str):
        """
        Reads the enumeration block of the .dfx file

        :param block: Enumeration block of the .dfx file
        :type block: list[str]
        :param name: Type name of the component
        :type name: str
        """
        super().read_block(block)
        self.is_active = block.lines[0].lower() == "true"
        self.value = int(block.lines[1])
        self.style = EnumerationStyle[block.lines[2]]
        self.enumeration_string = block.lines[3]

        if self.value == 0:
            return

        if name in Enumeration.counter:
            Enumeration.counter[name] += 1
        else:
            Enumeration.counter[name] = self.value

    @property
    def value_str(self) -> str:
        """
        String representation with applied style of the enumeration value.
        :return: Enumeration value with applied style
        :rtype: str
        """
        if self.value == 0:
            return ""
        if self.style == EnumerationStyle.Integer:
            return str(self.value)
        if self.style == EnumerationStyle.Hex:
            return f"{self.value:x}"

        chars = (
            list(string.ascii_lowercase)
            if self.style == EnumerationStyle.lowercase
            else list(string.ascii_uppercase)
        )
        chars = [""] + chars  # 1 = a, 26 = z

        remainders = []
        quotient, remainder = divmod(self.value, 26)
        while quotient > 0 or remainder > 0:
            if remainder == 0:
                # we don't have an equivalent for 0 in A-Z
                # thus we take Z instead and reduce the higher value by 1
                remainder = 26
                quotient -= 1
            remainders = [remainder] + remainders
            quotient, remainder = divmod(quotient, 26)

        result = "".join(chars[n] for n in remainders)
        return result

    def apply(self, name: str) -> str:
        """
        Applies the rules of this enumeration to a string

        :param name: String to apply the rules to
        :type name: str
        :return: Modified copy of name with rules applied
        :rtype: str
        """
        if not self.is_active:
            return name.replace(self.enumeration_string, "")

        # fill the enumeration string with the actual number
        enum_str = self.enumeration_string.replace("#", self.value_str)
        # insert the enumeration string into the name
        return name.replace("#", enum_str)

    def block(self) -> list[str]:
        """
        Returns the enumeration block of the .dfx file

        :return: Enumeration block of the .dfx file
        :rtype: list[str]
        """
        lines = []
        lines.append("ENUMERATION:")
        lines.append("\t{0}".format("true" if self.is_active else "false"))
        lines.append(f"\t{self.value}")
        lines.append(f"\t{self.style}")
        lines.append(f"\t{self.enumeration_string}")
        return lines
