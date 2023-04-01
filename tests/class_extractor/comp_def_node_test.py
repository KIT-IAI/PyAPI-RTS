# LGPL-3.0 License
# Copyright (c) 2023 KIT-IAI-ESA

import unittest
from pyapi_rts.shared.node_type import NodeIO, NodeType

from pyapi_rts.class_extractor.readers.blocks.node_block import CompDefNode


class CompDefNodeTest(unittest.TestCase):
    """
    Tests the CompDefNode class.
    """

    def test_init(self):
        """
        Tests the initialization of the CompDefNode class.
        """
        cdn = CompDefNode(
            "name", "$x", "$y", NodeIO.SHORT, NodeType.NAME_CONNECTED, "link", "phase"
        )
        self.assertEqual(cdn.name, "name")
        self.assertEqual(cdn.x, "$x")
        self.assertEqual(cdn.y, "$y")
        self.assertEqual(cdn.type, NodeType.NAME_CONNECTED)
        self.assertEqual(cdn.link_name, "link")
        self.assertEqual(cdn.io, NodeIO.SHORT)
        self.assertEqual(cdn.phase, "phase")

    def test_as_ext_conn_point(self):
        """
        Tests the conversion of the CompDefNode to an ExtConnectionPoint.
        """
        cdn = CompDefNode(
            "name", "$x", "$y", NodeIO.OUTPUT, NodeType.NAME_CONNECTED, "link", "phase"
        )
        ext_conn_point = cdn.as_ext_conn_point()
        self.assertEqual(ext_conn_point.name, "name")
        self.assertEqual(ext_conn_point.x, "$x")
        self.assertEqual(ext_conn_point.y, "$y")
        self.assertEqual(ext_conn_point.type, NodeType.NAME_CONNECTED)
        self.assertEqual(ext_conn_point.link_name, "link")
        self.assertEqual(ext_conn_point.io, NodeIO.OUTPUT)
        self.assertEqual(ext_conn_point.phase, 0)

        with self.assertRaises(ValueError):
            cdn = CompDefNode(
                "name", "x", "y", NodeIO.UNDEFINED, NodeType.NAME_CONNECTED, "link", "phase"
            )
            cdn.as_ext_conn_point()


if __name__ == "__main__":
    unittest.main()
