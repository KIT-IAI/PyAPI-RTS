# LGPL-3.0 License
# Copyright (c) 2023 KIT-IAI-ESA

import re

from .class_generator import ClassGenerator
from pyapi_rts.shared.condition_tree import BBNode


class GraphicsMacroGenerator(ClassGenerator):
    """
    Generates a dictionary with regular expressions for graphics macros.
    """

    def __init__(self, bboxes) -> None:
        """
        Initializes the generator

        :param bboxes: The dictionary with BoundingBoxNodes to the corresponding macros.
        :type bboxes: dict[str, BBNode]
        """
        self.bboxes: dict[str, BBNode] = bboxes
        self.foreach_regex = re.compile(r"(.*)FOREACH_REGEX:(.+)")
        self.foreach_func = re.compile(r"(.*)FOREACH_FUNC:(.+)")
        super().__init__()

    def replace(self, lines: list[str]) -> list[str]:
        """
        Replaces the template statements in the lines

        :param lines: Template file lines
        :type lines: list[str]
        :return: Changed lines
        :rtype: list[str]
        """
        lines_out = []
        for l in lines:
            if bool(self.foreach_regex.match(l)):
                lines_out += self.replace_foreach_regex(l)
            elif bool(self.foreach_func.match(l)):
                lines_out += self.replace_foreach_func(l)
            else:
                lines_out.append(l)
        return lines_out

    def replace_foreach_regex(self, line: str) -> list[str]:
        """
        Replaces the FOREACH_REGEX statement in the template line

        :param line: The line to replace
        :type line: str
        :return: The replaced lines
        :rtype: list[str]
        """
        g = self.foreach_regex.match(line).groups()
        return [g[0] + g[1].replace("{{MACRO}}", o) for o in self.bboxes.keys()]

    def replace_foreach_func(self, line: str) -> list[str]:
        """
        Replaces the FOREACH_FUNC statement in the template line

        :param line: The line to replace
        :type line: str
        :return: The replaced lines
        :rtype: list[str]
        """
        g = self.foreach_func.match(line).groups()
        return [
            g[0]
            + g[1].replace("{{MACRO}}", k).replace("{{BBOX}}", i.bboxes[0].init_code())
            for k, i in self.bboxes.items()
        ]
