# LGPL-3.0 License
# Copyright (c) 2023 KIT-IAI-ESA

import re

from pyapi_rts.api.internals.dfxblock import DfxBlock


class ParametersBlock(DfxBlock):
    """
    A block with a collection of parameters as a dictionary
    """

    _title_regex = re.compile(r"^PARAMETERS-START:\s?\n?$")

    def __init__(self) -> None:
        self._parameters: dict[str, str] = {}
        super().__init__()

    def read_block(self, block):
        super().read_block(block)
        for line in block.lines:
            split = line.split("\t:")
            self._parameters[split[0]] = split[1]

    def block(self) -> list[str]:
        lines = []
        lines.append("PARAMETERS-START:")
        lines = lines + [
            "{0}\t:{1}".format(key, value) for key, value in self._parameters.items()
        ]
        lines.append("PARAMETERS-END:")
        return lines
