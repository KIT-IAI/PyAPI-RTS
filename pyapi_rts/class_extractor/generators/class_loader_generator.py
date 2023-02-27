# LGPL-3.0 License
# Copyright (c) 2023 KIT-IAI-ESA

import re

from .class_generator import ClassGenerator
from ..extracted.ext_component import ExtComponent


class ClassLoaderGenerator(ClassGenerator):
    """
    Generates the class loader responsible for loading all other classes at runtime
    """

    def __init__(self, comps: list[ExtComponent], hook_names=list[str]) -> None:
        """
        Initializes the ClassLoaderGenerator

        :param comps: list of components
        :type comps: list[ExtComponent]
        """
        super().__init__()
        self.foreach_re = re.compile(r"(.*)FOREACH:(.+)")
        self.foreach_hook_re = re.compile(r"(.*)FOREACH_HOOK:(.+)")
        self.comps = comps
        self.hooks_name: list[str] = hook_names

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
            elif bool(self.foreach_hook_re.match(l)):
                lines_out += self.replace_foreach_hook(l)
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

    def replace_foreach_hook(self, line: str) -> list[str]:
        """
        Replaces the FOREACH_HOOK statement in one line

        :param line: Line to replace
        :type line: str
        :return: list of lines (changed)
        :rtype: list[str]
        """
        g = self.foreach_hook_re.match(line).groups()
        return [
            g[0] + g[1].replace("{{name}}", hook_name) for hook_name in self.hooks_name
        ]
