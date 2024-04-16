# LGPL-3.0 License
# Copyright (c) 2023 KIT-IAI-ESA

import pathlib
import unittest

from pyapi_rts.api.draft import Draft
from pyapi_rts.api.graph import get_connected_to

PATH = pathlib.Path(__file__).parent.resolve()


class LinkedComponentsTest(unittest.TestCase):
    """
    Test components of the same type linked by name
    """

    def test_tline_link(self):
        """
        Test TLINE components linked by name
        """
        draft = Draft()
        draft.read_file(PATH / "tline_linked.dfx")
        self.assertEqual(len(draft.get_components(False)), 2)
        self.assertEqual(len(draft.subsystems), 1)
        tline1 = draft.get_components(False)[0]
        tline2 = draft.get_components(False)[1]
        self.assertTrue(tline2.uuid in get_connected_to(draft.get_graph(), tline1.uuid))

    def test_tline_box_linked(self):
        """
        Test TLINE componentes linked by name to a calculation box
        """
        draft = Draft()
        draft.read_file(PATH / "tline_linked_box.dfx")
        self.assertEqual(len(draft.get_components(False)), 3)
        self.assertEqual(len(draft.subsystems), 1)
        tline1 = draft.get_components(False)[0]
        tline2 = draft.get_components(False)[1]
        calc_box = draft.get_components(False)[2]
        self.assertTrue(
            tline2.uuid in get_connected_to(draft.get_graph(), tline1.uuid),
        )
        self.assertTrue(
            calc_box.uuid
            in get_connected_to(draft.get_graph(), tline2.uuid, excluded_edge_types=set()),
        )


if __name__ == "__main__":
    unittest.main()
