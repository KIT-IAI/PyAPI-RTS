# LGPL-3.0 License
# Copyright (c) 2023 KIT-IAI-ESA

import pathlib
import unittest
from pyapi_rts.class_extractor.main import (
    read_file,
    read_component_dir,
    reverse_dictionary,
    read_component_tags,
)

PATH = pathlib.Path(__file__).parent.resolve()


class ExtractorTestCase(unittest.TestCase):
    """
    Tests for the ClassExtractor module
    """

    def test_read_file_bus(self):
        """
        Checks if the BUS component is read correctly
        """
        component, enums = read_file(
            PATH / "component_builder_files/test" / "BUS_TEST", {}
        )
        self.assertEqual(component.type_name, "BUSTEST")
        self.assertEqual(len(component.parameters), 1)
        self.assertEqual(len(component.collections), 2)
        self.assertEqual(len(enums), 2)
        self.assertIsNotNone(component.rectangle)

        self.assertEqual(component.parameters[0].name, "DOCUMENT")
        self.assertEqual(component.parameters[0]._type, "DocumentEnumParameter")

        self.assertEqual(enums[1]._type, "ScolEnumParameter")
        self.assertEqual(enums[0]._type, "DocumentEnumParameter")
        self.assertSetEqual(set(enums[0].options), set(["YES", "NO"]))

    def test_read_buslabel(self):
        """
        Checks if the BUSLABEL component is read correctly
        """
        component, enums = read_file(
            PATH / "component_builder_files/test" / "BUSLABEL_TEST", {}
        )
        self.assertEqual(component.type_name, "BUSLABELTEST")
        self.assertEqual(len(component.parameters), 0)
        self.assertEqual(len(component.collections), 5)
        self.assertEqual(component.name_parameter_key, "BName")
        self.assertEqual(len(enums), 16)
        self.assertIsNotNone(component.rectangle)

        self.assertEqual(component.collections[0].name, "HIDDENPARAMETERS")

        self.assertEqual(len(enums[0].options), 14)
        self.assertEqual(enums[0].name, "COL")

    def test_read_component_dir(self):
        """
        Checks if the component directory is read correctly
        """
        components_read = read_component_dir(PATH / "component_builder_files", {})
        self.assertEqual(len(components_read), 2)

        i = 0 if components_read[0][0].type_name == "BUSLABELTEST" else 1

        self.assertEqual(components_read[i][0].type_name, "BUSLABELTEST")
        self.assertEqual(components_read[1 - i][0].type_name, "BUSTEST")
        self.assertEqual(len(components_read[i][1]), 16)
        self.assertEqual(len(components_read[1 - i][1]), 2)

    def test_reverse_dictionary(self):
        """
        Checks if the reverse dictionary is created correctly
        """
        dictionary = {
            "A": ["1", "2"],
            "B": ["3", "1"],
            "C": ["1", "4", "5"],
        }
        rev = reverse_dictionary(dictionary)
        self.assertEqual(rev["1"], ["A", "B", "C"])
        self.assertEqual(rev["2"], ["A"])
        self.assertEqual(rev["3"], ["B"])
        self.assertEqual(rev["4"], ["C"])
        self.assertEqual(rev["5"], ["C"])

        self.assertEqual(reverse_dictionary({}), {})
        self.assertEqual(reverse_dictionary({"A": []}), {})

    def test_component_tags(self):
        """
        _summary_
        """
        tag_dict = read_component_tags(str(PATH / "component_tags.txt"))
        self.assertEqual(tag_dict["wirelabel"], ["connecting", "hierarchy_connecting"])
        self.assertEqual(tag_dict["bus"], ["connecting"])
        self.assertEqual(tag_dict["buslabel"], ["connecting"])
        self.assertEqual(tag_dict["wire"], ["connecting"])


if __name__ == "__main__":
    unittest.main()
