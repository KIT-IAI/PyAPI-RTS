# LGPL-3.0 License
# Copyright (c) 2023 KIT-IAI-ESA

import pathlib
import unittest

import lark

from pyapi_rts.class_extractor.readers.blocks.computation_transformer import (
    ComputationTransformer,
)

PATH = pathlib.Path(__file__).parent.absolute()


class ComputationTransformerTest(unittest.TestCase):
    """
    Class to test the computation transformer.
    """

    def test_computation_transformer(self):
        """
        Test the computation transformer.
        """
        transformer = ComputationTransformer()
        parser = lark.Lark(
            pathlib.Path(
                PATH / "../../pyapi_rts/class_extractor/readers/blocks/computations.lark"
            ).read_text(),
            parser="earley",
        )
        test_computation = "STRING name = name2"
        self.assertEqual(
            transformer.transform(parser.parse(test_computation)),
            ("name", "str", "$name2"),
        )

        test_computation = 'STRING name = "name2"'
        self.assertEqual(
            transformer.transform(parser.parse(test_computation)),
            ("name", "str", '"name2"'),
        )

        test_computation_condition = "INTEGER name = name2<2 ? 1 : 0"
        self.assertEqual(
            transformer.transform(parser.parse(test_computation_condition)),
            ("name", "int", "1.0 if ($name2 < 2.0) else 0.0"),
        )

        test_computation_brackets = "INTEGER name = 5 + (4 * (3 - 2))"
        self.assertEqual(
            transformer.transform(parser.parse(test_computation_brackets)),
            ("name", "int", "5.0 + (4.0 * (3.0 - 2.0))"),
        )

        test_computation_brackets = "INTEGER name = (1=1&2>1) ? 1 : 0"
        self.assertEqual(
            transformer.transform(parser.parse(test_computation_brackets)),
            ("name", "int", "1.0 if ((1.0 == 1.0) and (2.0 > 1.0)) else 0.0"),
        )

        test_computation_brackets = "INTEGER name = 1 << 2"
        self.assertEqual(
            transformer.transform(parser.parse(test_computation_brackets)),
            ("name", "int", "(int)(1.0) << (int)(2.0)"),
        )

        test_computation_brackets = "INTEGER name = (1 << 2) + (1 << 2) + (1 << 2) + 3"
        self.assertEqual(
            transformer.transform(parser.parse(test_computation_brackets)),
            (
                "name",
                "int",
                "((int)(1.0) << (int)(2.0)) + ((int)(1.0) << (int)(2.0)) + ((int)(1.0) << (int)(2.0)) + 3.0",
            ),
        )


if __name__ == "__main__":
    unittest.main()
