# LGPL-3.0 License
# Copyright (c) 2023 KIT-IAI-ESA

from typing import Any
import unittest
from pyapi_rts.api.internals.block import Block

from pyapi_rts.api.component import Component
from pyapi_rts.api.enumeration import EnumerationStyle
from pyapi_rts.api.parameters.connection_point import ConnectionPoint
from pyapi_rts.shared.node_type import NodeIO


class ComponentTest(unittest.TestCase):
    """
    Test for the Component base class
    """

    UUID4_REGEX = r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$"
    COMPONENT_TEST = """COMPONENT_TYPE=BUS
	240 368 0 0 7
	PARAMETERS-START:
	LW1	:3.0
	SCOL	:ORANGE
	DOCUMENT	:NO
	x1	:-64
	y1	:0
	x2	:32
	y2	:0
	PARAMETERS-END:
	ENUMERATION:
		true
		1
		Integer
		#"""

    @unittest.skip("not working")
    def test_init(self):
        """
        Test for the init method and the read values
        """
        block = Block(self.COMPONENT_TEST.split("\n"))
        component = Component()
        component.read_block(block)
        self.assertEqual(component._type, "BUS")
        self.assertEqual(component._parameters["LW1"], "3.0")
        self.assertEqual(component._parameters["SCOL"], "ORANGE")
        self.assertEqual(component._parameters["DOCUMENT"], "NO")
        self.assertEqual(component._parameters["x1"], "-64")
        self.assertEqual(component._parameters["y1"], "0")
        self.assertEqual(component._parameters["x2"], "32")
        self.assertEqual(component._parameters["y2"], "0")
        self.assertIsNotNone(component.enumeration)
        self.assertRegex(component.uuid, self.UUID4_REGEX)
        # self.assertEqual(len(component.connection_points()), 0)

    def test_set_get(self):
        """
        Tests the set and get operations
        """
        block = Block(self.COMPONENT_TEST.split("\n"))
        component = Component()
        component.read_block(block)

        self.assertNotEqual(component.x, 16)
        component.x = 16
        self.assertEqual(component.x, 16)

        self.assertNotEqual(component.y, 16)
        component.y = 16
        self.assertEqual(component.y, 16)

        self.assertNotEqual(component.rotation, 3)
        component.rotation = 5
        self.assertEqual(component.rotation, 1)
        component.rotation = -2
        self.assertEqual(component.rotation, 2)
        component.rotation = 3
        self.assertEqual(component.rotation, 3)

        component.mirror = 0
        self.assertNotEqual(component.mirror, 1)
        component.mirror = 3
        self.assertEqual(component.mirror, 1)
        component.mirror = -1
        self.assertEqual(component.mirror, 1)
        self.assertEqual(component.load_units, 10)

    def test_enumeration(self):
        """
        Tests the enumeration property
        """
        block = Block(self.COMPONENT_TEST.split("\n"))
        component = Component()
        component.read_block(block)
        self.assertIsNotNone(component.enumeration)
        self.assertEqual(component.enumeration.is_active, True)
        self.assertEqual(component.enumeration.enumeration_string, "#")
        self.assertEqual(component.enumeration.style, EnumerationStyle.Integer)
        self.assertEqual(component.enumeration.value, 1)
        self.assertEqual(component.enumeration.apply("test#"), "test1")

    def conn_points(rectangle: Any, dictionary: dict):
        """
        Returns the connection points of a rectangle for testing
        """
        return [ConnectionPoint(1, 1, "test", NodeIO.UNDEFINED)]

    @unittest.skip
    def test_position_dict(self):
        """
        Tests the generate_pos_dict() method.
        """

        block = Block(self.COMPONENT_TEST.split("\n"))
        component = Component()
        component.read_block(block)
        self.assertEqual(component.generate_pos_dict(), {})
        component._update_rectangle((1, 1, 1, 1))
        self.assertEqual(component.generate_pos_dict(), {})

        component.connection_points = self.conn_points
        self.assertEqual(
            component.generate_pos_dict(), {"241,369": [("test", component.uuid)]}
        )

        component._rotation = 2
        self.assertEqual(
            component.generate_pos_dict(), {"239,369": [("test", component.uuid)]}
        )
        # WTF
        self.assertEqual(component.x1, 1)
        self.assertEqual(component.y1, 1)
        self.assertEqual(component.x2, 1)
        self.assertEqual(component.y2, 1)
        self.assertTrue(len(component.connection_points()) > 0)

    @unittest.skip
    def test_overlap(self):  # ASDF: murks
        """
        Tests the overlaps method
        """
        component_a = Component()
        component_a._update_rectangle((10, 20, 30, 40))
        component_b = Component()
        component_b._update_rectangle((10, 20, 30, 40))

        self.assertTrue(component_a.overlaps(component_b))
        component_b._update_rectangle((100, 100, 30, 40))
        self.assertFalse(component_a.overlaps(component_b))
        component_b._update_rectangle((40, 20, 30, 40))
        self.assertTrue(component_a.overlaps(component_b))

    @unittest.skip
    def test_rotate(self):
        """
        Tests the rotate method
        """

        component_a = Component()
        component_a._update_rectangle((10, 20, 30, 40))

        # Rotate by 90 degrees
        component_b = component_a.rotated_copy(1, 0)
        self.assertEqual(component_a.x1, component_b.y1)
        self.assertEqual(component_a.x2, component_b.y2)
        self.assertEqual(component_a.y1, component_b.x1)
        self.assertEqual(component_a.y2, component_b.x2)
        self.assertEqual(component_a.stretchable, component_b.stretchable)
        self.assertEqual(component_b.x1, 20)
        self.assertEqual(component_b.y1, 10)
        self.assertEqual(component_b.x2, 40)
        self.assertEqual(component_b.y2, 30)

        # Rotate by 180 degrees
        component_b = component_a.rotated_copy(2, 0)
        self.assertEqual(component_a.x1, -component_b.x1)
        self.assertEqual(component_a.x2, component_b.x2)
        self.assertEqual(component_a.y1, -component_b.y1)
        self.assertEqual(component_a.y2, component_b.y2)
        self.assertEqual(component_a.stretchable, component_b.stretchable)
        self.assertEqual(component_b.x1, -10)
        self.assertEqual(component_b.y1, -20)
        self.assertEqual(component_b.x2, 30)
        self.assertEqual(component_b.y2, 40)

        # Rotate by 270 degrees
        component_b = component_a.rotated_copy(3, 0)
        self.assertEqual(component_a.x1, component_b.y1)
        self.assertEqual(component_a.x2, component_b.y2)
        self.assertEqual(component_a.y1, component_b.x1)
        self.assertEqual(component_a.y2, component_b.x2)
        self.assertEqual(component_a.stretchable, component_b.stretchable)
        self.assertEqual(component_b.x1, 20)
        self.assertEqual(component_b.y1, 10)
        self.assertEqual(component_b.x2, 40)
        self.assertEqual(component_b.y2, 30)

        # Mirror
        component_b = component_a.rotated_copy(0, 1)
        self.assertEqual(component_a.x1, -component_b.x1)
        self.assertEqual(component_a.x2, component_b.x2)
        self.assertEqual(component_a.y1, component_b.y1)
        self.assertEqual(component_a.y2, component_b.y2)
        self.assertEqual(component_a.stretchable, component_b.stretchable)
        self.assertEqual(component_b.x1, -10)
        self.assertEqual(component_b.y1, 20)
        self.assertEqual(component_b.x2, 30)
        self.assertEqual(component_b.y2, 40)


if __name__ == "__main__":
    unittest.main()
