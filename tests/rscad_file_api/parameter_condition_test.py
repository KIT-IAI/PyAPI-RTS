# LGPL-3.0 License
# Copyright (c) 2023 KIT-IAI-ESA

import unittest
from pyapi_rts.shared import (
    ParameterBoundProperty,
)

from pyapi_rts.shared import (
    OperatorChainOperator,
    ParameterCondition,
    ParameterConditionOperator,
)
from pyapi_rts.api.parameters.integer_parameter import IntegerParameter


class ParameterConditionTest(unittest.TestCase):
    """
    Tests the ParameterCondition class.
    """

    def test_init(self):
        """
        Test the __init__ method.
        """
        pbp = ParameterBoundProperty(1, int)
        param_cond = ParameterCondition(pbp, pbp, ParameterConditionOperator.EQUAL)
        self.assertEqual(param_cond.left, pbp)
        self.assertEqual(param_cond.right, pbp)
        self.assertEqual(param_cond.operator, ParameterConditionOperator.EQUAL)
        condition_chain = ParameterCondition(
            param_cond, param_cond, OperatorChainOperator.AND
        )
        self.assertEqual(condition_chain.left, param_cond)
        self.assertEqual(condition_chain.right, param_cond)
        self.assertEqual(condition_chain.operator, OperatorChainOperator.AND)

    def test_empty_single(self):
        """
        Test the empty and single classmethods.
        """
        param_cond = ParameterCondition.empty()
        self.assertEqual(param_cond.left, None)
        self.assertEqual(param_cond.right, None)
        self.assertEqual(param_cond.operator, ParameterConditionOperator.NONE)
        param_cond_single, lst = ParameterCondition.single([1, 2, 3])
        self.assertEqual(param_cond_single.left, None)
        self.assertEqual(param_cond_single.right, None)
        self.assertEqual(param_cond_single.operator, ParameterConditionOperator.NONE)
        self.assertEqual(lst, [1, 2, 3])

    def test_check(self):
        """
        Test the check method.
        """
        # Test Parameter and direct value
        pbp = ParameterBoundProperty(1, int)
        pbp_param = ParameterBoundProperty("$a", int)
        param_cond = ParameterCondition(
            pbp, pbp_param, ParameterConditionOperator.EQUAL
        )
        self.assertTrue(param_cond.check({"a": IntegerParameter(1)}))
        self.assertFalse(param_cond.check({"a": IntegerParameter(2)}))

        # Test the operator chain
        condition_chain = ParameterCondition(
            param_cond, param_cond, OperatorChainOperator.AND
        )
        self.assertTrue(condition_chain.check({"a": IntegerParameter(1)}))
        self.assertFalse(condition_chain.check({"a": IntegerParameter(2)}))

        condition_chain = ParameterCondition(
            param_cond, param_cond, OperatorChainOperator.OR
        )
        self.assertTrue(condition_chain.check({"a": IntegerParameter(1)}))
        self.assertFalse(condition_chain.check({"a": IntegerParameter(2)}))

        param_cond_2 = ParameterCondition(
            pbp, pbp_param, ParameterConditionOperator.NOT_EQUAL
        )
        condition_chain = ParameterCondition(
            param_cond, param_cond_2, OperatorChainOperator.LEFT
        )
        self.assertTrue(condition_chain.check({"a": IntegerParameter(1)}))
        self.assertFalse(condition_chain.check({"a": IntegerParameter(2)}))

    def test_param_cond_ops(self):
        """
        Test all ParameterConditionOperators
        """
        pbp_a = ParameterBoundProperty(1, int)
        pbp_b = ParameterBoundProperty(2, int)
        pbp_c = ParameterBoundProperty(2, int)
        pbp_d = ParameterBoundProperty(3, int)

        param_cond_a = ParameterCondition(
            pbp_a, pbp_b, ParameterConditionOperator.EQUAL
        )
        param_cond_b = ParameterCondition(
            pbp_b, pbp_c, ParameterConditionOperator.EQUAL
        )
        param_cond_c = ParameterCondition(
            pbp_d, pbp_a, ParameterConditionOperator.EQUAL
        )
        self.assertFalse(param_cond_a.check({}))
        self.assertTrue(param_cond_b.check({}))
        self.assertFalse(param_cond_c.check({}))

        param_cond_a.operator = ParameterConditionOperator.NOT_EQUAL
        param_cond_b.operator = ParameterConditionOperator.NOT_EQUAL
        param_cond_c.operator = ParameterConditionOperator.NOT_EQUAL
        self.assertTrue(param_cond_a.check({}))
        self.assertFalse(param_cond_b.check({}))
        self.assertTrue(param_cond_c.check({}))

        param_cond_a.operator = ParameterConditionOperator.LESS_THAN
        param_cond_b.operator = ParameterConditionOperator.LESS_THAN
        param_cond_c.operator = ParameterConditionOperator.LESS_THAN
        self.assertTrue(param_cond_a.check({}))
        self.assertFalse(param_cond_b.check({}))
        self.assertFalse(param_cond_c.check({}))

        param_cond_a.operator = ParameterConditionOperator.LESS_THAN_OR_EQUAL
        param_cond_b.operator = ParameterConditionOperator.LESS_THAN_OR_EQUAL
        param_cond_c.operator = ParameterConditionOperator.LESS_THAN_OR_EQUAL
        self.assertTrue(param_cond_a.check({}))
        self.assertTrue(param_cond_b.check({}))
        self.assertFalse(param_cond_c.check({}))

        param_cond_a.operator = ParameterConditionOperator.GREATER_THAN
        param_cond_b.operator = ParameterConditionOperator.GREATER_THAN
        param_cond_c.operator = ParameterConditionOperator.GREATER_THAN
        self.assertFalse(param_cond_a.check({}))
        self.assertFalse(param_cond_b.check({}))
        self.assertTrue(param_cond_c.check({}))

        param_cond_a.operator = ParameterConditionOperator.GREATER_THAN_OR_EQUAL
        param_cond_b.operator = ParameterConditionOperator.GREATER_THAN_OR_EQUAL
        param_cond_c.operator = ParameterConditionOperator.GREATER_THAN_OR_EQUAL
        self.assertFalse(param_cond_a.check({}))
        self.assertTrue(param_cond_b.check({}))
        self.assertTrue(param_cond_c.check({}))

        param_cond_a.operator = ParameterConditionOperator.NONE
        param_cond_b.operator = ParameterConditionOperator.NONE
        param_cond_c.operator = ParameterConditionOperator.NONE
        self.assertTrue(param_cond_a.check({}))
        self.assertTrue(param_cond_b.check({}))
        self.assertTrue(param_cond_c.check({}))

    def test_param_cond_chain_ops(self):
        """
        Test all OperatorChainOperators
        """
        pbp_a = ParameterBoundProperty(1, int)
        pbp_b = ParameterBoundProperty(2, int)
        condition_true = ParameterCondition(
            pbp_a, pbp_b, ParameterConditionOperator.NOT_EQUAL
        )
        condition_false = ParameterCondition(
            pbp_a, pbp_b, ParameterConditionOperator.EQUAL
        )

        # AND
        condition_chain = ParameterCondition(
            condition_true, condition_false, OperatorChainOperator.AND
        )
        self.assertFalse(condition_chain.check({}))

        condition_chain = ParameterCondition(
            condition_true, condition_true, OperatorChainOperator.AND
        )
        self.assertTrue(condition_chain.check({}))

        condition_chain = ParameterCondition(
            condition_false, condition_false, OperatorChainOperator.AND
        )
        self.assertFalse(condition_chain.check({}))

        # OR
        condition_chain = ParameterCondition(
            condition_true, condition_false, OperatorChainOperator.OR
        )
        self.assertTrue(condition_chain.check({}))

        condition_chain = ParameterCondition(
            condition_false, condition_true, OperatorChainOperator.OR
        )
        self.assertTrue(condition_chain.check({}))

        condition_chain = ParameterCondition(
            condition_true, condition_true, OperatorChainOperator.OR
        )
        self.assertTrue(condition_chain.check({}))

        condition_chain = ParameterCondition(
            condition_false, condition_false, OperatorChainOperator.OR
        )
        self.assertFalse(condition_chain.check({}))

        # LEFT
        condition_chain = ParameterCondition(
            condition_true, condition_false, OperatorChainOperator.LEFT
        )
        self.assertTrue(condition_chain.check({}))

        condition_chain = ParameterCondition(
            condition_false, condition_true, OperatorChainOperator.LEFT
        )
        self.assertFalse(condition_chain.check({}))


if __name__ == "__main__":
    unittest.main()
