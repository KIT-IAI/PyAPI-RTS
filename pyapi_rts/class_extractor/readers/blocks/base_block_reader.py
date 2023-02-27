# LGPL-3.0 License
# Copyright (c) 2023 KIT-IAI-ESA

import re
from typing import Any, Pattern
from pyapi_rts.class_extractor.readers.lines.base_line_reader import BaseLineReader


class BaseBlockReader:
    """
    Base class representing an indented block in a file
    """

    def __init__(self) -> None:
        self.reg: Pattern = re.compile(r"^$")
        #: A list of blocktypes contained in this block : list[CBlockReader]
        self.blocks: list[BaseBlockReader] = []
        #: A list of lineReaders searched for in this block : list[CLineReader]
        self.line_readers: list[BaseLineReader] = []
        #: A dictionary containing the results of the block : dict[str, Any]
        self.reg = re.compile(r"^[A-Z-_]+:(.*)\n?$")
        #: A dictionary containing the results of the block : dict[str, Any]
        self.results: dict[str, Any] = {}

    def write_result(self, key: str, value: Any):
        """
        Appends a result to the results dictionary

        :param key: Key of the result
        :type key: str
        :param value: Value of the result
        :type value: Any
        """
        if key in self.results:
            self.results[key].append(value)
        else:
            self.results[key] = [value]

    def merge_results(self, cblock: "BaseBlockReader") -> None:
        """
        Merge results from another block into this block

        :param cblock: 'CBlockReader'
        :type cblock: 'CBlockReader'
        :return: None
        """
        for k, vs in cblock.results.items():
            for v in vs:
                self.write_result(k, v)

    @classmethod
    def _whitespace_left(cls, line: str) -> int:
        """
        Amount of whitespace on the start of a line

        :param line: Line with whitespace
        :type line: str
        :return: Number of whitespace characters on the start of a line
        :rtype: int
        """
        size = len(line) - len(line.lstrip())
        return line[:size].count(" ") + 4 * line[:size].count("\t")

    @classmethod
    def _strip_left(cls, line: str, size: int) -> str:
        """
        Remove some of the whitespace on the start of a line

        :param line: Line with whitespace
        :type line: str
        :param size: Number of whitespace units to remove
        :type size: int
        :return: Line with whitespace removed
        :rtype: str
        """
        while size > 0:
            if line.startswith("    ") and size >= 4:
                line = line[3:]
                size -= 4
            elif line.startswith(" "):
                if line.startswith(" \t"):
                    pass
                elif line.startswith("  \t") and size >= 2:
                    line = line[1:]
                elif line.startswith("   \t") and size >= 3:
                    line = line[2:]
                else:
                    size -= 1
            elif line.startswith("\t"):
                if size >= 4:
                    size -= 4
                else:
                    line = " " * (4 - size) + line[1:]
                    return line
            else:
                return line
            line = line[1:]
        return line

    def read(self, lines: list[str]) -> None:
        """
        Read a block

        :param lines: list of lines in block
        :type lines: list[str]
        :rtype: None
        """
        index = 1
        while index < len(lines):
            if index + 1 < len(lines) and any(
                filter(lambda x: x.reg.match(lines[index]), self.blocks)
            ):
                # Block found
                strip_len = self._whitespace_left(lines[index + 1])
                end_line = next(
                    filter(
                        (
                            lambda i: self._whitespace_left(lines[i]) == 0
                            and len(lines[i]) > 1
                        ),
                        range(index + 1, len(lines)),
                    ),
                    len(lines),
                )
                flat_block = [lines[index]] + [
                    self._strip_left(l, strip_len) for l in lines[index + 1 : end_line]
                ]
                self.__check_block(flat_block)
                index = end_line
            elif any(filter(lambda x: x.reg.match(lines[index]), self.line_readers)):
                # Line found
                for line_reader in self.line_readers:
                    if bool(line_reader.reg.match(lines[index])):
                        line_reader.read_line(lines[index])
                        index += 1
                        break
            else:
                index += 1

        # Move Results from lineReaders to this block
        for line_reader in self.line_readers:
            for k, vs in line_reader.results.items():
                for v in vs:
                    self.write_result(k, v)
                line_reader.results[k] = []

    def __check_block(self, block: list[str]):
        """
        Checks if a block is supported by any of the blocktypes in this block

        :param block: list of lines in block
        :type block: list[str]
        """
        for block_type in self.blocks:
            if bool(block_type.reg.match(block[0])):
                block_type.read(block)
                return
