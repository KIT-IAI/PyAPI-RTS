# LGPL-3.0 License
# Copyright (c) 2023 KIT-IAI-ESA

import re

from pyapi_rts.class_extractor.readers.lines.condition_line_reader import ConditionLineReader, IfElse
from pyapi_rts.class_extractor.graphics_parsing import GRAPHICS_REGEXS
from pyapi_rts.shared import ParameterCondition


class GraphicsConditionLineReader(ConditionLineReader):
    """
    Reads condition lines from the GRAPHICS: block of the Component Definition Files.
    """

    reg = re.compile(
        r"\s*(?:(IfNot)|(ElseIf)|(If)|(Else))(?: )?\(?(.*)\)?",
        re.IGNORECASE,  # (EndIf)|
    )

    def __init__(self, incl_macros: bool = True) -> None:
        super().__init__()
        self.incl_macros = incl_macros

    def get_condition(self, line: str) -> None | tuple[IfElse, ParameterCondition]:
        """
        Reads the condition from the line without changing the result dictionary.
        """
        m = self.reg.match(line)
        if not bool(m):
            return None

        if m.group(1) is not None:
            return (IfElse.IFNOT, self._read_inner_cond(m.group(5), negate=True))
        elif m.group(2) is not None:
            return (IfElse.ELIF, self._read_inner_cond(m.group(5)))
        elif m.group(3) is not None:
            return (IfElse.IF, self._read_inner_cond(m.group(5)))
        else:
            return (IfElse.ELSE, ParameterCondition.empty())

    def is_if_line(self, line: str) -> bool:
        reg = re.compile(r'(?:[^"]|\A)\b(If|IfNot)\s*\(', re.IGNORECASE)
        return reg.search(line) is not None and not self.is_elif_line(line)

    def is_elif_line(self, line: str) -> bool:
        reg = re.compile(r'(?:[^"]|\A)\b(ElseIf)\s*\(', re.IGNORECASE)
        return reg.search(line) is not None

    def is_else_line(self, line: str) -> bool:
        reg = re.compile(r'(?:[^"]|\A)\b(Else)', re.IGNORECASE)
        return reg.search(line) is not None and not self.is_elif_line(line)

    def is_end_line(self, line: str) -> bool:
        reg = re.compile(r'(?:[^"]|\A)\b(EndIf)', re.IGNORECASE)
        return reg.search(line) is not None

    def get_line_components(self, line: str) -> list[str]:
        split_pos = []
        for match in re.finditer(r'(?:[^"]|\A)\bIf\s*\(', line, re.IGNORECASE):
            split_pos.append(match.start())
        for match in re.finditer(r'(?:[^"]|\A)\bIfNot\s*\(', line, re.IGNORECASE):
            split_pos.append(match.start())
        for match in re.finditer(r'(?:[^"]|\A)\bElseIf\s*\(', line, re.IGNORECASE):
            split_pos.append(match.start())
        for match in re.finditer(r'(?:[^"]|\A)\bEndIf\b', line, re.IGNORECASE):
            split_pos.append(match.start())
        for match in re.finditer(r'(?:[^"]|\A)\bElse\b', line, re.IGNORECASE):
            split_pos.append(match.start())

        for pattern in GRAPHICS_REGEXS.values():
            for match in pattern.finditer(line):
                split_pos.append(match.start())

        if self.incl_macros:
            from pyapi_rts.generated.graphics_macros import MACRO_REGEXS

            for pattern in MACRO_REGEXS.values():
                for match in pattern.finditer(line):
                    split_pos.append(match.start())
        if len(split_pos) < 2:
            return [line]

        split_pos.sort()
        split_lines = [
            line[split_pos[i] : split_pos[i + 1]].strip()
            for i in range(len(split_pos) - 1)
        ]
        return split_lines + [line[split_pos[-1] :].strip()]
