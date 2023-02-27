# LGPL-3.0 License
# Copyright (c) 2023 KIT-IAI-ESA

import unittest

from pyapi_rts.class_extractor.readers.blocks.computations_block import ComputationsBlock


class ComputationsBlockTest(unittest.TestCase):
    """
    Tests the computation block class.
    """

    def test_computation_block(self):
        """
        Tests a simple computation block.
        """
        comp_block = ComputationsBlock()
        comp_block.read(["COMPUTATIONS:", "  INTEGER int = 0"])
        self.assertEqual(comp_block.results["computations"], [("int", "int", "0.0")])

    def test_multi_comp_block(self):
        """
        Tests Computation Blocks with multiple computations.
        """
        comp_block = ComputationsBlock()
        comp_block.read(
            ["COMPUTATIONS:", "  INTEGER int = 0", "  INTEGER cond = int=0 ? 0 : 1"]
        )
        self.assertEqual(
            comp_block.results["computations"],
            [
                ("int", "int", "0.0"),
                ("cond", "int", '0.0 if (self.get_by_key("int", 1, True) == 0.0) else 1.0'),
            ],
        )

    def test_test(self):
        comp_block = ComputationsBlock()
        comp_block.read(["COMPUTATIONS:", "  INTEGER loadunit  = 24 + ld1 + ld2"])
        self.assertEqual(
            comp_block.results["computations"],
            [
                (
                    "loadunit",
                    "int",
                    '24.0+self.get_by_key("ld1", 1, True)+self.get_by_key("ld2", 1, True)',
                )
            ],
        )

    def test_get_special(self):
        """
        Tests the get_special method.
        """
        comp_block = ComputationsBlock()
        comp_block.read(["COMPUTATIONS:", "  INTEGER int = $TEST"])
        self.assertEqual(
            comp_block.results["computations"],
            [("int", "int", 'self.get_special_value("TEST")')],
        )

    def test_apostrophe(self):
        """
        Tests the evaluation with an apostrophe in the computation name.
        """
        comp_block = ComputationsBlock()
        comp_block.read(["COMPUTATIONS:", "  INTEGER int' = 0"])
        self.assertEqual(comp_block.results["computations"], [("int'", "int", "0.0")])


if __name__ == "__main__":
    unittest.main()
