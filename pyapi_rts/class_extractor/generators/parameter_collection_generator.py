# LGPL-3.0 License
# Copyright (c) 2023 KIT-IAI-ESA

import re

from ..extracted.ext_parameter_coll import ExtParameterColl
from .class_generator import ClassGenerator
from ..utils import valid_file_name


class ParameterCollectionGenerator(ClassGenerator):
    """
    Generates a ParameterCollection (group of parameters) form an ExtParameterColl
    """

    def __init__(self, pc: ExtParameterColl) -> None:
        """
        Initializes the ParameterCollectionGenerator

        :param pc: ParameterCollection to generate a class for
        :type pc: ExtParameterColl
        """
        super().__init__()
        self.pc = pc
        self.foreach_type_re = re.compile(r"(.*)FOREACH_TYPE:(.+)")
        self.foreach_re = re.compile(r"(.*)FOREACH:(.+)")
        self.docstr_re = re.compile(r"(.*)DOCSTR:(.*)")

    def replace(self, lines: list[str]) -> list[str]:
        """
        Replaces the template statements in the lines

        :param lines: Lines in template file
        :type lines: list[str]
        :return: Lines with replaced template statements
        :rtype: list[str]
        """
        lines_out = []
        for l in lines:
            if bool(self.foreach_type_re.match(l)):
                lines_out += self.replace_foreachType(l)
            elif bool(self.foreach_re.match(l)):
                lines_out += self.replace_foreach(l)
            elif bool(self.docstr_re.match(l)):
                g = self.docstr_re.match(l).groups()
                lines_out += [g[0] + '"""']
                for p in self.pc.parameters:
                    lines_out.extend(
                        [
                            g[0] + ":param " + p.name + ": " + p.description,
                            g[0] + ":type " + p.name + ": " + p.comp_type,
                        ]
                    )
                lines_out += [g[0] + '"""']
            else:
                lines_out.append(l.replace("{{name}}", self.pc.type_name))
        return lines_out

    def replace_foreachType(self, line: str) -> list[str]:
        """
        Replaces the FOREACH_TYPE statement in one line

        :param line: Line to replace
        :type line: str
        :return: list of lines (changed)
        :rtype: list[str]
        """
        g = self.foreach_type_re.match(line).groups()
        return [
            g[0]
            + g[1]
            .replace("{{TypeParam}}", o)
            .replace(
                "{{TypePath}}",
                (
                    self.BASIC_COMPONENT_PATH
                    if o in self.BASIC_COMPONENTS
                    else (
                        self.ENUM_PATH
                        if o.endswith("EnumParameter")
                        else self.GENERATED_PATH
                        + valid_file_name(
                            "__".join(self.pc.name.split("__")[:-1])
                        )
                        + "."
                    )
                    + o
                ),
            )
            for o in (set([p.comp_type for p in self.pc.parameters]))
        ]

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
            .replace("{{name}}", p.name)
            .replace("{{key}}", p.key)
            .replace("{{TypeParam}}", p.comp_type)
            .replace("{{args}}", p.get_args())
            for p in self.pc.parameters
        ]
