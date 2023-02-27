# LGPL-3.0 License
# Copyright (c) 2023 KIT-IAI-ESA

import os
import pathlib
import unittest

from pyapi_rts.api.lark.rlc_tline import RLCTLine

PATH = pathlib.Path(__file__).parent.absolute().resolve()


class RLCTlineTest(unittest.TestCase):
    """
    Tests for the RLCTline class
    """

    def test_init(self):
        """Initialize RLCTline with valid default values."""
        rlc_tline = RLCTLine("tline_name")
        self.assertEqual(rlc_tline.num_phases, 3)
        self.assertEqual(rlc_tline.frequency, 50.0)

    def test_from_file(self):
        """Create an RLCTline object from a .tli file."""
        rlc_tline = RLCTLine.from_file(PATH / "tline.tli")

        self.assertEqual(rlc_tline.length, 23.0)
        rlc_tline.length = 24.0
        self.assertEqual(rlc_tline.length, 24.0)

        self.assertEqual(rlc_tline.frequency, 50.0)
        rlc_tline.frequency = 60.0
        self.assertEqual(rlc_tline.frequency, 60.0)

        self.assertEqual(rlc_tline.ground_resistivity, 100.0)
        rlc_tline.ground_resistivity = 200.0
        self.assertEqual(rlc_tline.ground_resistivity, 200.0)

        self.assertEqual(rlc_tline.r1, 0.03)
        rlc_tline.r1 = 0.1
        self.assertEqual(rlc_tline.r1, 0.1)

        self.assertEqual(rlc_tline.r0, 0.09)
        rlc_tline.r0 = 0.1
        self.assertEqual(rlc_tline.r0, 0.1)

        self.assertEqual(rlc_tline.xind0, 0.895)
        rlc_tline.xind0 = 0.9
        self.assertEqual(rlc_tline.xind0, 0.9)

        self.assertEqual(rlc_tline.xind1, 0.25)
        rlc_tline.xind1 = 0.9
        self.assertEqual(rlc_tline.xind1, 0.9)

        self.assertEqual(rlc_tline.xcap1, 0.23)
        rlc_tline.xcap1 = 0.9
        self.assertEqual(rlc_tline.xcap1, 0.9)

        self.assertEqual(rlc_tline.xcap0, 0.23)
        rlc_tline.xcap0 = 0.9
        self.assertEqual(rlc_tline.xcap0, 0.9)

        self.assertEqual(rlc_tline.num_phases, 6)
        with self.assertRaises(ValueError):
            rlc_tline.num_phases = 5
        rlc_tline.num_phases = 3
        self.assertEqual(rlc_tline.num_phases, 3)

        self.assertEqual(rlc_tline.transposed, True)
        rlc_tline.transposed = False
        self.assertEqual(rlc_tline.transposed, False)

        self.assertEqual(rlc_tline.mutual_resistance, 0.162)
        rlc_tline.mutual_resistance = 0.2
        self.assertEqual(rlc_tline.mutual_resistance, 0.2)

        self.assertEqual(rlc_tline.mutual_reactance, 0.781)
        rlc_tline.mutual_reactance = 0.9
        self.assertEqual(rlc_tline.mutual_reactance, 0.9)

        with self.assertRaises(ValueError):
            RLCTLine.from_file(PATH / "tline_invalid.tli")

        with self.assertRaises(ValueError):
            RLCTLine.from_file(PATH / "tline_not_ohms.tli")

    def test_write_file(self):
        """Write contents of an RLCTline object to file."""
        FILE_NAME = "tline_name"
        rlc_tline = RLCTLine(FILE_NAME)
        rlc_tline.r1 = 1.0
        self.assertTrue(rlc_tline.write_file(PATH))

        rlc_tline_read = RLCTLine.from_file(PATH / f"{FILE_NAME}.tli")
        self.assertEqual(rlc_tline_read.r1, 1.0)

        if os.path.exists(PATH / f"{FILE_NAME}.tli"):
            os.remove(PATH / f"{FILE_NAME}.tli")


if __name__ == "__main__":
    unittest.main()
