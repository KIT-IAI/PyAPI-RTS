# LGPL-3.0 License
# Copyright (c) 2023 KIT-IAI-ESA

import re

from .class_generator import ClassGenerator
from ..extracted.ext_component import ExtComponent


class ClassLoaderGenerator(ClassGenerator):
    """
    Generates the class loader responsible for loading all other classes at runtime
    """

    def __init__(self, comps: list[ExtComponent]) -> None:
        """
        Initializes the ClassLoaderGenerator

        :param comps: list of components
        :type comps: list[ExtComponent]
        """
        super().__init__()
        self.foreach_re = re.compile(r"(.*)FOREACH:(.+)")
        self.comps = comps

    def replace(self, lines: list[str]) -> list[str]:
        """
        Replaces the template statements in the lines

        :param lines: list of lines
        :type lines: list[str]
        :return: list of lines (changed)
        :rtype: list[str]
        """
        lines_out = []
        for l in lines:
            if bool(self.foreach_re.match(l)):
                lines_out += self.replace_foreach(l)
            else:
                lines_out.append(l)
        return lines_out

    def replace_foreach(self, line: str) -> list[str]:
        """
        Replaces the FOREACH statement in one line

        :param line: Line to replace
        :type line: str
        :return: list of lines (changed)
        :rtype: list[str]
        """
        g = self.foreach_re.match(line).groups()
        return [
            g[0]
            + g[1]
            .replace("{{name}}", c.type)
            .replace("{{TypeName}}", c.type_name)
            .replace(
                "{{TypePath}}",
                (
                    self.BASIC_COMPONENT_PATH
                    if c in self.BASIC_COMPONENTS
                    else (self.GENERATED_PATH + c.type_name)
                ),
            )
            for c in self.comps
        ]
