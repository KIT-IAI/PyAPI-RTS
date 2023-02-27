# LGPL-3.0 License
# Copyright (c) 2023 KIT-IAI-ESA


import re

from ..extracted.ext_component import ExtComponent
from .class_generator import ClassGenerator


class ComponentGenerator(ClassGenerator):
    """
    Generates a python class representing a RSCAD FX component
    """

    def __init__(self, comp: ExtComponent) -> None:
        """
        Initializes the class generator

        :param comp: The component to generate a class for
        :type comp: ExtComponent
        """
        self.comp = comp
        self.foreach_type_re = re.compile(r"(.*)FOREACH_TYPE:(.+)")
        self.foreach_param_re = re.compile(r"(.*)FOREACH_PARAM:(.+)")
        self.foreach_coll_re = re.compile(r"(.*)FOREACH_COLL:(.+)")
        self.foreach_comp_re = re.compile(r"(.*)FOREACH_COMP:(.+)")
        self.rectangle_init_re = re.compile(r"(.*)RECT_INIT:(.*)")
        self.rectangle_func_re = re.compile(r"(.*)RECT_FUNC:(.*)")
        self.docstr_re = re.compile(r"(.*)DOCSTR:(.*)")
        self.tags_re = re.compile(r"(.*)TAGS\[(\S+)\]:(.*)")
        # self.BindClassesRe = re.compile(r"(.*)BIND_CLASSES:(.*)")
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
            if bool(self.foreach_type_re.match(l)):
                lines_out += self.replace_foreach_type(l)
            elif bool(self.foreach_param_re.match(l)):
                lines_out += self.replace_foreach_param(l)
            elif bool(self.foreach_coll_re.match(l)):
                lines_out += self.replace_foreach_coll(l)
            elif bool(self.foreach_comp_re.match(l)):
                lines_out += self.replace_foreach_comp(l)
            elif bool(self.rectangle_init_re.match(l)):
                if self.comp.rectangle is not None:
                    g = self.rectangle_init_re.match(l).groups()
                    lines_out += [
                        g[0] + lin for lin in self.comp.rectangle.component_init()
                    ]
            elif bool(self.tags_re.match(l)):
                g = self.tags_re.match(l).groups()
                if getattr(self.comp, g[1]) is not None:
                    lines_out += [
                        g[0] + g[2].replace("{{value}}", str(getattr(self.comp, g[1])))
                    ]
            elif bool(self.rectangle_func_re.match(l)):
                if self.comp.rectangle is not None:
                    g = self.rectangle_func_re.match(l).groups()
                    lines_out += [
                        g[0] + lin for lin in self.comp.rectangle.rectangle_functions()
                    ]
            elif bool(self.docstr_re.match(l)):
                g = self.docstr_re.match(l).groups()
                lines_out += [g[0] + '"""']
                for p in self.comp.parameters:
                    lines_out.extend(
                        [
                            g[0] + ":param " + p.name + ": " + p.description,
                            g[0] + ":type " + p.name + ": " + p.comp_type,
                        ]
                    )
                lines_out += [g[0] + "\t" + p.name for p in self.comp.collections]
                lines_out += [g[0] + '"""']
            else:
                lines_out.append(
                    l.replace("{{name}}", self.comp.type)
                    .replace("{{TypeName}}", self.comp.type_name)
                    .replace(
                        "{{name_param_key}}",
                        '"' + str(self.comp.name_parameter_key) + '"'
                        if self.comp.name_parameter_key is not None
                        else "None",
                    )
                )
        return lines_out

    def replace_foreach_type(self, line: str) -> list[str]:
        """
        Replaces the FOREACH_TYPE statement in the template line

        :param line: The line to replace
        :type line: str
        :return: The replaced lines
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
                        else self.GENERATED_PATH + self.comp.type_name + "."
                    )
                    + o
                ),
            )
            for o in (set([p.comp_type for p in self.comp.parameters]))
        ]

    def replace_foreach_param(self, line: str) -> list[str]:
        """
        Replaces the FOREACH_PARAM statement in the template line

        :param line: The line to replace
        :type line: str
        :return: The replaced lines
        :rtype: list[str]
        """
        g = self.foreach_param_re.match(line).groups()
        return [
            g[0]
            + g[1]
            .replace("{{name}}", p.name)
            .replace("{{key}}", repr(p.key)[1:-1])
            .replace("{{TypeParam}}", p.comp_type)
            .replace("{{default}}", repr(p.default))
            for p in self.comp.parameters
        ]

    def replace_foreach_coll(self, line: str) -> list[str]:
        """
        Replaces the FOREACH_COLL statement in the template line

        :param line: The line to replace
        :type line: str
        :return: The replaced lines
        :rtype: list[str]
        """
        # TODO: Check for binding overwrite
        g = self.foreach_coll_re.match(line).groups()
        return [
            g[0]
            + g[1].replace("{{name}}", c.name).replace("{{TypeParam}}", c.type_name)
            for c in self.comp.collections
        ]

    def sanitize_parameter_name(self, name: str) -> str:
        """
        Sanitizes the parameter name to be valid Python variable name

        :param name: The parameter name
        :type name: str
        :return: The sanitized name
        :rtype: str
        """
        name = name.replace("'", "_2")
        if name[0].isdigit():
            name = "d" + name
        return name

    def replace_foreach_comp(self, line: str) -> list[str]:
        """
        Replaces the FOREACH_COMP statement in the template line

        :param line: The line to replace
        :type line: str
        :return: The replaced lines
        :rtype: list[str]
        """
        g = self.foreach_comp_re.match(line).groups()
        if "{{method}}" in g[1]:
            result = []
            for c in self.comp.computations:
                result += [
                    f"def {self.sanitize_parameter_name(c[0])}(self) -> {c[1]}:",
                    f"  return ({c[1]})({c[2]})",
                    f"",
                ]
            result = [g[0] + r for r in result]
            return result
        return [
            g[0]
            + g[1]
            .replace("{{name_parameter}}", self.sanitize_parameter_name(c[0]))
            .replace("{{name_esc}}", c[0].replace("'", "\\'"))
            .replace("{{type}}", c[1])
            .replace("{{expression}}", c[2])
            for c in self.comp.computations
        ]
