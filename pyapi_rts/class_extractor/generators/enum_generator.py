# LGPL-3.0 License
# Copyright (c) 2023 KIT-IAI-ESA

import hashlib
import re

from ..extracted.ext_enum_parameter import ExtEnumParameter
from .class_generator import ClassGenerator


class EnumGenerator(ClassGenerator):
    """
    Generates a python class file from an ExtEnumParameter
    """

    def __init__(self, enum: ExtEnumParameter) -> None:
        self.enum = enum
        self.foreach_re = re.compile(r"(.*)FOREACH:(.+)")
        super().__init__()

    def replace(self, lines: list[str]) -> list[str]:
        """
        Replaces the template statements in the lines

        :param lines: Template file lines
        :type lines: list[str]
        :return: Template file lines (changed)
        :rtype: list[str]
        """
        lines_out = []
        for l in lines:
            if bool(self.foreach_re.match(l)):
                lines_out += self.replace_foreach(l)
            else:
                lines_out.append(
                    l.replace("{{name}}", self.enum.name.title()).replace(
                        "{{defaultValue}}", self.enum.options[0]
                    )
                )
        return lines_out

    def replace_foreach(self, line: str) -> list[str]:
        """
        Replaces the FOREACH statement in one line

        :param line: Line to replace
        :type line: str
        :return: Changed lines
        :rtype: list[str]
        """
        g = self.foreach_re.match(line).groups()
        sani_opts = list(self.enum.options)
        sani_opts = [
            o.replace(" ", "_")
            .replace("/", "slash")
            .replace("%", "prct")
            .replace("(", "")
            .replace(")", "")
            .replace("None", "None_")
            .replace("-", "_")
            .replace("+", "plus")
            .replace(".", "dot")
            .replace("~", "wave")
            .replace("#", "hash")
            .replace("^", "up")
            .replace("*", "star")
            .replace("$", "dollar")
            .replace(">", "right")
            .replace("<", "left")
            .replace(",", "commma")
            .replace("=", "eq")
            .replace("&", "and")
            .replace("|", "or")
            .replace("!", "not")
            .replace("?", "question")
            .replace(";", "semicolon")
            .replace("{", "brace")
            .replace("}", "brace")
            .replace("[", "bracket")
            .replace("]", "bracket")
            for o in sani_opts
        ]
        sani_opts = ["DEF" if o == "def" else o for o in sani_opts]
        sani_opts = [("".join(o[2:]) if o.startswith("__") else o) for o in sani_opts]
        sani_opts = [
            ("d" if len(o) > 0 and o[0].isdigit() else "") + o for o in sani_opts
        ]
        sani_opts = [
            ("".join(o[:-1]) if o.endswith("_") and o.startswith("_") else o)
            for o in sani_opts
        ]
        opts = list(self.enum.options)

        option_hash = hashlib.new("sha256")
        for elem in sani_opts:
            option_hash.update(elem.encode("utf-8"))
        option_hash = option_hash.hexdigest()
        opt_list = [
            g[0]
            + g[1]
            .replace(
                "{{option_sani}}",
                (f"EmptyString{option_hash[:10]}{i}" if len(sani_opts[i]) == 0 else "")
                + sani_opts[i],
            )
            .replace("{{option}}", opts[i])
            for i in range(len(opts))
        ]
        return list(opt_list)
