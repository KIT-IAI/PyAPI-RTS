# LGPL-3.0 License
# Copyright (c) 2023 KIT-IAI-ESA

import pathlib
import re

import lark

from .base_block_reader import BaseBlockReader
from .computation_transformer import ComputationTransformer

PATH = pathlib.Path(__file__).parent.absolute()


class LarkComputationSingleton:
    __instance = None
    __counter = 0
    # SIMPLE_REGEX = re.compile(r"^\s*(INTEGER|REAL|STRING)\s+(\S+)\s+=\s+(\w+)$")
    SIMPLE_REGEX = re.compile(
        r"^\s*(INTEGER|REAL|STRING)\s+(\w+)\s*=\s*((?:\s*\w+\s*[\+\*\/\-]\s*)*)(\w+)\s*$"
    )

    @staticmethod
    def tag_values(string: str) -> str:
        string = string.replace("$", "€")
        if not string.strip().replace(".", "").isdigit() and len(string.strip()) > 0:
            return "$" + string.strip()
        return str(float(string)) if len(string.strip()) > 0 else ""

    @staticmethod
    def parse(computation: str) -> str:
        """
        Parses a computation.
        """
        if len(computation.strip()) < 3:
            return None
        if LarkComputationSingleton.SIMPLE_REGEX.match(computation):
            groups = LarkComputationSingleton.SIMPLE_REGEX.match(computation).groups()
            if len(groups) < 3:
                pass
            comp = ""
            a = groups[2]
            while len(a) > 0:
                var = re.split(r"[\+\-\/\*]", a)[0]
                operator = a[len(var)] if len(a) > len(var) else ""
                comp += LarkComputationSingleton.tag_values(var) + operator
                a = a[len(var) + 1 :]
                # var = LarkComputationSingleton.tag_values(var.strip())
                # comp += var + operator
            comp += (
                str(float(groups[3]))
                if groups[3].replace(".", "").isdigit()
                else LarkComputationSingleton.tag_values(groups[3].strip())
            )
            # comp = ""
            # if groups[2] is None:
            #     comp = LarkComputationSingleton.tag_values(groups[4])
            # else:
            #     i = 2
            #     while i + 1 < len(groups):
            #         comp += LarkComputationSingleton.tag_values(groups[i])
            #         if groups[i + 1] is not None:
            #             comp += groups[i + 1]
            #         i += 2
            return (
                groups[1],
                {"INTEGER": "int", "STRING": "str", "REAL": "float"}[groups[0]],
                comp,
            )
        if LarkComputationSingleton.__instance is None:
            LarkComputationSingleton.__instance = lark.Lark.open(
                PATH / "computations.lark", parser="earley"
            )
        LarkComputationSingleton.__counter += 1
        return LarkComputationSingleton.__instance.parse(computation)


class ComputationsBlock(BaseBlockReader):
    """
    A block reader for the computations block.
    """

    DOLLAR_WORD_REGEX = re.compile(r".*?\$+([\w\.@']+).*")
    EURO_WORD_REGEX = re.compile(r".*?\$?€+([\w\.@']+).*")

    def __init__(self) -> None:
        super().__init__()
        self.reg = re.compile(r"COMPUTATIONS:.*")
        # Contains computations expressed as Python code
        self.results["computations"] = []

    def _post_processing(self, transformed: list[tuple[str, str, str]]) -> dict:
        """
        Post-processes the computation transformed to a Python expression.
        :param transformed: The transformed computation expression.
        :type transformed: list[tuple[str, str, str]]
        :returns: The dictionary of the post-processed computations.
        :rtype: dict
        """

        type_default = {
            "int": 1,
            "str": '""',
            "float": 1.0,
        }

        results = {}
        for computation_name, _type, computation in transformed:
            if computation_name in results.keys():
                continue
                # raise ValueError(
                #    "Computation name '{}' is used twice.".format(computation_name)
                # )

            while re.match(self.DOLLAR_WORD_REGEX, computation) is not None:
                key = re.match(self.DOLLAR_WORD_REGEX, computation).group(1)
                key = key.replace("'", "\\'")
                key = f'self.get_by_key("{key}", {type_default[_type]}, True)'
                computation = re.sub(r"\$+[\w\.@']+", key, computation, 1)

            while re.match(self.EURO_WORD_REGEX, computation) is not None:
                key = re.match(self.EURO_WORD_REGEX, computation).group(1)
                key = key.replace("'", "\\'")
                key = f'self.get_special_value("{key}")'
                computation = re.sub(r"\$?€+[\w\.@']+", key, computation, 1)

            results[computation_name] = (_type, computation)
        return results

    def read(self, lines: list[str]) -> None:
        """
        Reads the computations block.
        """
        # l = lark.Lark.open(PATH / "computations.lark", parser="earley")
        parsed = list(
            map(
                (lambda x: LarkComputationSingleton.parse(x.strip())),
                filter((lambda x: len(x.strip()) > 2), lines[1:]),
            )
        )
        transformed = list(
            filter(
                (lambda x: x is not None),
                map(
                    (
                        lambda line: line
                        if isinstance(line, tuple)
                        else ComputationTransformer().transform(line)
                    ),
                    parsed,
                ),
            )
        )
        for name, (_type, comp) in self._post_processing(transformed).items():
            self.write_result("computations", (name, _type, comp))
        # print("Computations:", len(self.results["computations"]))  # DEBUG
