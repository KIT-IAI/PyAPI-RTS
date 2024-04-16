# LGPL-3.0 License
# Copyright (c) 2023 KIT-IAI-ESA

import pathlib
import unittest


from pyapi_rts.api import Draft
from pyapi_rts.api.graph import get_connected_to
from pyapi_rts.generated.lfrtdssharcsldSHUNTCAP import lfrtdssharcsldSHUNTCAP
from pyapi_rts.generated.rtdsudcDYLOAD import rtdsudcDYLOAD


PATH = pathlib.Path(__file__).parent.resolve()


class GraphTest(unittest.TestCase):
    """
    Tests for the ComponentBox class
    """

    def test_get_connected_to_groups(self):
        """
        Tests if the get_connected_to method returns correct connections when components are grouped.
        """
        draft = Draft()
        draft.read_file(PATH / "models/grouped.dfx")
        graph = draft.get_graph()

        # BUS components grouped
        bus2 = draft.subsystems[0].search_by_name("BUS2")[0]
        connected2 = get_connected_to(graph, bus2.uuid)
        self.assertEqual(len(connected2), 3)

        # BUSLabel + BUS components grouped
        bus3 = draft.subsystems[0].search_by_name("BUS3")[0]
        connected3 = get_connected_to(graph, bus3.uuid)
        self.assertEqual(len(connected3), 3)

        # BUS components + DYLOAD grouped
        bus4 = draft.subsystems[0].search_by_name("BUS4")[0]
        connected4 = get_connected_to(graph, bus4.uuid)
        self.assertEqual(len(connected4), 3)

        # 1 BUS component + DYLOAD grouped
        bus5 = draft.subsystems[0].search_by_name("BUS5")[0]
        connected5 = get_connected_to(graph, bus5.uuid)
        self.assertEqual(len(connected5), 3)

        # all 4 components grouped
        bus6 = draft.subsystems[0].search_by_name("BUS6")[0]
        connected6 = get_connected_to(graph, bus6.uuid)
        self.assertEqual(len(connected6), 3)

        # BUS components grouped, then grouped with BUSLabel
        bus7 = draft.subsystems[0].search_by_name("BUS7")[0]
        connected7 = get_connected_to(graph, bus7.uuid)
        self.assertEqual(len(connected7), 3)

        # BUS components grouped, then grouped with DYLOAD
        bus8 = draft.subsystems[0].search_by_name("BUS8")[0]
        connected8 = get_connected_to(graph, bus8.uuid)
        self.assertEqual(len(connected8), 3)

        # BUSLabel grouped with DYLOAD
        bus9 = draft.subsystems[0].search_by_name("BUS9")[0]
        connected9 = get_connected_to(graph, bus9.uuid)
        self.assertEqual(len(connected9), 3)

        # BUSLabel and BUS grouped in Hierarchy Box
        bus1 = draft.subsystems[0].search_by_name("BUS1")[0]
        connected1 = get_connected_to(graph, bus1.uuid)
        # at least the bus should be connected to the group in the hierarchy box
        self.assertGreater(len(connected1), 2)
        # also, it should include the dynamic load in the list
        self.assertIn("RLDload", [draft.get_by_id(c).name for c in connected1])

    def test_10_wirelabels_in_box(self):
        """
        Test component aggeration with an example.
        """
        draft = Draft()
        draft.read_file(PATH / "models/labels_in_boxes.dfx")
        self.assertEqual(len(draft.subsystems), 1)
        self.assertEqual(len(draft.get_components()), 21)
        graph = draft.get_graph()
        a1 = draft.subsystems[0].search_by_name("A1")[0]
        # Get relevant components
        connected_to = get_connected_to(graph, a1.uuid)
        # Should be connected to one other wirelabel
        self.assertEqual(len(connected_to), 1)

    def test_kit_aggregation_min(self):
        """
        Test component aggeration with an example.
        """
        draft = Draft()
        draft.read_file(PATH / "aggregation/kit_aggregation_min2.dfx")
        self.assertEqual(len(draft.subsystems), 1)
        self.assertEqual(len(draft.get_components()), 21)
        graph = draft.get_graph()
        B123_1_400V = next(
            filter(
                (lambda c: c.name == "B123_1_400V"),
                draft.subsystems[0].get_components(),
            ),
            None,
        )
        # Get relevant components
        connected_to = get_connected_to(graph, B123_1_400V.uuid)
        # not connected to self and one hierarchy
        self.assertEqual(len(connected_to), 21 - 1 - 1)
        dyloads = list(
            filter(
                (lambda c: isinstance(draft.get_by_id(c), rtdsudcDYLOAD)),
                connected_to,
            )
        )
        self.assertEqual(len(dyloads), 1)
        shunts = list(
            filter(
                (lambda c: isinstance(draft.get_by_id(c), lfrtdssharcsldSHUNTCAP)),
                connected_to,
            )
        )
        self.assertEqual(len(shunts), 1)


if __name__ == "__main__":
    unittest.main()
