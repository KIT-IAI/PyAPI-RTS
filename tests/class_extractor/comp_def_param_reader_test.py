# LGPL-3.0 License
# Copyright (c) 2023 KIT-IAI-ESA

import unittest

from pyapi_rts.class_extractor.readers.lines.comp_def_parameter_reader import CompDefParameterReader


class CompDefParameterReaderTest(unittest.TestCase):
    """
    Tests for the CompDefParameterReader class.
    """

    def test_read_parameter(self):
        """
        Tests the reading of a parameter.
        """
        reader = CompDefParameterReader()
        reader.read_line(
            r'LW1  "Bus thickness (Single Phase)"         "" 5 REAL 3.0 0.0'
        )
        self.assertEqual(reader.results["parameter"][0].key, "LW1")
        self.assertEqual(
            reader.results["parameter"][0].description, "Bus thickness (Single Phase)"
        )
        self.assertEqual(reader.results["parameter"][0].desc_valid, "")
        self.assertEqual(reader.results["parameter"][0].mystery, "5")
        self.assertEqual(reader.results["parameter"][0]._type, "REAL")
        self.assertEqual(reader.results["parameter"][0].default, "3.0")
        self.assertEqual(reader.results["parameter"][0].minimum, "0.0")
        self.assertEqual(reader.results["parameter"][0].maximum, "")

        reader.read_line(r'x1 "x1"  " " 4 INTEGER -32 0 0 false')
        self.assertEqual(reader.results["parameter"][1].key, "x1")
        self.assertEqual(reader.results["parameter"][1].description, "x1")
        self.assertEqual(reader.results["parameter"][1].desc_valid, " ")
        self.assertEqual(reader.results["parameter"][1].mystery, "4")
        self.assertEqual(reader.results["parameter"][1]._type, "INTEGER")
        self.assertEqual(reader.results["parameter"][1].default, "-32")
        self.assertEqual(reader.results["parameter"][1].minimum, "0")
        self.assertEqual(reader.results["parameter"][1].maximum, "0")

        with self.assertRaises(ValueError):
            reader.read_line("invalid")
        self.assertEqual(len(reader.results["parameter"]), 2)


if __name__ == "__main__":
    unittest.main()
