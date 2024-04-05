# LGPL-3.0 License
# Copyright (c) 2023 KIT-IAI-ESA

import re


class Block:
    """A block of lines of a DFX file.

    BlockReaders divide lines of a DFX files into blocks that can be used
    by implementations of DfxBlock for further processing.
    This class is basically just a fancy wrapper around a list of strings (lines).
    """

    def __init__(self, lines: list[str]) -> None:

        self.lines: list[str] = []
        """The lines that define the block content."""
        self.title: str = lines[0]
        """The title of the block that defines its type."""

        # Checks for different kinds of indentation
        leading_whitespace_regex = re.compile(r"^(?:[^\S\t]{2,4}|\t)(.+)\s?\n?$")

        if "END" in lines[-1]:
            # Cut last line if END statement was accidentally added to block
            lines = lines[:-1]
        # Remove indentation from block if it is an indented block
        if len(lines) > 1 and bool(leading_whitespace_regex.match(lines[1])):
            lines = [self.title] + [
                leading_whitespace_regex.match(s).groups()[0] for s in lines[1:]
            ]
        self.lines = lines[1:]  # Remove title line
