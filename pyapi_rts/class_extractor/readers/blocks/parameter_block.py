# LGPL-3.0 License
# Copyright (c) 2023 KIT-IAI-ESA

import re

from pyapi_rts.class_extractor.readers.lines.comp_def_parameter_reader import CompDefParameterReader
from .base_block_reader import BaseBlockReader
from .section_block import SectionBlock


class ParameterBlock(BaseBlockReader):
    """
    A block of parameters.
    """

    def __init__(self) -> None:
        """
        Initializes the block reader.
        """
        super().__init__()
        self.reg = re.compile(r"PARAMETERS:.*")
        self.blocks.append(SectionBlock())
        self.line_readers.append(CompDefParameterReader())
        self.results["parameter"] = []
        self.results["section"] = []

    def read(self, lines: list[str]) -> None:
        """
        Reads the parameter block.

        :param lines: Lines to read
        :type lines: list[str]
        """
        super().read(lines)
        for s in self.blocks[0].results["section"]:
            self.write_result("section", s)
