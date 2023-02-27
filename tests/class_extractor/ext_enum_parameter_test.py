# LGPL-3.0 License
# Copyright (c) 2023 KIT-IAI-ESA

import unittest

from pyapi_rts.class_extractor.extracted.ext_enum_parameter import ExtEnumParameter


class ExtEnumParameterTest(unittest.TestCase):
    """
    Tests the ExtEnumParameter class.
    """

    def test_init(self):
        """
        Tests the initialization of the ExtEnumParameter class.
        """
        ext_enum_param = ExtEnumParameter("testname")
        self.assertEqual(ext_enum_param.name, "testname")
        self.assertEqual(ext_enum_param.options, [])
        self.assertEqual(ext_enum_param.enum_type, "TestnameEnumParameter")

    def test_eq(self):
        """
        Tests the equality operator
        """
        ext_enum_param = ExtEnumParameter("testname")
        ext_enum_param2 = ExtEnumParameter("testname2")
        self.assertEqual(ext_enum_param, ext_enum_param2)

        ext_enum_param.options.append("test")
        self.assertNotEqual(ext_enum_param, ext_enum_param2)

        ext_enum_param2.options.append("test")
        self.assertEqual(ext_enum_param, ext_enum_param2)

    def test_options_hash(self):
        """
        Tests the options_hash property
        """
        ext_enum_param = ExtEnumParameter("testname")
        ext_enum_param2 = ExtEnumParameter("testname2")
        self.assertEqual(ext_enum_param.options_hash, ext_enum_param2.options_hash)

        ext_enum_param.options.append("test")
        self.assertNotEqual(ext_enum_param.options_hash, ext_enum_param2.options_hash)

        ext_enum_param2.options.append("test")
        self.assertEqual(ext_enum_param.options_hash, ext_enum_param2.options_hash)

        ext_enum_param.options.append("test2")
        ext_enum_param.options.append("test3")
        ext_enum_param.options.append("test3")
        ext_enum_param.options.append("test2")
        self.assertNotEqual(ext_enum_param.options_hash, ext_enum_param2.options_hash)


if __name__ == "__main__":
    unittest.main()
