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
        draft.read_file(PATH / "models/tline_linked/tline_linked.dfx")
        self.assertEqual(len(draft.get_components(False)), 7)
        self.assertEqual(len(draft.subsystems), 1)
        sub = draft.subsystems[0]
        bus1 = sub.search_by_name("BUS1")[0]
        bus2 = sub.search_by_name("BUS2")[0]

        # essentially, BUS1 and BUS2 should be viewed as connected
        # it could be useful to add an option to get_connected_to to exclude connections via lines, transformers etc
        # another possibility would be to allow getting the other end of the line and checking if BUS2 is connected to that end
        connected = get_connected_to(draft.get_graph(), bus1.uuid)
        self.assertTrue(bus2.uuid in connected)

        # tlines = draft.get_components_by_type('lf_rtds_sharc_sld_TLINE', False)
        # tline1 = tlines[0]
        # tline2 = tlines[1]


if __name__ == "__main__":
    unittest.main()
