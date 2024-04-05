# LGPL-3.0 License
# Copyright (c) 2023 KIT-IAI-ESA

import re

from pyapi_rts.api.internals.block import Block


class BlockReader:
    """Used to read the content of DFX files.
    
    The BlockReader is instantiated with a list of strings that represent the lines of a DFX file.
    Its sole purpose is to identify the limits of blocks in these lines and provide them for 
    further processing.
    """

    def __init__(self, source: list[str]) -> None:
        self.source = source
        """The source lines of the file."""
        self.current_block: Block | None = None
        """The last block that was read."""
        self.blocks: list[Block] = []
        """All blocks read until now"""

        self.__position = 0
        self.__start_regex = re.compile(r"^(.+)[-_]START:(?:.*)\n?$")
        self.__indent_regex = re.compile(r"^(?:[^\S\t]{2,4}|\t+)(.+)\s?\n?$")

        self.next_block()

    def __check_indent(self, line: str) -> bool:
        """Checks if a string starts with tabulator or multiple spaces

        :param line: string to check
        :type line: str
        :return: True if line starts with tabulator or multiple spaces
        :rtype: bool
        """
        return bool(self.__indent_regex.match(line))

    def next_block(self) -> bool:
        """Try to read next block

        :return: success, false if no next block exists
        :rtype: bool
        """
        start = self.__position
        end = 0
        fin = False

        # Loop until source ends or next block found
        while self.__position < len(self.source) and not fin:
            if self.__check_indent(self.source[self.__position]):
                # Indented block found
                start = self.__position - 1
                end = next(
                    filter(
                        lambda i: not self.__check_indent(self.source[i]),
                        range(start + 1, len(self.source)),
                    ),
                    len(self.source),
                )
                # get index of next line not indented
                fin = True

            elif bool(self.__start_regex.match(self.source[self.__position])):
                # Found START-END block
                start = self.__position
                # Extract Name of block (???-START:)
                block_id = self.__start_regex.match(self.source[self.__position]).groups()[0]

                # Regexes for counting depth of hierarchy
                start_reg = re.compile(r"^" + block_id + r"[-_]START:(?:.*)\n?")
                end_reg = re.compile(r"^" + block_id + r"[-_]END:(?:.*)\n?")

                end = start + 1
                depth = 1
                while end < len(self.source) and depth > 0:
                    # Loop until end is found or source ends
                    if start_reg.match(self.source[end]):
                        depth += 1
                    elif end_reg.match(self.source[end]):
                        depth -= 1

                    end += 1
                fin = True
                if end != len(self.source):
                    end -= 1  # Fix end position if this is the last block

            else:
                self.__position += 1

            if fin:
                self.current_block = Block(self.source[start:end])  # Create new block
                self.__position = end
                # Append new block to list of blocks
                self.blocks.append(self.current_block)
                return True
        return False
