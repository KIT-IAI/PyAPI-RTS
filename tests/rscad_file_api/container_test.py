# LGPL-3.0 License
# Copyright (c) 2023 KIT-IAI-ESA

import pathlib
import unittest

import networkx as nx

from pyapi_rts.api import Container, Component, Draft, Hierarchy
from pyapi_rts.api.graph import get_connected_to


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

    def test_wirelabel_hierarchy(self):
        """
        Test for the connetions between wirelabels through adjacent hierarchies without direct contact.
        """
        draft = Draft()
        draft.read_file(PATH / "models/get_connected_at_point/wirelabel_hierarchy.dfx")
        self.assertEqual(len(draft.get_components()), 5)
        self.assertEqual(len(draft.subsystems[0].get_components()), 2)
        wirelabel = draft.subsystems[0].search_by_name("A2")[0]
        self.assertEqual(len(get_connected_to(draft.get_graph(), wirelabel.uuid)), 2)

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
