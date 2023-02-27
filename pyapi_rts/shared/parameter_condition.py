# LGPL-3.0 License
# Copyright (c) 2023 KIT-IAI-ESA

from enum import Enum
from typing import Any, Union

from pyapi_rts.shared import ParameterBoundProperty


class ParameterCondition:
    """
    A condition that compares two ParameterBoundProperty objects
    """

    def __init__(
        self,
        left: Union[ParameterBoundProperty, "ParameterCondition"],
        right: Union[ParameterBoundProperty, "ParameterCondition"],
        operator: Union["ParameterConditionOperator", "OperatorChainOperator"],
        negate: bool = False,
    ) -> None:
        #: The left side of the condition
        self.left: ParameterBoundProperty | ParameterCondition = left
        #: The right side of the condition
        self.right: ParameterBoundProperty | ParameterCondition = right
        #: The operator of the condition
        self.operator: ParameterConditionOperator | OperatorChainOperator = operator
        #: If True, negate the evaluation of the condition.
        self.negate = negate

    @classmethod
    def empty(cls):
        """
        Returns an empty ParameterCondition that always returns True

        :return: An empty ParameterCondition
        :rtype: _type_
        """
        return ParameterCondition(None, None, ParameterConditionOperator.NONE)

    @classmethod
    def single(cls, lst: list[Any]):
        """
        Returns a parameter condition that always returns the node_list

        :param node_list: The node list to always return
        :type node_list: list[Any]
        :return: A parameter condition that always returns the node_list
        :rtype: tuple[ParameterCondition, list[Any]]
        """
        return (ParameterCondition.empty(), lst)

    def check(self, dictionary) -> bool:
        """
        Evaluates the condition on a dictionary of a component's parameters

        :param dictionary: The dictionary of parameters to evaluate the condition on
        :type dictionary: dict[str, Any]
        :return: True if the condition is met, False if not
        :rtype: bool
        """
        result = self.operator.value[0](self.left, self.right, dictionary)
        if self.negate:
            return not result
        return result

    def __str__(self) -> str:
        param_cond_op = (
            "ParameterConditionOperator."
            if isinstance(self.operator, ParameterConditionOperator)
            else "OperatorChainOperator."
        ) + self.operator.name
        return f"ParameterCondition({self.left},{self.right},{param_cond_op},{self.negate})"


def get_enum_index(enum_value: Any) -> int:
    """
    Returns the index of an enum value

    :param enumValue: The enum value to get the index of
    :type enumValue: Any
    :return: The index of the enum value
    :rtype: int
    """
    return list(enum_value.__class__).index(enum_value)


def get_with_enum_as_index(value: Any) -> Any:
    """
    Returns the index of an enum value if it is an enum value, otherwise returns the value

    :param value: The value to get the index of
    :type value: Any
    :return: The index of the enum value if it is an enum value, otherwise returns the value
    :rtype: Any
    """
    return get_enum_index(value) if isinstance(value, Enum) else value


class ParameterConditionOperator(Enum):
    """
    Enum of all possible parameter condition operators.
    Composed of a function that evaluates the condition and a string representation of the operator
    """

    TOGGLE_EQUAL = (
        lambda l, r, d: get_with_enum_as_index(l.get_value(d))
        == get_with_enum_as_index(r.get_value(d)),
        "==",
    )
    NOT_EQUAL = (
        lambda l, r, d: get_with_enum_as_index(l.get_value(d))
        != get_with_enum_as_index(r.get_value(d)),
        "!=",
    )
    GREATER_THAN_OR_EQUAL = (
        lambda l, r, d: get_with_enum_as_index(l.get_value(d))
        >= get_with_enum_as_index(r.get_value(d)),
        ">=",
    )
    LESS_THAN_OR_EQUAL = (
        lambda l, r, d: get_with_enum_as_index(l.get_value(d))
        <= get_with_enum_as_index(r.get_value(d)),
        "<=",
    )
    GREATER_THAN = (
        lambda l, r, d: get_with_enum_as_index(l.get_value(d))
        > get_with_enum_as_index(r.get_value(d)),
        ">",
    )
    LESS_THAN = (
        lambda l, r, d: get_with_enum_as_index(l.get_value(d))
        < get_with_enum_as_index(r.get_value(d)),
        "<",
    )
    EQUAL = (
        lambda l, r, d: get_with_enum_as_index(l.get_value(d))
        == get_with_enum_as_index(r.get_value(d)),
        "=",
    )
    EQUAL2 = (
        lambda l, r, d: get_with_enum_as_index(l.get_value(d))
        == get_with_enum_as_index(r.get_value(d)),
        ",",
    )
    NONE = (lambda l, r, d: True, "\n")


class OperatorChainOperator(Enum):
    """
    Enum of all possible operator chain operators.
    Composed of the check function and the string representation of the operator.
    """

    AND = (lambda l, r, d: l.check(d) and r.check(d), "&")
    AND2 = (lambda l, r, d: l.check(d) and r.check(d), "&&")
    OR = (lambda l, r, d: l.check(d) or r.check(d), "|")
    OR2 = (lambda l, r, d: l.check(d) or r.check(d), "||")
    LEFT = (lambda l, _, d: l.check(d), "\n")
