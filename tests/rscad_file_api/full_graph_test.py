# LGPL-3.0 License
# Copyright (c) 2023 KIT-IAI-ESA

import pathlib
import unittest


from pyapi_rts.api import Draft
from tests.graph_visualization import visualize_graph

PATH = pathlib.Path(__file__).parent.absolute().resolve()


class DraftTest(unittest.TestCase):
    """
    Tests for the full graph generation
    """

    # TODO: this is not a real test yet
    def test_generate_full_graph(self):
        """
        Tests the composition of all subsystem connection graphs.
        """
        draft = Draft()
        draft.read_file(PATH / "models" / "full_graph.dfx")
        # draft.read_file(PATH / "models" / "tmp" / "KIT20KV_v2020.dfx")
        components = draft.get_components(with_groups=True)
        self.assertEqual(len(components), 81)

        # subsys = draft.subsystems[0]
        # subsys_graph, _ = subsys.generate_full_graph()
        # visualize_graph(subsys_graph)

        full_graph = draft.get_graph()
        # visualize_graph(full_graph)

        self.assertEqual(full_graph.number_of_nodes(), 81)


if __name__ == "__main__":
    unittest.main()
