# LGPL-3.0 License
# Copyright (c) 2023 KIT-IAI-ESA

import unittest

from pyapi_rts.class_extractor.extracted.ext_component import ExtComponent
from pyapi_rts.class_extractor.extracted.ext_parameter import ExtParameter
from pyapi_rts.class_extractor.extracted.ext_parameter_coll import ExtParameterColl


class ExtComponentTest(unittest.TestCase):
    """
    Tests for the ExtComponent class.
    """

    def test_init(self):
        """
        Tests the initialization of the ExtComponent class.
        """
        ext_comp = ExtComponent()
        self.assertEqual(ext_comp.type_name, "Component")
        self.assertEqual(ext_comp.collections, [])
        self.assertEqual(ext_comp.parameters, [])
        self.assertEqual(ext_comp.rectangle, None)

    def test_type_name(self):
        """
        Tests the type_name property.
        """
        ext_comp = ExtComponent()
        ext_comp.set_type("Test")
        self.assertEqual(ext_comp.type_name, "Test")


if __name__ == "__main__":
    unittest.main()
