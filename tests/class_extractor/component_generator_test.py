# LGPL-3.0 License
# Copyright (c) 2023 KIT-IAI-ESA

import os
import pathlib
import unittest
import tempfile

from pyapi_rts.class_extractor.extracted.ext_component import ExtComponent
from pyapi_rts.class_extractor.extracted.ext_parameter import ExtParameter
from pyapi_rts.class_extractor.extracted.ext_parameter_coll import ExtParameterColl
from pyapi_rts.class_extractor.extracted.ext_rectangle import ExtRectangle
from pyapi_rts.class_extractor.generators.component_generator import ComponentGenerator
from pyapi_rts.class_extractor.readers.blocks.node_block import CompDefNode
from pyapi_rts.shared import NodeType
from pyapi_rts.shared.node_type import NodeIO


class ComponentGeneratorTest(unittest.TestCase):
    """
    Tests for the ComponentGenerator class.
    """

    def test_generator(self):
        """
        Tests the generator.
        """
        component = ExtComponent()
        component.set_type("Test")
        component.parameters.append(ExtParameter("TestParam", "Name", "INTEGER", 0))
        collection = ExtParameterColl("TestColl")
        collection.parameters.append(ExtParameter("TestParam2", "Name2", "INTEGER", 1))
        component.collections.append(collection)
        component.rectangle = ExtRectangle()

        comp_gen = ComponentGenerator(component)
        input_lines = """
        FOREACH_TYPE: {{TypeParam}} {{TypePath}}
        FOREACH_PARAM: {{name}} {{key}} {{TypeParam}}
        FOREACH_COLL: {{name}} {{TypeParam}}
        RECT_INIT:
        RECT_FUNC:
        DOCSTR:
        {{name}} {{TypeName}} {{name_param_key}}
        """
        new_lines = comp_gen.replace(input_lines.split("\n"))
        _, temp_file = tempfile.mkstemp()
        comp_gen.write_file(pathlib.Path(temp_file), new_lines)
        self.assertTrue(os.path.isfile(temp_file))
        for line in new_lines:
            self.assertFalse("{{" in line or "}}" in line)

    def test_merge(self):
        """
        Tests the mergin of two CompDefNodes
        """

        cdn1 = CompDefNode(
            "name", "$x", "$y", NodeIO.SHORT, NodeType.NC_LINKED, "link", "phase"
        )
        cdn2 = CompDefNode(
            "name", "$x", "$y", NodeIO.SHORT, NodeType.OTHER, "link", "phase"
        )
        ext_conn_point = cdn1.as_ext_conn_point()
        ext_conn_point2 = cdn2.as_ext_conn_point()
        ext_conn_point.merge(ext_conn_point2)
        self.assertEqual(ext_conn_point.name, "name")
        self.assertEqual(ext_conn_point.x, "$x")
        self.assertEqual(ext_conn_point.y, "$y")
        self.assertEqual(ext_conn_point.type, NodeType.NC_LINKED)
        self.assertEqual(ext_conn_point.link_name, "link")
        self.assertEqual(ext_conn_point.io, NodeIO.SHORT)
        # self.assertEqual(ext_conn_point.phase, "phase")

        cdn2 = CompDefNode(
            "name",
            "$x",
            "$y",
            NodeIO.SHORT,
            NodeType.NC_CONNECTED_LINKED,
            "link",
            "phase",
        )
        ext_conn_point2 = cdn2.as_ext_conn_point()
        ext_conn_point.merge(ext_conn_point2)
        self.assertEqual(ext_conn_point.type, NodeType.NC_CONNECTED_LINKED)


if __name__ == "__main__":
    unittest.main()
