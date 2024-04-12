# LGPL-3.0 License
# Copyright (c) 2023 KIT-IAI-ESA

import re

from pyapi_rts.api.internals.block import Block
from pyapi_rts.api.internals.dfxblock import DfxBlock


class ParametersBlock(DfxBlock):
    """A block with a collection of parameters as a dictionary"""

    _title_regex = re.compile(r"^PARAMETERS-START:\s?\n?$")

    def __init__(self) -> None:
        self.parameters: dict[str, str] = {}
        super().__init__()

    def read_block(self, block: Block) -> None:
        for line in block.lines:
            split = line.split("\t:")
            self.parameters[split[0]] = split[1]

    def block(self) -> list[str]:
        lines = (
            ["PARAMETERS-START:"]
            + [f"{key}\t:{value}" for key, value in self.parameters.items()]
            + ["PARAMETERS-END:"]
        )
        return lines
