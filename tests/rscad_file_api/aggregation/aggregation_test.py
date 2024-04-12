# LGPL-3.0 License
# Copyright (c) 2023 KIT-IAI-ESA

import os
import pathlib
import unittest

from pyapi_rts.api import Draft, Component
from pyapi_rts.generated.lfrtdssharcsldSHUNTCAP import lfrtdssharcsldSHUNTCAP
from pyapi_rts.generated.rtdsudcDYLOAD import rtdsudcDYLOAD


PATH = pathlib.Path(__file__).parent.resolve()


def sum_by_key(cs: list[Component], key: str) -> float:
    return sum(map((lambda c: c.get_by_key(key)), cs))


class AggregationTest(unittest.TestCase):
    """
    Tests the aggregation of components with an example.
    """

    def test_kit_aggregation(self):
        """
        Test component aggeration with an example.
        """
        draft = Draft()
        draft.read_file(PATH / "kit_aggregation_grouped.dfx")
        self.assertEqual(len(draft.subsystems), 1)
        self.assertEqual(len(draft.get_components()), 172)
        B123_4_400V = draft.subsystems[0].search_by_name("B123_4_400V")[0]

        # Get relevant components
        connected_to = draft.subsystems[0].get_connected_to(B123_4_400V, clone=False)
        dyloads = list(
            filter(
                (lambda c: isinstance(c, rtdsudcDYLOAD)),
                connected_to,
            )
        )
        self.assertEqual(len(dyloads), 5)
        shunts = list(
            filter(
                (lambda c: isinstance(c, lfrtdssharcsldSHUNTCAP)),
                connected_to,
            )
        )
        self.assertEqual(len(shunts), 4)

        graph, _ = draft.subsystems[0].get_graph()

        dyl: rtdsudcDYLOAD = dyloads[0].duplicate()
        dyl.set_by_key("Qinit", sum_by_key(dyloads, "Qinit"))
        dyl.set_by_key("Pinit", sum_by_key(dyloads, "Pinit"))
        draft.subsystems[0].update_component(dyl)
        for dyload in dyloads[1:]:
            for neighbor in graph.neighbors(dyload.uuid):
                # Remove connected BUS and WIRE
                draft.subsystems[0].remove_component(neighbor, False)
            draft.subsystems[0].remove_component(dyload.uuid, False)

        shunt: lfrtdssharcsldSHUNTCAP = shunts[0].duplicate()
        shunt.set_by_key("CuF", sum_by_key(shunts, "CuF"))
        draft.subsystems[0].update_component(shunt)
        for shunt in shunts[1:]:
            draft.subsystems[0].remove_component(shunt.uuid, False)
            for neighbor in graph.neighbors(shunt.uuid):
                # Remove connected BUS
                draft.subsystems[0].remove_component(neighbor, False)

        # Clean up WIRELABELs
        full_graph = draft.generate_full_graph()
        for wirelabel in draft.get_components_by_type("wirelabel", recursive=False):
            wl_uuid = wirelabel.uuid
            if len(list(full_graph.neighbors(wl_uuid))) == 1:
                # Not connected to anything, remove
                draft.subsystems[0].remove_component(wl_uuid)

        draft.write_file(PATH / "out.dfx")
        self.assertEqual(len(draft.get_components()), 142)
        self.assertAlmostEqual(dyl.PANDQSETTINGS.Qinit.value, 0.14555)
        self.assertAlmostEqual(dyl.PANDQSETTINGS.Pinit.value, 0.58098)
        self.assertAlmostEqual(shunt.CONFIGURATION.CuF.value, 1989.437)

        os.remove(PATH / "out.dfx")


if __name__ == "__main__":
    unittest.main()
