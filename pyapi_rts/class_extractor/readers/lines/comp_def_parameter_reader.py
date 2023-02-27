# LGPL-3.0 License
# Copyright (c) 2023 KIT-IAI-ESA

import re
from .base_line_reader import BaseLineReader
from pyapi_rts.class_extractor.extracted.comp_def_parameter import CompDefParameter


class CompDefParameterReader(BaseLineReader):
    """
    Reads a parameter line from the definition file
    """

    reg = re.compile(
        r"(\S+)\s+\"(.*)\"\s+\"([^\"]*)\"\s+(\S+)\s+(\S+)(?:\s+(\S+)(?:\s+(\S+)(?:\s+(\S+)?(?:\s+(.+)?(?:\s*))?)?)?)?(?:\n|$)"
    )

    def __init__(self) -> None:
        """
        Initializes the CompDefParameterReader
        """
        super().__init__()
        self.results["parameter"] = []

    def read_line(self, line: str) -> None:
        """
        Extracts information from a line

        :param line: Line to read
        :type line: str
        :raises ValueError: Line does not contain a parameter
        """
        m = self.reg.match(line)
        if not bool(m):
            raise ValueError("CompDefParameter: Line must contain a parameter")
        g = m.groups()

        self.write_result(
            "parameter",
            CompDefParameter(
                g[0],
                g[1],
                g[2],
                g[3],
                g[4],
                g[5],
                g[6] if g[6] is not None else "",
                g[7] if g[7] is not None else "",
                g[8] if g[8] is not None else "",
            ),
        )
