# LGPL-3.0 License
# Copyright (c) 2023 KIT-IAI-ESA

import pathlib
import unittest

from pyapi_rts.api.draft import Draft
from pyapi_rts.api.graph import get_connected_to

PATH = pathlib.Path(__file__).parent.absolute()


class LinkNodesTest(unittest.TestCase):
    """
    Tests the link nodes functionality.
    """

    def test_link_nodes(self):
        """
        Checks if link nodes are correctly recognized as connected.
        """
        draft = Draft()
        draft.read_file(PATH / "models/link_nodes.dfx")

        n1_nodes = list(filter((lambda c: c.name == "N1"), draft.get_components()))
        for node in n1_nodes:
            connected = get_connected_to(draft.get_graph(), node.uuid)
            self.assertEqual(len(connected), 2)
        # There are two N5 nodes in the draft with the linkNodes attribute set to 'no'.
        # This is not a valid model. However, the nodes should not be viewed as conncted.
        for component in draft.get_components():
            if component.uuid not in map(lambda c: c.uuid, n1_nodes):
                connected = get_connected_to(draft.get_graph(), component.uuid)
                self.assertEqual(len(connected), 0)


if __name__ == "__main__":
    unittest.main()
