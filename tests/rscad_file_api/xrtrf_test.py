# LGPL-3.0 License
# Copyright (c) 2023 KIT-IAI-ESA

import pathlib
import unittest

from pyapi_rts.api.draft import Draft
from pyapi_rts.api.graph import get_connected_to

PATH = pathlib.Path(__file__).parent.absolute()


class XrTrfTest(unittest.TestCase):
    """
    Tests the connections between Cross rack trfs.
    """

    def test_xrtrf_connections(self):
        """
        Tests the connections between Cross rack trfs.
        """
        draft = Draft()
        draft.read_file(PATH / "models/xrtrf.dfx")

        # Check the connections
        xrtrf1 = draft.subsystems[0].get_components()[0]
        connected = get_connected_to(draft.get_graph(), xrtrf1.uuid)
        self.assertEqual(len(connected), 1)

        xrtrf2 = draft.subsystems[2].get_components()[0]
        connected = get_connected_to(draft.get_graph(), xrtrf2.uuid)
        self.assertEqual(len(connected), 1)


if __name__ == "__main__":
    unittest.main()
