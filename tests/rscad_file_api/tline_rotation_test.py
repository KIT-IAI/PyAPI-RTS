# LGPL-3.0 License
# Copyright (c) 2023 KIT-IAI-ESA

import pathlib
import unittest

from pyapi_rts.api.draft import Draft
from pyapi_rts.api.graph import get_connected_to

PATH = pathlib.Path(__file__).parent.absolute().resolve()


class TlineRotationTest(unittest.TestCase):
    """
    Test TLINE components rotated by name
    """

    def test_tline_rotation(self):
        """
        Test TLINE components rotated by name
        """
        draft = Draft()
        draft.read_file(PATH / "models/tline_rotation.dfx")
        for i in range(1, 5):
            tline = draft.subsystems[0].search_by_name(f"LINESE{i}")[0]
            self.assertEqual(len(get_connected_to(draft.get_graph(), tline.uuid)), i)


if __name__ == "__main__":
    unittest.main()
