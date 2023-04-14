# LGPL-3.0 License
# Copyright (c) 2023 KIT-IAI-ESA

import pathlib
import unittest

import networkx as nx

from pyapi_rts.api import ComponentBox, Component, Draft, Hierarchy
from pyapi_rts.generated.rtdssharcsldBUSLABEL import rtdssharcsldBUSLABEL
from pyapi_rts.generated.rtdsudcDYLOAD import rtdsudcDYLOAD

PATH = pathlib.Path(__file__).parent.resolve()


class DraftVarTest(unittest.TestCase):
    """
    Tests for the draft var functionality
    """

    def test_draft_vars_init(self):
        """
        Tests if draft.get_draft_vars() returns the correct draft vars after reading a file.
        """
        draft = Draft()
        draft.read_file(PATH / "models/draftvar.dfx")

        # simple check that basics are working
        bus1 = draft.subsystems[0].search_by_name("BUS1")[0]
        self.assertEqual(bus1.get_by_key("VRate"), 230.0)

        draft_vars = draft.get_draft_vars()
        self.assertEqual(len(draft_vars), 3)

        self.assertIn("DV1", draft_vars)
        self.assertIn("DV2", draft_vars)
        self.assertIn("DV3", draft_vars)

    def test_draft_vars_eval(self):
        """
        Tests if draft.get_draft_vars() returns the correct draft vars after reading a file.
        """
        draft = Draft()
        draft.read_file(PATH / "models/draftvar.dfx")

        draft_vars = draft.get_draft_vars()

        box1: Hierarchy = draft.subsystems[0].search_by_name("box1")[0]
        dload1: rtdsudcDYLOAD = draft.subsystems[0].search_by_name("DLOAD1")[0]

        self.assertEqual(box1.get_by_key("DESC1", draft_vars=draft_vars), "Hello")
        self.assertEqual(dload1.get_by_key("Pinit", draft_vars=draft_vars), 2.0)
        self.assertEqual(dload1.get_by_key("Qmin", draft_vars=draft_vars), 3)

    def test_draft_vars_eval_enumeration(self):
        """
        Tests if draft.get_draft_vars() returns the correct draft vars after reading a file.
        """
        draft = Draft()
        draft.read_file(PATH / "models/draftvar.dfx")
        draft_vars = draft.get_draft_vars()

        bus1: rtdssharcsldBUSLABEL = draft.subsystems[0].search_by_name("BUS1")[0]
        box1: Hierarchy = draft.subsystems[0].search_by_name("box1")[0]

        self.assertEqual(box1.get_by_key("DESC2", draft_vars=draft_vars), "Hello")
        self.assertEqual(bus1.get_by_key("NA", draft_vars=draft_vars), "Hello")

    def test_draft_vars_set(self):
        """
        Tests if draft.get_draft_vars() returns the correct draft vars after reading a file.
        """
        draft = Draft()
        draft.read_file(PATH / "models/draftvar.dfx")
        draft_vars = draft.get_draft_vars()

        dload1: rtdsudcDYLOAD = draft.subsystems[0].search_by_name("DLOAD1")[0]

        dload1.PARAMETERS.freq.set_draft_var("$DV3")
        self.assertEqual(dload1.get_by_key("freq", draft_vars=draft_vars), 3)

        with self.assertRaises(TypeError):
            dload1.PARAMETERS.cc.set_draft_var("$DV3")

        with self.assertRaises(ValueError):
            dload1.PARAMETERS.freq.set_str("$DV2")

    def test_draft_vars_modify(self):
        """
        Tests if draft.get_draft_vars() returns the correct draft vars after reading a file.
        """
        draft = Draft()
        draft.read_file(PATH / "models/draftvar.dfx")
        draft_vars = draft.get_draft_vars()

        dload1: rtdsudcDYLOAD = draft.subsystems[0].search_by_name("DLOAD1")[0]
        self.assertEqual(dload1.get_by_key("Qmin", draft_vars=draft_vars), 3)

        dv3: Component = draft.subsystems[0].search_by_name("DV3")[0]
        dv3.set_by_key("Value", 5)

        self.assertEqual(dload1.get_by_key("Qmin", draft_vars=draft_vars), 5)


if __name__ == "__main__":
    unittest.main()
