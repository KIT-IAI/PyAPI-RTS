# LGPL-3.0 License
# Copyright (c) 2023 KIT-IAI-ESA

import pathlib
import unittest

import networkx as nx

from pyapi_rts.api import Container, Component, Draft, Hierarchy


PATH = pathlib.Path(__file__).parent.resolve()


class ComponentBoxTest(unittest.TestCase):
    """
    Tests for the ComponentBox class
    """

    def test_init(self):
        """
        Tests the init method
        """
        no_parent = Container()
        self.assertEqual(no_parent.box_parent, None)
        self.assertEqual(no_parent.get_components(), [])
        parent = Container(parent=no_parent)
        self.assertEqual(parent.box_parent, no_parent)

    def test_get_by_id(self):
        """
        Tests the get_by_id method
        """
        component_box = Hierarchy()
        component = Component()
        component_box.add_component(component)
        self.assertEqual(component_box.get_by_id(component.uuid), component)
        # Recursive search
        component_box2 = Hierarchy()
        component_box3 = Hierarchy()
        component_box2.add_component(component_box3)
        self.assertIsNone(component_box2.get_by_id(component.uuid, True))
        component_box3.add_component(component_box)
        self.assertEqual(component_box2.get_by_id(component.uuid, True).uuid, component.uuid)
        self.assertIsNone(component_box2.get_by_id(component.uuid, False))

    def test_add_component(self):
        """
        Tests the add_component method
        """
        # No graph generated
        component_box = Hierarchy()
        component = Component()
        component_box.add_component(component)
        self.assertEqual(component_box.get_components()[0].uuid, component.uuid)
        component2 = Component()
        component_box.add_component(component2)
        self.assertEqual(len(component_box.get_components()), 2)
        # Component Box is parent of componentBox
        component_box2 = Hierarchy()
        component_box2.add_component(component_box)
        self.assertEqual(component_box2.get_components()[0].uuid, component_box.uuid)
        self.assertEqual(component_box.box_parent, component_box2)

    def test_remove_component(self):
        """
        Tests the remove_component method
        """
        component_box = Container()
        component = Component()
        component_box.add_component(component)
        self.assertEqual(component_box.get_components()[0].uuid, component.uuid)
        self.assertTrue(component_box.remove_component(component.uuid))
        self.assertEqual(component_box.get_components(), [])

        self.assertFalse(component_box.remove_component("not-existing-uuid"))
        # Graph
        component_box.add_component(component)
        self.assertFalse(nx.utils.graphs_equal(component_box.get_graph()[0], nx.Graph()))
        self.assertTrue(component_box.remove_component(component.uuid))
        self.assertTrue(nx.utils.graphs_equal(component_box.get_graph()[0], nx.Graph()))

    def test_modify_component(self):
        """
        Tests the modify_component method.
        """
        component_box = Container()
        component = Component()
        component_box.add_component(component)
        self.assertEqual(component_box.get_components()[0].uuid, component.uuid)

        component.COMPONENT_TYPE_NAME = "new-type"
        self.assertNotEqual(component_box.get_components(), [component])
        component_box.update_component(component)
        self.assertEqual(component_box.get_components()[0].uuid, component.uuid)

        self.assertEqual(component.COMPONENT_TYPE_NAME, "new-type")

    def test_get_connected_to(self):
        """
        Tests if the get_connected_to method returns copies of the components
        """
        draft = Draft()
        draft.read_file(PATH / "bus_rings.dfx")
        bus = draft.subsystems[0].get_components()[1]
        connected_to_bus = draft.subsystems[0].get_connected_to(bus)
        self.assertNotEqual(connected_to_bus[0].x, 16 + 32 * 10)
        connected_to_bus[1].x = 16 + 32 * 10
        self.assertEqual(connected_to_bus[1].x, 16 + 32 * 10)

        for component in draft.get_components():
            self.assertFalse(
                component.uuid == connected_to_bus[1].uuid and component.x == 16 + 32 * 10
            )

    def test_get_connected_to_groups(self):
        """
        Tests if the get_connected_to method returns correct connections when components are grouped.
        """
        draft = Draft()
        draft.read_file(PATH / "models/grouped.dfx")

        # BUS components grouped
        bus2 = draft.subsystems[0].search_by_name("BUS2")[0]
        connected2 = draft.subsystems[0].get_connected_to(bus2)
        self.assertEqual(len(connected2), 3)

        # BUSLabel + BUS components grouped
        bus3 = draft.subsystems[0].search_by_name("BUS3")[0]
        connected3 = draft.subsystems[0].get_connected_to(bus3)
        self.assertEqual(len(connected3), 3)

        # BUS components + DYLOAD grouped
        bus4 = draft.subsystems[0].search_by_name("BUS4")[0]
        connected4 = draft.subsystems[0].get_connected_to(bus4)
        self.assertEqual(len(connected4), 3)

        # 1 BUS component + DYLOAD grouped
        bus5 = draft.subsystems[0].search_by_name("BUS5")[0]
        connected5 = draft.subsystems[0].get_connected_to(bus5)
        self.assertEqual(len(connected5), 3)

        # all 4 components grouped
        bus6 = draft.subsystems[0].search_by_name("BUS6")[0]
        connected6 = draft.subsystems[0].get_connected_to(bus6)
        self.assertEqual(len(connected6), 3)

        # BUS components grouped, then grouped with BUSLabel
        bus7 = draft.subsystems[0].search_by_name("BUS7")[0]
        connected7 = draft.subsystems[0].get_connected_to(bus7)
        self.assertEqual(len(connected7), 3)

        # BUS components grouped, then grouped with DYLOAD
        bus8 = draft.subsystems[0].search_by_name("BUS8")[0]
        connected8 = draft.subsystems[0].get_connected_to(bus8)
        self.assertEqual(len(connected8), 3)

        # BUSLabel grouped with DYLOAD
        bus9 = draft.subsystems[0].search_by_name("BUS9")[0]
        connected9 = draft.subsystems[0].get_connected_to(bus9)
        self.assertEqual(len(connected9), 3)

        # BUSLabel and BUS grouped in Hierarchy Box
        bus1 = draft.subsystems[0].search_by_name("BUS1")[0]
        connected1 = draft.subsystems[0].get_connected_to(bus1)
        # at least the bus should be connected to the group in the hierarchy box
        self.assertGreater(len(connected1), 2)
        # also, it should include the dynamic load in the list
        self.assertIn("RLDload", [c.name for c in connected1])

    def test_wirelabel_hierarchy(self):
        """
        Test for the connetions between wirelabels through adjacent hierarchies without direct contact.
        """
        draft = Draft()
        draft.read_file(PATH / "models/get_connected_at_point/wirelabel_hierarchy.dfx")
        self.assertEqual(len(draft.get_components()), 5)
        self.assertEqual(len(draft.subsystems[0].get_components()), 2)
        wirelabel = draft.subsystems[0].search_by_name("A2")[0]
        self.assertEqual(len(draft.subsystems[0].get_connected_to(wirelabel)), 2)

    def test_get_components(self):
        """
        Tests if the get_connected_to method returns copies of the components
        """
        draft = Draft()
        draft.read_file(PATH / "models/get_components/3_buses.dfx")
        components = draft.subsystems[0].get_components()

        self.assertEqual(len(components), 3)

    def test_get_components_grouped(self):
        """
        Tests if the get_connected_to method returns copies of the components
        """
        draft = Draft()
        draft.read_file(PATH / "models/get_components/3_buses_grouped.dfx")

        components = draft.subsystems[0].get_components(with_groups=False)
        self.assertEqual(len(components), 1)

        components = draft.subsystems[0].get_components(with_groups=True)
        self.assertEqual(len(components), 4)

    def test_get_components_ground(self):
        """
        Tests if ground components are recognized correctly.
        """
        draft = Draft()
        draft.read_file(PATH / "models/grounds.dfx")

        comps = draft.subsystems[0].get_components()
        self.assertEqual(len(comps), 3)

    def test_get_components_grouped_double(self):
        """
        Tests if components inside multiple groups are returned.
        """
        draft = Draft()
        draft.read_file(PATH / "models/grouped_7.dfx")

        comps = draft.subsystems[0].get_components(recursive=False, with_groups=True)
        self.assertEqual(len(comps), 9)


if __name__ == "__main__":
    unittest.main()
