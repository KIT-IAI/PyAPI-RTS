# LGPL-3.0 License
# Copyright (c) 2023 KIT-IAI-ESA

import re

from .base_block_reader import BaseBlockReader
from pyapi_rts.class_extractor.readers.lines.comp_def_parameter_reader import CompDefParameterReader
from pyapi_rts.class_extractor.extracted.comp_def_parameter import CompDefParameter


class SectionBlock(BaseBlockReader):
    """
    Reads a section of parameters from the definition file
    """

    def __init__(self) -> None:
        super().__init__()
        self.reg = re.compile(r"\s*SECTION:.*")
        self.section_re = re.compile(
            r"\s*SECTION:\s{0,10}(?:(?:\"(.+)\")|(?:(\S+))).*\n?"
        )
        self.results["section"] = []

    def read(self, lines: list[str]) -> None:
        """
        Reads the section block.

        :param lines: Lines to read
        :type lines: list[str]
        :raises ValueError: The first line of the section block is not a section name
        """
        m = self.section_re.match(lines[0])
        if not bool(m):
            raise ValueError("SectionBlock: first line must contain a section name")
        sec = CompDefSection(
            m.groups()[0] if m.groups()[0] is not None else m.groups()[1]
        )

        for i, l in enumerate(lines[1:]):
            l = l.strip()
            cdpr = CompDefParameterReader()
            if bool(cdpr.reg.match(l)):
                cdpr.read_line(l)
                sec.comps.append(cdpr.results["parameter"][-1])
            if self.section_re.match(l):
                # Next section, stop reading
                self.write_result("section", sec)
                self.read(lines[i + 1 :])
                return

        self.write_result("section", sec)


class CompDefSection:
    """
    A section of parameters with a name
    """

    def __init__(self, name: str) -> None:
        self.name = name
        self.comps: list[CompDefParameter] = []
