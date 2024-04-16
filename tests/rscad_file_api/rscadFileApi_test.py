# LGPL-3.0 License
# Copyright (c) 2023 KIT-IAI-ESA

import pathlib
import unittest
from pyapi_rts.api.draft import Draft
from pyapi_rts.api.graph import get_connected_to

PATH = pathlib.Path(__file__).parent.resolve()


class ParserTestCase(unittest.TestCase):
    """
    Tests the .dfx parser
    """

    def test_parser_connection_stretch(self):
        """
        Checks if two rings of buses are read correctly
        """
        draft = Draft()
        draft.read_file(PATH / "bus_rings.dfx")
        self.assertEqual(len(draft.get_components(True)), 10)
        self.assertEqual(len(draft.get_components(False)), 10)
        graph = draft.get_graph()
        buslabel1 = draft.subsystems[0].search_by_name("BUS1")[0]
        self.assertEqual(buslabel1.parent, draft.subsystems[0])
        connected_to_bus1 = get_connected_to(graph, buslabel1.uuid)
        self.assertEqual(len(connected_to_bus1), 4)
        buslabel2 = draft.subsystems[0].search_by_name("BUS2")[0]
        connected_to_bus2 = get_connected_to(graph, buslabel2.uuid)
        self.assertEqual(len(connected_to_bus2), 4)

    def test_parser_connection_hierarchies(self):
        """
        Checks if connections are recognized between hierarchy
        """
        draft = Draft()
        draft.read_file(PATH / "test.dfx")
        self.assertEqual(len(draft.get_components(False)), 5)
        self.assertEqual(len(draft.get_components(True)), 11)
        self.assertEqual(len(draft.subsystems[0].get_components(False)), 5)
        self.assertEqual(len(draft.subsystems[0].get_components(True)), 11)
        self.assertEqual(len(draft.get_components_by_type("BUS", False)), 2)
        tline = draft.get_components_by_type("lf_rtds_sharc_sld_TLINE")

        connected = get_connected_to(draft.get_graph(), tline[0].uuid)
        self.assertTrue(tline[1].uuid in connected)
        self.assertEqual(len(connected), 10)

    def test_tline_connection_count(self):
        """
        Checks the number of connections of a TLINE for all possible states of numc
        """
        draft = Draft()
        draft.read_file(PATH / "tline.dfx")
        self.assertEqual(len(draft.get_components(False)), 1)
        tline = draft.get_components_by_type("lf_rtds_sharc_sld_TLINE")[0]
        self.assertEqual(len(tline.connection_points), 2)


if __name__ == "__main__":
    unittest.main()
