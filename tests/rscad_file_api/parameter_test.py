# LGPL-3.0 License
# Copyright (c) 2023 KIT-IAI-ESA

import unittest

from pyapi_rts.api.parameters.integer_parameter import IntegerParameter
from pyapi_rts.api.parameters.float_parameter import FloatParameter
from pyapi_rts.api.parameters.string_parameter import StringParameter
from pyapi_rts.api.parameters.name_parameter import NameParameter


class ParameterTest(unittest.TestCase):
    """
    Tests for the different parameter classes
    """

    def test_float_parameter(self):
        """
        Tests the FloatParameter class
        """
        float_param = FloatParameter(1.0)
        self.assertEqual(float_param.value, 1.0)
        float_param.value = 2
        self.assertEqual(float_param.value, 2.0)
        float_param.set_str("1.5")
        self.assertEqual(float_param.value, 1.5)
        with self.assertRaises(ValueError):
            float_param.set_str("abc")
        self.assertEqual(float_param.value, 1.5)
        self.assertEqual(str(float_param), "1.5")
        self.assertEqual(float_param.default, 1.0)

    def test_integer_parameter(self):
        """
        Tests the IntegerParameter class
        """
        integer_param = IntegerParameter(1)
        self.assertEqual(integer_param.value, 1)
        integer_param.value = 2
        self.assertEqual(integer_param.value, 2)
        with self.assertRaises(ValueError):
            self.assertFalse(integer_param.set_str("1.5"))
        self.assertEqual(integer_param.value, 2)
        with self.assertRaises(ValueError):
            integer_param.set_str("abc")
        self.assertEqual(integer_param.value, 2)
        self.assertEqual(str(integer_param), "2")

    def test_name_parameter(self):
        """
        Tests the NameParameter class
        """
        name_param = NameParameter("name")
        self.assertEqual(name_param.value, "name")
        name_param.value = "name2"
        self.assertEqual(name_param.value, "name2")
        with self.assertRaises(TypeError):
            name_param.set_str(1)
        self.assertEqual(name_param.value, "name2")
        self.assertEqual(str(name_param), "name2")

    def test_string_parameter(self):
        """
        Tests the StringParameter class
        """
        string_param = StringParameter("string")
        self.assertEqual(string_param.value, "string")
        string_param.value = "string2"
        self.assertEqual(string_param.value, "string2")
        string_param.value = 1
        self.assertEqual(string_param.value, "1")
        self.assertEqual(str(string_param), "1")


if __name__ == "__main__":
    unittest.main()
