# LGPL-3.0 License
# Copyright (c) 2023 KIT-IAI-ESA

import unittest

from pyapi_rts.api.internals.block import Block
from pyapi_rts.api.group import Group


class GroupTest(unittest.TestCase):
    """
    Tests for the Group class.
    """

    def test_group(self):
        """
        Tests the group reader.
        """
        test_case = [
            "GROUP-START:",
            "COMPONENT_TYPE=GROUP",
            "	784 464 0 0 0",
            "COMPONENT_TYPE=BUS",
            "	1136 464 1 0 7",
            "	PARAMETERS-START:",
            "	LW1	:3.0",
            "	SCOL	:BLACK",
            "	DOCUMENT	:NO",
            "	x1	:-32",
            "	y1	:0",
            "	x2	:32",
            "	y2	:0",
            "	PARAMETERS-END:",
            "	ENUMERATION:",
            "		true",
            "		0",
            "		Integer",
            "		#",
            "GROUP-END:",
        ]
        group = Group()
        group.read_block(Block(test_case))

        self.assertEqual(group.type, "GROUP")
        self.assertEqual(group.get_components()[0].type, "BUS")
        self.assertEqual(group.get_components()[0].get_by_key("LW1"), 3.0)

        write_block = [l.rstrip() for l in group.block()]
        for line in write_block:
            self.assertIn(line.rstrip(), test_case)
            # self.assertIn(line.rstrip(), write_block[i].rstrip())


if __name__ == "__main__":
    unittest.main()
