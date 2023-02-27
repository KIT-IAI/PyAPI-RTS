# LGPL-3.0 License
# Copyright (c) 2023 KIT-IAI-ESA

import pathlib
import unittest

from pyapi_rts.generated.lfrtdssharcsldSHUNTCAP import (
    lfrtdssharcsldSHUNTCAP,
)
from pyapi_rts.generated.rtdsudcDYLOAD import (
    rtdsudcDYLOAD,
)
from pyapi_rts.api import Draft

PATH = pathlib.Path(__file__).parent.resolve()


class GetConnectedToTest(unittest.TestCase):
    """
    Tests the aggregation of components with an example.
    """

    def test_10_wirelabels_in_box(self):
        """
        Test component aggeration with an example.
        """
        draft = Draft()
        draft.read_file(PATH / "models/labels_in_boxes.dfx")
        self.assertEqual(len(draft.subsystems), 1)
        self.assertEqual(len(draft.get_components()), 21)
        a1 = draft.search_by_name("A1")["SS #1"][0]
        # Get relevant components
        connected_to = draft.subsystems[0].get_connected_to(a1, clone=False)
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
        B123_1_400V = next(
            filter(
                (lambda c: c.name == "B123_1_400V"),
                draft.subsystems[0].get_components(),
            ),
            None,
        )
        # Get relevant components
        connected_to = draft.subsystems[0].get_connected_to(B123_1_400V, clone=False)
        # not connected to self and one hierarchy
        self.assertEqual(len(connected_to), 21 - 1 - 1)
        dyloads = list(
            filter(
                (lambda c: isinstance(c, rtdsudcDYLOAD)),
                connected_to,
            )
        )
        self.assertEqual(len(dyloads), 1)
        shunts = list(
            filter(
                (lambda c: isinstance(c, lfrtdssharcsldSHUNTCAP)),
                connected_to,
            )
        )
        self.assertEqual(len(shunts), 1)


if __name__ == "__main__":
    unittest.main()
