# LGPL-3.0 License
# Copyright (c) 2023 KIT-IAI-ESA

import re

from pyapi_rts.shared import Stretchable
from pyapi_rts.class_extractor.readers.lines.base_line_reader import BaseLineReader
from .base_block_reader import BaseBlockReader


class DirectivesBlock(BaseBlockReader):
    """
    Reads the DIRECTIVES block from the definition file
    """

    def __init__(self) -> None:
        super().__init__()
        self.line_readers.append(StretchLine())
        self.line_readers.append(NameLine())
        self.line_readers.append(LinkLine())
        self.reg = re.compile(r"DIRECTIVES:.*")
        self.results["stretchable"] = []
        self.results["linked"] = []
        self.results["name"] = []


class NameLine(BaseLineReader):
    """
    Reads the name of the parameter naming the component.
    """

    reg = re.compile(r"^NAME = (\S*)\n?$")

    def read_line(self, line: str) -> bool:
        match = self.reg.match(line)
        if match:
            self.write_result("name", match.group(1))


class StretchLine(BaseLineReader):
    """
    Reads the stretchable line from the definition file
    and determines if the component is stretchable
    """

    reg = re.compile(r"STRETCHABLE = (\S+).*")

    def read_line(self, line: str) -> bool:
        """
        Determines if the component is stretchable

        :param line: Line with the stretchable directive
        :type line: str
        :raises ValueError: Line does not contain a stretchable directive
        :return: Success if stretchable directive was found
        :rtype: bool
        """

        match = self.reg.match(line)
        if not bool(match):
            raise ValueError("Invalid line: " + line)
        if match.group(1) == Stretchable.UP_DOWN.value[0]:
            self.write_result("stretchable", Stretchable.UP_DOWN)
        elif match.group(1) == Stretchable.BOX.value[0]:
            self.write_result("stretchable", Stretchable.BOX)
        else:
            self.write_result("stretchable", Stretchable.NO)


class LinkLine(BaseLineReader):
    """
    Reads the COMPONENT_LINKED line.
    """

    reg = re.compile(r"LINKED_COMPONENT\s*=\s*TRUE.*")

    def read_line(self, line: str) -> bool:
        match = self.reg.match(line)
        if match:
            self.write_result("linked", True)
