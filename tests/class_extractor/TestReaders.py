# LGPL-3.0 License
# Copyright (c) 2023 KIT-IAI-ESA

import re
from pyapi_rts.class_extractor.readers.blocks.base_block_reader import BaseBlockReader

from pyapi_rts.class_extractor.readers.lines.base_line_reader import BaseLineReader


class ExampleLineReader(BaseLineReader):
    """
    Test Line Reader, reads line in the following format: "INT: <value>"
    """

    reg = re.compile(r"^INT:\s+(\d+)\n?$")

    def __init__(self) -> None:
        """
        Initialize the TestLineReader.
        """
        super().__init__()
        self.reg = re.compile(r"^INT:\s+(\d+)\n?$")
        self.results["int"] = []

    def read_line(self, line: str) -> bool:
        """
        Read a line if it matches the regular expression.

        :param line: Line to read
        :type line: str
        :rtype: bool
        :return: True if the line was read, False otherwise
        """
        match = self.reg.match(line)
        if match and match.group(1).isdigit():
            self.write_result("int", int(match.group(1)))
            return True
        return False


class ExampleBlockReader(BaseBlockReader):
    """
    Test Block Reader, reads blocks in the format: "BLOCK:"
    """

    def __init__(self) -> None:
        """
        Initialize the block reader.
        """
        super().__init__()
        self.reg = re.compile(r"^BLOCK:\n?$")
        self.line_readers.append(ExampleLineReader())
