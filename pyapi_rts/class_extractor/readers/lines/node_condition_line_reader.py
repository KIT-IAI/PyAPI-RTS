# LGPL-3.0 License
# Copyright (c) 2023 KIT-IAI-ESA

import re
from pyapi_rts.class_extractor.readers.lines.condition_line_reader import ConditionLineReader, IfElse
from pyapi_rts.shared import ParameterCondition


class NodeConditionLineReader(ConditionLineReader):
    """
    Reads condition lines from the NODES: block of the Component Definition Files.
    """

    reg = re.compile(
        r".*#(?:(ElseIf|ELseIf|ELSEIF)|(ELSE|Else)|(IF|If))(?: )?(\(?.*\)?)"
    )

    def __init__(self) -> None:
        super().__init__()

    def get_condition(self, line: str) -> None | tuple["IfElse", ParameterCondition]:
        """
        Reads the condition from the line without changing the result dictionary.
        """
        m = self.reg.match(line)
        if not bool(m):
            return None

        if m.group(3) is not None:
            return (IfElse.IF, self._read_inner_cond(m.group(4)))
        elif m.group(1) is not None:
            return (IfElse.ELIF, self._read_inner_cond(m.group(4)))
        else:
            return (IfElse.ELSE, ParameterCondition.empty())

    def is_if_line(self, line: str) -> bool:
        reg = re.compile(r'(?:[^"]|\A)(#IF)', re.IGNORECASE)
        return reg.search(line) is not None

    def is_elif_line(self, line: str) -> bool:
        reg = re.compile(r'(?:[^"]|\A)(#ELIF|#ELSEIF)', re.IGNORECASE)
        return reg.search(line) is not None

    def is_else_line(self, line: str) -> bool:
        reg = re.compile(r'(?:[^"]|\A)(#ELSE)\b', re.IGNORECASE)
        return reg.search(line) is not None  # and not self.is_elif_line(line)

    def is_end_line(self, line: str) -> bool:
        reg = re.compile(r'(?:[^"]|\A)(#END)', re.IGNORECASE)
        return reg.search(line) is not None
