# LGPL-3.0 License
# Copyright (c) 2023 KIT-IAI-ESA

from enum import Enum
import unittest
from pyapi_rts.api.parameters.enum_parameter import EnumParameter
from pyapi_rts.api.parameters.parameter import Parameter

from pyapi_rts.shared import (
    ParameterBoundProperty,
)
from pyapi_rts.api.parameters.integer_parameter import IntegerParameter


class ParameterBoundPropertyTestEnum(Enum):
    """
    An enum for testing ParameterBoundProperty.
    """

    A = 1
    B = 2
    C = 3


class ParameterBoundPropertyTest(unittest.TestCase):
    """
    Tests for the ParameterBoundProperty class
    """

    def test_init(self):
        """
        Tests the initialization of the class
        """
        pbp = ParameterBoundProperty(1, int)
        self.assertEqual(pbp.get_value({}), 1)
        self.assertEqual(pbp.get_direct_value(), 1)
        self.assertEqual(str(pbp), "ParameterBoundProperty(1,int)")

    def test_get_set(self):
        """
        Tests the get and set methods
        """
        pbp = ParameterBoundProperty(1, int)
        pbp.set_value("2")
        self.assertNotEqual(pbp.get_value({}), 2)
        self.assertEqual(pbp.get_value({}), 1)
        self.assertEqual(pbp.get_direct_value(), 1)
        pbp.set_value((int)(2))
        self.assertEqual(pbp.get_value({}), 2)
        self.assertEqual(pbp.get_direct_value(), 2)

    def test_addition(self):
        """
        Tests the addition syntax $(a + b)
        """
        pbp = ParameterBoundProperty("$(a + b)", int)
        self.assertEqual(
            pbp.get_value(
                {"a": IntegerParameter(1), "b": IntegerParameter(2)}
            ),
            3,
        )
        self.assertEqual(
            pbp.get_value(
                {"a": IntegerParameter(1), "b": IntegerParameter(2)}
            ),
            3,
        )
        self.assertEqual(pbp.get_value({}), 0)
        self.assertEqual(pbp.get_direct_value(), "$(a + b)")

        pbp = ParameterBoundProperty("$(a + b + c)", int)
        self.assertEqual(
            pbp.get_value(
                {
                    "a": IntegerParameter(1),
                    "b": IntegerParameter(2),
                    "c": IntegerParameter(3),
                }
            ),
            6,
        )
        self.assertEqual(pbp.get_value({}), 0)
        self.assertEqual(pbp.get_direct_value(), "$(a + b + c)")

    def test_subtraction(self):
        """
        Tests the subtraction syntax $(a - b)
        """
        pbp = ParameterBoundProperty("$(a - b)", int)
        self.assertEqual(
            pbp.get_value(
                {"a": IntegerParameter(1), "b": IntegerParameter(2)}
            ),
            -1,
        )
        self.assertEqual(
            pbp.get_value(
                {"a": IntegerParameter(1), "b": IntegerParameter(2)}
            ),
            -1,
        )
        self.assertEqual(pbp.get_value({}), 0)
        self.assertEqual(pbp.get_direct_value(), "$(a - b)")

        pbp = ParameterBoundProperty("$(a - b - c)", int)
        self.assertEqual(
            pbp.get_value(
                {
                    "a": IntegerParameter(1),
                    "b": IntegerParameter(2),
                    "c": IntegerParameter(3),
                }
            ),
            -4,
        )
        self.assertEqual(pbp.get_value({}), 0)
        self.assertEqual(pbp.get_direct_value(), "$(a - b - c)")

    def test_multiplication(self):
        """
        Tests the multiplication syntax $(a * b)
        """
        pbp = ParameterBoundProperty("$(a * b)", int)
        self.assertEqual(
            pbp.get_value(
                {"a": IntegerParameter(1), "b": IntegerParameter(2)}
            ),
            2,
        )
        self.assertEqual(
            pbp.get_value(
                {"a": IntegerParameter(1), "b": IntegerParameter(2)}
            ),
            2,
        )
        self.assertEqual(pbp.get_value({}), 0)
        self.assertEqual(pbp.get_direct_value(), "$(a * b)")

        pbp = ParameterBoundProperty("$(a * b * c)", int)
        self.assertEqual(
            pbp.get_value(
                {
                    "a": IntegerParameter(1),
                    "b": IntegerParameter(2),
                    "c": IntegerParameter(3),
                }
            ),
            6,
        )
        self.assertEqual(pbp.get_value({}), 0)
        self.assertEqual(pbp.get_direct_value(), "$(a * b * c)")

    def test_brackets(self):
        """
        Tests the bracket syntax
        """
        dictionary = {
            "a": IntegerParameter(1),
            "b": IntegerParameter(2),
            "c": IntegerParameter(3),
        }
        pbp = ParameterBoundProperty("$(a - b - c)", int)
        self.assertEqual(pbp.get_value(dictionary), -4)
        pbp = ParameterBoundProperty("$(a - (b - c))", int)
        self.assertEqual(pbp.get_value(dictionary), 2)
        pbp = ParameterBoundProperty("$((a - b) - c)", int)
        self.assertEqual(pbp.get_value(dictionary), -4)

    def test_resolve(self):
        """
        Tests the resolving of parameters
        """
        pbp = ParameterBoundProperty("$abc", int)
        self.assertEqual(pbp.get_value({"abc": IntegerParameter(1)}), 1)
        self.assertEqual(pbp.get_value({"abc": IntegerParameter(1)}), 1)
        self.assertEqual(
            pbp.get_value(
                {"abc": IntegerParameter(1), "def": IntegerParameter(2)}
            ),
            1,
        )
        self.assertEqual(pbp.get_value({}), 0)
        self.assertEqual(pbp.get_direct_value(), "$abc")

    def test_enum(self):
        """
        Tests the resolving of an enum index
        """
        pbp = ParameterBoundProperty("$abc", ParameterBoundPropertyTestEnum)
        self.assertEqual(
            pbp.get_value({"abc": EnumParameter[ParameterBoundPropertyTestEnum](ParameterBoundPropertyTestEnum.A)}),
            0,
        )
        self.assertEqual(
            pbp.get_value({"abc": EnumParameter[ParameterBoundPropertyTestEnum](ParameterBoundPropertyTestEnum.B)}),
            1,
        )
        pbp = ParameterBoundProperty("$(a + b)", ParameterBoundPropertyTestEnum)
        self.assertEqual(
            pbp.get_value(
                {
                    "a": EnumParameter[ParameterBoundPropertyTestEnum](ParameterBoundPropertyTestEnum.B),
                    "b": EnumParameter[ParameterBoundPropertyTestEnum](ParameterBoundPropertyTestEnum.C),
                }
            ),
            3,
        )


if __name__ == "__main__":
    unittest.main()
