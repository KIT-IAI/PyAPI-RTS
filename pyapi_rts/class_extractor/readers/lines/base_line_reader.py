# LGPL-3.0 License
# Copyright (c) 2023 KIT-IAI-ESA

import copy
from typing import Any, Pattern


class BaseLineReader:
    """
    Extracts information from a line matching the given pattern
    """

    reg: Pattern = None

    def __init__(self) -> None:
        #: A dictionary containing the results of the line : dict[str, Any]
        self.results: dict[str, Any] = {}

    def write_result(self, key: str, value: Any):
        """
        Writes a new entry to the results dictionary at a given key

        :param key: Key to write to
        :type key: str
        :param value: Value of result
        :type value: Any
        """
        if key in self.results:
            self.results[key].append(value)
        else:
            self.results[key] = [value]

    def read_line(self, line: str) -> bool:
        """
        Reads a line and extracts information

        :param line: Line to read
        :type line: str
        :return: Success of the read operation
        :rtype: bool
        """
        return False

    def return_and_reset(self) -> dict[str, Any]:
        """
        Returns the results and resets the results dictionary

        :return: Results of the read operation
        :rtype: dict[str, Any]
        """
        ret = copy.deepcopy(self.results)
        for key in self.results.keys():
            self.results[key] = []
        return ret
