# LGPL-3.0 License
# Copyright (c) 2023 KIT-IAI-ESA

import pathlib
import unittest
from pyapi_rts.api.draft import Draft


PATH = pathlib.Path(__file__).parent.resolve()


class EnumerationTest(unittest.TestCase):
    """
    Tests for the enumeration parameter of components.
    """

    def test_enumeration_zero(self):
        """Test case for value = 0."""
        draft = Draft()
        draft.read_file(PATH / "models/enumeration/buses.dfx")

        components = draft.get_components()
        self.assertEqual(len(components), 8)

        self.assertIn("BUS", (c.name for c in components))

    def test_simple_enumeration(self):
        """Test case for decimal values."""
        draft = Draft()
        draft.read_file(PATH / "models/enumeration/buses.dfx")

        components = draft.get_components()
        self.assertEqual(len(components), 8)

        self.assertIn("BUS1", (c.name for c in components))
        self.assertIn("BUS2", (c.name for c in components))
        self.assertIn("BUS3", (c.name for c in components))

    def test_enumeration_deactivated(self):
        """Test case for deactivated enumeration."""
        draft = Draft()
        draft.read_file(PATH / "models/enumeration/buses.dfx")

        components = draft.get_components()
        self.assertEqual(len(components), 8)

        self.assertIn("BUSD", (c.name for c in components))

    def test_custom_enumeration_string(self):
        """Test case for custom enumeration strings."""
        draft = Draft()
        draft.read_file(PATH / "models/enumeration/buses.dfx")

        components = draft.get_components()
        self.assertEqual(len(components), 8)

        for c in components:
            print(c.name)

        self.assertIn("BUSX5Y", (c.name for c in components))
        self.assertIn("BUSXY", (c.name for c in components))

    def test_active_no_enumeration_char(self):
        """Enumeration is active but no # in name."""
        draft = Draft()
        draft.read_file(PATH / "models/enumeration/buses.dfx")

        components = draft.get_components()
        self.assertEqual(len(components), 8)

        for c in components:
            print(c.name)

        self.assertIn("BUSZ", (c.name for c in components))

    def test_enumeration_styles_hex(self):
        """Test case for hex style."""
        draft = Draft()
        draft.read_file(PATH / "models/enumeration/styles.dfx")

        components = draft.get_components()
        self.assertEqual(len(components), 9)

        names = [c.name for c in components]

        self.assertIn("BUS1", names)
        self.assertIn("BUS1b", names)
        self.assertIn("BUS64", names)

    def test_enumeration_styles_lower(self):
        """Test case for lowercase style."""
        draft = Draft()
        draft.read_file(PATH / "models/enumeration/styles.dfx")

        components = draft.get_components()
        self.assertEqual(len(components), 9)

        names = [c.name for c in components]

        self.assertIn("BUSa", names)
        self.assertIn("BUSaa", names)
        self.assertIn("BUScv", names)

    def test_enumeration_styles_upper(self):
        """Test case for uppercase style."""
        draft = Draft()
        draft.read_file(PATH / "models/enumeration/styles.dfx")

        components = draft.get_components()
        self.assertEqual(len(components), 9)

        names = [c.name for c in components]

        self.assertIn("BUSZ", names)
        self.assertIn("BUSAZ", names)
        self.assertIn("BUSYZ", names)

    def test_enumeration_signals(self):
        """Test case for signal connections using enumeration."""
        draft = Draft()
        draft.read_file(PATH / "models/enumeration/signals.dfx")

        components = draft.get_components()
        self.assertEqual(len(components), 24)

        names = [c.name for c in components]

        self.assertIn("A1", names)
        self.assertIn("Ab", names)
        self.assertIn("AC", names)

        subsys = draft.subsystems[0]
        self.assertEqual(len(subsys.get_connected_to_label("A1")), 2)
        self.assertEqual(
            len(subsys.get_connected_to_label("A1", return_connecting=True)), 6
        )
        self.assertEqual(len(subsys.get_connected_to_label("B4")), 1)

        self.assertEqual(len(subsys.get_connected_to_label("Ab")), 2)
        self.assertEqual(
            len(subsys.get_connected_to_label("Ab", return_connecting=True)), 6
        )
        self.assertEqual(len(subsys.get_connected_to_label("Be")), 1)

        self.assertEqual(len(subsys.get_connected_to_label("AC")), 2)
        self.assertEqual(
            len(subsys.get_connected_to_label("AC", return_connecting=True)), 6
        )
        self.assertEqual(len(subsys.get_connected_to_label("B6")), 1)


if __name__ == "__main__":
    unittest.main()
