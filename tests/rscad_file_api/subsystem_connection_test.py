# LGPL-3.0 License
# Copyright (c) 2023 KIT-IAI-ESA

import pathlib
import unittest

from pyapi_rts.api import Draft

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
        connected = draft.subsystems[0].get_connected_to(tline_first_subsystem)
        self.assertTrue(
            tline_second_subsystem.uuid in list(map((lambda c: c.uuid), connected))
        )


if __name__ == "__main__":
    unittest.main()
