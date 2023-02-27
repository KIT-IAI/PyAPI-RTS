# LGPL-3.0 License
# Copyright (c) 2023 KIT-IAI-ESA

import unittest

from pyapi_rts.class_extractor.readers.lines.condition_line_reader import IfElse
from pyapi_rts.class_extractor.readers.lines.node_condition_line_reader import (
    NodeConditionLineReader,
)
from pyapi_rts.shared import (
    ParameterBoundProperty,
    ParameterConditionOperator,
    OperatorChainOperator,
)


class NodeConditionLineReaderTest(unittest.TestCase):
    """
    Tests the NodeConditionLineReader class.
    """

    def test_get_condition(self):
        """
        Tests the get_condition method.
        """
        clr = NodeConditionLineReader()
        condition = clr.get_condition("#IF (phview==0)")
        self.assertEqual(condition[0], IfElse.IF)
        self.assertEqual(condition[1].left, ParameterBoundProperty("$phview", int))
        self.assertEqual(condition[1].right, ParameterBoundProperty(0, int))
        self.assertEqual(
            condition[1].operator,
            ParameterConditionOperator.TOGGLE_EQUAL,
        )

        # Chained condition
        condition = clr.get_condition("#IF Intp==1&& IntpFrac==1")
        self.assertEqual(condition[0], IfElse.IF)
        self.assertEqual(
            condition[1].left.left,
            ParameterBoundProperty("$Intp", int),
        )
        self.assertEqual(condition[1].left.right, ParameterBoundProperty(1, int))
        self.assertEqual(
            condition[1].left.operator,
            ParameterConditionOperator.TOGGLE_EQUAL,
        )
        self.assertEqual(
            condition[1].right.left,
            ParameterBoundProperty("$IntpFrac", int),
        )
        self.assertEqual(condition[1].right.right, ParameterBoundProperty(1, int))
        self.assertEqual(
            condition[1].right.operator,
            ParameterConditionOperator.TOGGLE_EQUAL,
        )
        self.assertEqual(condition[1].operator, OperatorChainOperator.AND2)

        # ElIf without brackets
        condition = clr.get_condition("#ElseIf phview==1")
        self.assertEqual(condition[0], IfElse.ELIF)
        self.assertEqual(condition[1].left, ParameterBoundProperty("$phview", int))
        self.assertEqual(condition[1].right, ParameterBoundProperty(1, int))
        self.assertEqual(
            condition[1].operator,
            ParameterConditionOperator.TOGGLE_EQUAL,
        )

        # Brackets and additions
        condition = clr.get_condition("#IF (YD1 + YD2 + YD3)>2")
        self.assertEqual(condition[0], IfElse.IF)
        self.assertEqual(
            condition[1].left,
            ParameterBoundProperty("$(YD1 + YD2 + YD3)", int),
        )
        self.assertEqual(condition[1].right, ParameterBoundProperty(2, int))
        self.assertEqual(
            condition[1].operator,
            ParameterConditionOperator.GREATER_THAN,
        )

        # No operator
        condition = clr.get_condition("#IF EMON")
        self.assertEqual(condition[0], IfElse.IF)
        self.assertEqual(
            condition[1].left,
            ParameterBoundProperty("$EMON", int),
        )
        self.assertEqual(condition[1].right, ParameterBoundProperty(1, int))
        self.assertEqual(
            condition[1].operator,
            ParameterConditionOperator.EQUAL,
        )

    def test_get_condition_brackets(self):
        clr = NodeConditionLineReader()

        # condition = clr.get_condition("#IF numtl=0&&(nc01>2)")
        # condition = clr.get_condition("#IF (numtl=0)&&nc01>2")
        # condition = clr.get_condition("#IF A | B && C || D")

        condition = clr.get_condition("#IF (numtl=0&&nc01>2)|(numtl=1&(nc11>2))")
        self.assertEqual(condition[0], IfElse.IF)
        self.assertEqual(condition[1].operator, OperatorChainOperator.OR)

        self.assertEqual(condition[1].left.operator, OperatorChainOperator.AND2)
        self.assertEqual(
            condition[1].left.left.left,
            ParameterBoundProperty("$numtl", int),
        )
        self.assertEqual(
            condition[1].left.left.right,
            ParameterBoundProperty(0, int),
        )
        self.assertEqual(
            condition[1].left.left.operator,
            ParameterConditionOperator.EQUAL,
        )


if __name__ == "__main__":
    unittest.main()
