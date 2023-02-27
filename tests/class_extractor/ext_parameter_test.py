# LGPL-3.0 License
# Copyright (c) 2023 KIT-IAI-ESA

import unittest
from pyapi_rts.class_extractor.extracted.ext_parameter import ExtParameter


class ExtParameterTest(unittest.TestCase):
    """
    Tests for the ExtParameter class.
    """

    def test_init(self):
        """
        Tests the initialization of the ExtParameter class.
        """
        ext_param = ExtParameter("key", "name", "type", "default", "desc")
        self.assertEqual(ext_param.key, "key")
        self.assertEqual(ext_param.name, "name")
        self.assertEqual(ext_param.comp_type, "type")
        self.assertEqual(ext_param.default, "default")
        self.assertEqual(ext_param.description, "desc")

    def test_forbidden_name(self):
        """
        Tests the renaming of names that are forbidden by Python.
        """
        ext_param = ExtParameter("key", "del", "type", "desc")
        self.assertEqual(ext_param.name, "_del")


if __name__ == "__main__":
    unittest.main()
