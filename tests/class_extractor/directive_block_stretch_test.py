# LGPL-3.0 License
# Copyright (c) 2023 KIT-IAI-ESA

import unittest

from pyapi_rts.class_extractor.readers.blocks.directives_block import (
    DirectivesBlock,
    Stretchable,
)


class DirectiveBlockTest(unittest.TestCase):
    """
    Tests for the classes in the DirectivesBlock file.
    """

    def test_directive_block(self):
        """
        Tests the DirectivesBlock class and StretchableLineReader.
        """
        dir_block = DirectivesBlock()
        self.assertEqual(
            dir_block.results, {"stretchable": [], "linked": [], "name": []}
        )

        dir_block.read(
            [
                "#DIRECTIVES:",
                "DOCUMENT = $DOCUMENT",
                r'DOCUMENT_SECTION("HIDDEN PARAMETERS") = false"',
                "STRETCHABLE = STRETCHABLE_UP_DOWN_LINE",
            ]
        )
        self.assertEqual(len(dir_block.results["stretchable"]), 1)
        self.assertEqual(dir_block.results["stretchable"][0], Stretchable.UP_DOWN)

        dir_block.read(
            [
                "#DIRECTIVES:",
                "DOCUMENT = $DOCUMENT",
                r'DOCUMENT_SECTION("HIDDEN PARAMETERS") = false"',
                "STRETCHABLE = STRETCHABLE_BOX",
            ]
        )
        self.assertEqual(len(dir_block.results["stretchable"]), 2)
        self.assertEqual(dir_block.results["stretchable"][1], Stretchable.BOX)

    def test_name(self):
        """
        Tests the NameLine reader.
        """
        dir_block = DirectivesBlock()
        self.assertEqual(
            dir_block.results, {"stretchable": [], "linked": [], "name": []}
        )
        dir_block.read(
            [
                "#DIRECTIVES:",
                "DOCUMENT = $DOCUMENT",
                r'DOCUMENT_SECTION("HIDDEN PARAMETERS") = false"',
                "STRETCHABLE = STRETCHABLE_BOX",
                "NAME = Test",
            ]
        )
        self.assertEqual(len(dir_block.results["name"]), 1)
        self.assertEqual(dir_block.results["name"][0], "Test")

    def test_linked(self):
        """
        Tests the LINKED_COMPONENT line
        """
        dir_block = DirectivesBlock()
        self.assertEqual(
            dir_block.results, {"stretchable": [], "linked": [], "name": []}
        )
        dir_block.read(
            [
                "#DIRECTIVES:",
                "DOCUMENT = $DOCUMENT",
                r'DOCUMENT_SECTION("HIDDEN PARAMETERS") = false"',
                "LINKED_COMPONENT=TRUE",
                "NAME = Test",
            ]
        )
        self.assertEqual(len(dir_block.results["linked"]), 1)
        self.assertTrue(dir_block.results["linked"][0])

if __name__ == "__main__":
    unittest.main()
