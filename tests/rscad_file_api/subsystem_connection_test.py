# LGPL-3.0 License
# Copyright (c) 2023 KIT-IAI-ESA

import pathlib
import unittest

from pyapi_rts.api import Draft
from pyapi_rts.api.graph import get_connected_to

PATH = pathlib.Path(__file__).parent.resolve()


class SubsystemConnectionTest(unittest.TestCase):
    """
    Test the connections between components with the
    same name in different subsystems.
    """

    def test_subsystem_connection(self):
        """
        Test the connections between components with the
        same name in different subsystems.
        """
        draft = Draft()
        draft.read_file(PATH / "subsystem_connection_test.dfx")
        self.assertEqual(len(draft.subsystems), 2)
        self.assertEqual(len(draft.subsystems[0].get_components()), 3)
        self.assertEqual(len(draft.subsystems[1].get_components()), 3)
        tline_first_subsystem = draft.subsystems[0].search_by_name("LINESE1")[0]
        tline_second_subsystem = draft.subsystems[1].search_by_name("LINESE1")[0]
        connected = get_connected_to(draft.get_graph(), tline_first_subsystem.uuid)
        self.assertTrue(tline_second_subsystem.uuid in connected)


if __name__ == "__main__":
    unittest.main()
