# LGPL-3.0 License
# Copyright (c) 2023 KIT-IAI-ESA

import pathlib
import unittest
from pyapi_rts.api.draft import Draft

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
        buslabel1 = draft.subsystems[0].search_by_name("BUS1")[0]
        self.assertEqual(buslabel1.parent, draft.subsystems[0])
        connected_to_bus1 = draft.subsystems[0].get_connected_to(buslabel1)
        self.assertEqual(len(connected_to_bus1), 4)
        buslabel2 = draft.subsystems[0].search_by_name("BUS2")[0]
        connected_to_bus2 = draft.subsystems[0].get_connected_to(buslabel2)
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

        hierarchies = [c for c in draft.subsystems[0].get_components() if c.type == "HIERARCHY"]

        connected = hierarchies[0].get_connected_to(tline[0])
        self.assertTrue(tline[1].uuid in map((lambda x: x.uuid), connected))
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
