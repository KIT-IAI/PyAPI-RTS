# LGPL-3.0 License
# Copyright (c) 2023 KIT-IAI-ESA

from enum import Enum
import re
from pyapi_rts.shared import (
    ParameterBoundProperty,
)
from pyapi_rts.shared import (
    ParameterCondition,
    ParameterConditionOperator,
    OperatorChainOperator,
)


class IfElse(Enum):
    """
    Enum for the different types of condition

    :param Enum: IF,ELSE,ELSE
    :type Enum: Enum
    """

    IF = 0
    ELIF = 1
    ELSE = 2
    IFNOT = 3


class ConditionLineReader:
    """
    Reads a condition line from the definition file
    """

    reg = re.compile(r"")  # Replace in inheriting classes

    def get_condition(self, line: str) -> None | tuple["IfElse", ParameterCondition]:
        """
        Reads the condition from the line without changing the result dictionary.
        """
        return None

    def is_if_line(self, line: str) -> bool:
        """
        Checks if the line is a start line
        """
        return False

    def is_elif_line(self, line: str) -> bool:
        """
        Checks if the line is an elif line
        """
        return False

    def is_else_line(self, line: str) -> bool:
        """
        Checks if the line is an else line
        """
        return False

    def is_end_line(self, line: str) -> bool:
        """
        Checks if the line is an end line
        """
        return False

    def is_condition_line(self, line: str) -> bool:
        """
        Checks if the line is a condition line or an end line
        """
        return (
            self.is_if_line(line)
            or self.is_elif_line(line)
            or self.is_else_line(line)
            or self.is_end_line(line)
        )

    def _determine_split_operator(self, expr: str) -> tuple[int, OperatorChainOperator]:
        # (symbol, index, priority, level)
        # priority: AND is stronger than OR -> split OR first
        # level: number of brackets -> split lower levels first
        operators = []
        level = 0
        i = 0
        while i < len(expr):
            if expr[i] == "(":
                level += 1
            elif expr[i] == ")":
                level -= 1
            elif expr[i] == "&":
                if i + 1 < len(expr) and expr[i + 1] == "&":
                    operators.append((OperatorChainOperator.AND2, i, 2, level))
                    i += 1
                else:
                    operators.append((OperatorChainOperator.AND, i, 2, level))
            elif expr[i] == "|":
                if i + 1 < len(expr) and expr[i + 1] == "|":
                    operators.append((OperatorChainOperator.OR2, i, 1, level))
                    i += 1
                else:
                    operators.append((OperatorChainOperator.OR, i, 1, level))
            i += 1

        if operators:
            operators.sort(key=lambda x: x[2])  # sort after priority
            operators.sort(key=lambda x: x[3])  # sort after level
            return (operators[0][1], operators[0][0])
        return (None, None)

    def _read_inner_cond(self, s: str, negate: bool = False) -> ParameterCondition:
        """
        Reads the inner condition block and build the complete condition recursively

        :param s: String to read
        :type s: str
        :return: The complete condition
        :rtype: ParameterCondition
        """
        s = s.strip()

        split_index, operator = self._determine_split_operator(s)
        if split_index is not None:
            symbol = operator.value[1]
            return ParameterCondition(
                self._read_inner_cond(s[:split_index]),
                self._read_inner_cond(s[split_index+len(symbol):]),
                operator,
                negate,
            )

        for c, symbol in [o.value for o in ParameterConditionOperator]:
            spl = s.split(symbol)
            if len(spl) == 2 and symbol != "\n":
                left = self._read_property(spl[0])
                right = self._read_property(spl[1])
                return ParameterCondition(
                    left, right, ParameterConditionOperator((c, symbol)), negate
                )
        return ParameterCondition(
            self._read_property(s),
            ParameterBoundProperty(1, (int)),
            ParameterConditionOperator.EQUAL,
            negate,
        )

    def _read_property(self, string: str) -> ParameterBoundProperty | None:
        """
        Reads a property for comparison operations, can be a parameter or a value

        :param s: String to read
        :type s: str
        :return: Parameter name or value
        :rtype: ParameterBoundProperty | None
        """
        s_without_brackets = string.replace("(", "").replace(")", "")
        if s_without_brackets.strip().isdigit():
            return ParameterBoundProperty(int(s_without_brackets.strip()), (int))
        if not string.strip().endswith("()"):
            if s_without_brackets.strip().isalnum():
                return ParameterBoundProperty("$" + s_without_brackets.strip(), (int))
            # Calculation, add brackets
            return ParameterBoundProperty(
                "$(" + s_without_brackets.strip() + ")", (int)
            )
        # Special case: Special function
        return ParameterBoundProperty("$" + string, (int))


class ConditionLineTree:
    def __init__(self) -> None:
        pass
