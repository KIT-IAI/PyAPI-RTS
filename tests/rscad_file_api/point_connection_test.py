# LGPL-3.0 License
# Copyright (c) 2023 KIT-IAI-ESA

import pathlib
import unittest
from pyapi_rts.api.draft import Draft

PATH = pathlib.Path(__file__).parent.absolute()


class PointConnectionTest(unittest.TestCase):
    """
    Tests for the connections on a given connection point.
    """

    def test_direct_connection(self):
        """
        Tests a direct connection between two components with a WIRE.
        """
        draft = Draft()
        draft.read_file(PATH / "models/point_connection_direct.dfx")
        self.assertEqual(len(draft.get_components()), 3)

        # Test the connection between the two components
        inort2 = draft.subsystems[0].search_by_name("INORT1")[0]
        self.assertEqual(
            len(
                draft.subsystems[0].get_connected_at_component_point(
                    inort2.uuid, "NA", True
                )
            ),
            3,
        )
        self.assertEqual(
            len(
                draft.subsystems[0].get_connected_at_component_point(
                    inort2.uuid, "NA", False
                )
            ),
            2,
        )

        self.assertEqual(
            len(
                draft.subsystems[0].get_connected_at_component_point(
                    inort2.uuid, "CCSIG", True
                )
            ),
            1,
        )

        # Test the wrapper in the component class
        self.assertEqual(
            len(inort2.get_connected_at_point("CCSIG", True)),
            1,
        )

    def test_multi_layer(self):
        """
        Tests the direct connection between two components on different layers.
        """
        draft = Draft()
        draft.read_file(PATH / "models/point_connection_multi_layer.dfx")
        self.assertEqual(len(draft.get_components()), 8)

        src1 = draft.subsystems[0].search_by_name("SRC1")[0]

        self.assertEqual(
            len(
                draft.subsystems[0].get_connected_at_component_point(
                    src1.uuid, "A", True
                )
            ),
            7,
        )
        self.assertEqual(
            len(
                draft.subsystems[0].get_connected_at_component_point(
                    src1.uuid, "A", False
                )
            ),
            3,
        )

    def test_connected_to_group(self):
        """Test that connected components are recognized when some of them are in a group."""
        draft = Draft()
        draft.read_file(
            PATH / "models/get_connected_at_point/wirelabel_connection_grouped.dfx"
        )
        # 2 components are grouped and seem to not count here...
        self.assertEqual(len(draft.get_components()), 17)

        pv = draft.subsystems[0].search_by_name("PV1Array")[0]

        connected = draft.subsystems[0].get_connected_at_component_point(
            pv.uuid, "INS", True
        )

        # expected: PVArray, Wire, Wirelabel
        self.assertEqual(len(connected), 3)

    def test_wirelabel_connection(self):
        """Test that components connected to point via wirelabel are found."""
        draft = Draft()
        draft.read_file(PATH / "models/get_connected_at_point/wirelabel_connection.dfx")
        self.assertEqual(len(draft.get_components()), 19)

        pv = draft.subsystems[0].search_by_name("PV1Array")[0]

        connected = draft.subsystems[0].get_connected_at_component_point(
            pv.uuid, "INS", True
        )

        # expected: PVArray, Wire, Wirelabel, Wirelabel, Wire, Slider
        self.assertEqual(len(connected), 6)
        # self.assertEqual(
        #     len(
        #         draft.subsystems[0].get_connected_at_point(src1.uuid, "A", False)
        #     ),
        #     3,
        # )


if __name__ == "__main__":
    unittest.main()
