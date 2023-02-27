# LGPL-3.0 License
# Copyright (c) 2023 KIT-IAI-ESA

import unittest

from pyapi_rts.class_extractor.readers.blocks.base_block_reader import BaseBlockReader
from tests.class_extractor.TestReaders import (
    ExampleBlockReader,
    ExampleLineReader,
)


class BaseBlockReaderTest(unittest.TestCase):
    """
    Tests for the BaseBlockReader class.
    """

    def test_init(self):
        """
        Tests the initialization of the class.
        """
        c_block = BaseBlockReader()
        self.assertEqual(c_block.blocks, [])
        self.assertEqual(c_block.line_readers, [])
        self.assertEqual(c_block.reg.pattern, r"^[A-Z-_]+:(.*)\n?$")
        self.assertEqual(c_block.results, {})

    def test_line_reader(self):
        """
        Tests the usage of the line_readers.
        """
        c_block = BaseBlockReader()
        c_block.line_readers.append(ExampleLineReader())

        self.assertEqual(c_block.line_readers[0].reg.pattern, r"^INT:\s+(\d+)\n?$")
        self.assertEqual(c_block.line_readers[0].results, {"int": []})
        c_block.read(["", "INT: 1", "", "INT 2.3", "INT: 2", "INT: 3"])
        self.assertEqual(c_block.results, {"int": [1, 2, 3]})

    def test_blocks(self):
        """
        Tests the usage of the blocks.
        """
        c_block = BaseBlockReader()
        c_block.blocks.append(ExampleBlockReader())
        self.assertEqual(c_block.blocks[0].reg.pattern, r"^BLOCK:\n?$")

        c_block.read(
            [
                "",
                "BLOCK:",
                "    INT: 1",
                "",
                "    BLOCK:",
                "        INT: 2",
                "",
                "    BLOCK:",
                "        nothing",
            ]
        )
        self.assertEqual(c_block.blocks[0].results, {"int": [1]})
        self.assertEqual(c_block.results, {})

    def test_whitespace_counter(self):
        """
        Tests for the __whitespaceLeft(line) method.
        """
        c_block = BaseBlockReader()
        self.assertEqual(c_block._whitespace_left(""), 0)
        self.assertEqual(c_block._whitespace_left(" "), 1)
        self.assertEqual(c_block._whitespace_left("  "), 2)
        self.assertEqual(c_block._whitespace_left("   "), 3)
        self.assertEqual(c_block._whitespace_left("    "), 4)

        self.assertEqual(c_block._whitespace_left("\t"), 4)
        self.assertEqual(c_block._whitespace_left("\t\t"), 8)
        self.assertEqual(c_block._whitespace_left("\t\t\t"), 12)
        self.assertEqual(c_block._whitespace_left("\t "), 5)
        self.assertEqual(c_block._whitespace_left("\t  "), 6)

    def test_strip_left(self):
        """
        Tests the __strip_left(line, amount) method.
        """
        c_block = BaseBlockReader()
        self.assertEqual(c_block._strip_left("", 0), "")
        self.assertEqual(c_block._strip_left("", 1), "")
        self.assertEqual(c_block._strip_left("  ", 1), " ")
        self.assertEqual(c_block._strip_left("  ", 2), "")
        self.assertEqual(c_block._strip_left("     ", 4), " ")
        self.assertEqual(c_block._strip_left("\t", 2), "  ")
        self.assertEqual(c_block._strip_left("\t ", 4), " ")
        self.assertEqual(c_block._strip_left(" \t", 2), "  ")
        self.assertEqual(c_block._strip_left("  \t ", 2), "   ")


if __name__ == "__main__":
    unittest.main()
