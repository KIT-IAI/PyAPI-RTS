# LGPL-3.0 License
# Copyright (c) 2023 KIT-IAI-ESA

import pathlib
import unittest

from pyapi_rts.api import Draft, Component, Hierarchy, Subsystem

PATH = pathlib.Path(__file__).parent.absolute().resolve()


class DraftTest(unittest.TestCase):
    """
    Tests for the draft class
    """

    def test_init(self):
        """
        Tests the initialization of the draft
        """
        draft = Draft()
        self.assertEqual(draft.subsystems, [])
        self.assertEqual(draft.get_components(), [])

    def test_add_subsystem(self):
        """
        Tests the adding of a subsystem to the draft
        """
        draft = Draft()
        draft.add_subsystem("subsystem1")
        self.assertEqual(draft.subsystems, ["subsystem1"])

    def test_add_subsystem_component(self):
        """
        Tests the adding of a subsystem and a component to the draft
        """
        draft = Draft()
        subsystem = Subsystem(draft, 1)
        draft.add_subsystem(subsystem)
        draft.add_component(Component(), subsystem.index)
        self.assertEqual(draft.subsystems[0].number, 1)
        self.assertEqual(len(draft.subsystems), 1)
        self.assertEqual(len(draft.get_components()), 1)

    def test_add_subsystem_component_duplicate(self):
        """
        Tests the adding of a subsystem and a component to the draft
        """
        draft = Draft()
        subsystem = Subsystem(draft, 1)

        draft.add_subsystem(subsystem)
        draft.add_component(Component(), subsystem.index)

        subsystem2 = Subsystem(draft, 2)
        draft.add_subsystem(subsystem2)
        draft.add_component(Component(), subsystem2.index)
        self.assertEqual(len(draft.subsystems), 2)
        self.assertEqual(len(draft.subsystems[0].get_components()), 1)
        self.assertEqual(len(draft.get_components()), 2)

    def test_modify_component(self):
        """
        Tests the modification of a component in the draft
        """
        draft = Draft()
        subsystem = Subsystem(draft, 1)
        draft.add_subsystem(subsystem)
        component = Component()
        draft.add_component(component, subsystem.index)
        self.assertEqual(len(draft.get_components()), 1)
        self.assertEqual(draft.get_components()[0].x, 144)

        component.x = 48
        self.assertTrue(draft.modify_component(component))
        self.assertFalse(draft.modify_component(Component()))
        self.assertEqual(len(draft.get_components()), 1)
        self.assertEqual(draft.get_components()[0].x, 48)

    def test_remove_component(self):
        """
        Tests the removal of a component in the draft
        """
        draft = Draft()
        subsystem = Subsystem(draft, 1)
        draft.add_subsystem(subsystem)
        component = Component()
        draft.add_component(component, subsystem.index)
        self.assertEqual(len(draft.get_components()), 1)
        self.assertTrue(draft.remove_component(component.uuid))
        self.assertFalse(draft.remove_component(component.uuid))
        self.assertEqual(len(draft.get_components()), 0)

        # Test removing a component from a hierarchy
        draft = Draft()
        subsystem = Subsystem(draft, 1)
        draft.add_subsystem(subsystem)
        hierarchy = Hierarchy()
        draft.add_component(hierarchy, subsystem.index)
        component = Component()
        draft.add_component(component, hierarchy.uuid)
        self.assertEqual(len(draft.get_components()), 2)
        self.assertTrue(draft.remove_component(component.uuid))
        self.assertFalse(draft.remove_component(component.uuid))
        self.assertEqual(len(draft.get_components()), 1)

    def test_get_draft(self):
        """
        Tests the getting of the draft
        """
        draft = Draft()
        subsystem = Subsystem(draft, 1)
        draft.add_subsystem(subsystem)

        self.assertEqual(subsystem.get_draft(), draft)

        hierarchy = Hierarchy()
        subsystem.add_component(hierarchy)

        self.assertEqual(hierarchy.get_draft(), draft)

    def test_get_by_id(self):
        """
        Tests the getting of a component by id
        """
        draft = Draft()
        subsystem = Subsystem(draft, 1)
        draft.add_subsystem(subsystem)
        component = Component()
        draft.add_component(component, subsystem.index)

        self.assertEqual(draft.get_by_id(component.uuid), component)
        self.assertIsNone(draft.get_by_id("notanid"))

    def test_get_connection_graph(self):
        """
        Tests the composition of all subsystem connection graphs
        """
        draft = Draft()
        draft.read_file(PATH / "models/search_by_name.dfx")
        graph = draft.get_connection_graph()
        self.assertEqual(len(graph.nodes), 4)
        self.assertEqual(len(graph.edges), 0)

    def test_get_tline_constants(self):
        """
        Tests the loading of the tline constants and conversion to an RLC tline.
        """
        draft = Draft()
        draft.read_file(PATH / "models/search_by_name.dfx")
        constants = draft.get_tline_constants("simple")
        self.assertEqual(len(constants.sections), 3)
        self.assertEqual(constants.get("Line Summary/Line Length"), "20.0")
        self.assertIsNone(draft.get_tline_constants("doesnotexist"))

        rlc_tline = draft.get_rlc_tline("simple")
        self.assertEqual(rlc_tline.length, 20.0)
        self.assertIsNone(draft.get_rlc_tline("doesnotexist"))

    def test_search_by_name(self):
        """
        Tests the search for components by name in all subsystems
        """
        draft = Draft()
        draft.read_file(PATH / "models/search_by_name.dfx")
        self.assertEqual(len(draft.search_by_name("BUS1").items()), 2)
        self.assertEqual(len(draft.search_by_name("BUS1", True)["SS #1"]), 2)
        self.assertEqual(
            len(draft.search_by_name("bus1", True, case_sensitive=True)["SS #2"]), 0
        )
        self.assertEqual(
            len(draft.search_by_name("bus1", True, case_sensitive=False)["SS #1"]), 2
        )
        self.assertEqual(
            len(draft.search_by_name("bus1", True, case_sensitive=False)), 2
        )
        self.assertEqual(
            len(
                draft.search_by_name("bus1", recursive=False, case_sensitive=True)[
                    "SS #2"
                ]
            ),
            0,
        )
        self.assertEqual(
            len(
                draft.search_by_name("bus2", recursive=True, case_sensitive=False)[
                    "SS #2"
                ]
            ),
            1,
        )


if __name__ == "__main__":
    unittest.main()
