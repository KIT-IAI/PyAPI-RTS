# LGPL-3.0 License
# Copyright (c) 2023 KIT-IAI-ESA

import re


import pyapi_rts.api.internals.blockreader


class Block:
    """
    A Block read by the BlockReader with own Block Reader to read lower layers of the hierarchy
    """

    def __init__(self, lines: list[str]) -> None:

        #: The lines of the block
        self.lines: list[str] = []
        #: The name of the block
        self.title: str = ""
        #: The block reader for the content of the block
        self.reader: pyapi_rts.api.internals.blockreader.BlockReader = None

        # Checks for different kinds of indentation
        leading_whitespace_regex = re.compile(r"^(?:[^\S\t]{2,4}|\t)(.+)\s?\n?$")

        self.title = lines[0]
        if "END" in lines[-1]:
            # Cut last line if END statement was accidentally added to block
            lines = lines[:-1]
        # Remove indentation from block if it is an indented block
        if len(lines) > 1 and bool(leading_whitespace_regex.match(lines[1])):
            lines = [self.title] + [
                leading_whitespace_regex.match(s).groups()[0] for s in lines[1:]
            ]
        self.lines: list[str] = lines[1:]  # Remove title line
        self.reader = pyapi_rts.api.internals.blockreader.BlockReader(
            self.lines
        )  # Pass lines to block reader
