# LGPL-3.0 License
# Copyright (c) 2023 KIT-IAI-ESA

import unittest

from pyapi_rts.api.parameters.boolean_parameter import BooleanParameter
from pyapi_rts.api.parameters.integer_parameter import IntegerParameter
from pyapi_rts.api.parameters.float_parameter import FloatParameter
from pyapi_rts.api.parameters.string_parameter import StringParameter
from pyapi_rts.api.parameters.name_parameter import NameParameter


class ParameterTest(unittest.TestCase):
    """
    Tests for the different parameter classes
    """

    def test_boolean_parameter(self):
        """
        Tests the BooleanParameter class
        """
        bool_param = BooleanParameter("bool_param", True)
        self.assertEqual(bool_param.get_value(), True)
        bool_param.set_value(False)
        self.assertEqual(bool_param.get_value(), False)
        bool_param.set_value(1)
        self.assertEqual(bool_param.get_value(), False)
        bool_param.set_str("True")
        self.assertEqual(bool_param.get_value(), True)
        self.assertEqual(str(bool_param), "True")

    def test_float_parameter(self):
        """
        Tests the FloatParameter class
        """
        float_param = FloatParameter("float_param", 1.0)
        self.assertEqual(float_param.get_value(), 1.0)
        float_param.set_value(2)
        self.assertEqual(float_param.get_value(), 2.0)
        float_param.set_str("1.5")
        self.assertEqual(float_param.get_value(), 1.5)
        float_param.set_str("abc")
        self.assertEqual(float_param.get_value(), 1.5)
        self.assertEqual(str(float_param), "1.5")

    def test_integer_parameter(self):
        """
        Tests the IntegerParameter class
        """
        integer_param = IntegerParameter("integer_param", 1)
        self.assertEqual(integer_param.get_value(), 1)
        self.assertTrue(integer_param.set_value(2))
        self.assertEqual(integer_param.get_value(), 2)
        self.assertFalse(integer_param.set_str("1.5"))
        self.assertEqual(integer_param.get_value(), 2)
        integer_param.set_str("abc")
        self.assertEqual(integer_param.get_value(), 2)
        self.assertEqual(str(integer_param), "2")

    def test_name_parameter(self):
        """
        Tests the NameParameter class
        """
        name_param = NameParameter("name_param", "name")
        self.assertEqual(name_param.get_value(), "name")
        self.assertTrue(name_param.set_value("name2"))
        self.assertEqual(name_param.get_value(), "name2")
        self.assertFalse(name_param.set_str(1))
        self.assertEqual(name_param.get_value(), "name2")
        self.assertEqual(str(name_param), "name2")

    def test_string_parameter(self):
        """
        Tests the StringParameter class
        """
        string_param = StringParameter("string_param", "string")
        self.assertEqual(string_param.get_value(), "string")
        self.assertTrue(string_param.set_value("string2"))
        self.assertEqual(string_param.get_value(), "string2")
        self.assertTrue(string_param.set_value(1))
        self.assertEqual(string_param.get_value(), "1")
        self.assertEqual(str(string_param), "1")


if __name__ == "__main__":
    unittest.main()
