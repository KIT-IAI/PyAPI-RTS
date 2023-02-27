# LGPL-3.0 License
# Copyright (c) 2023 KIT-IAI-ESA

import unittest

from pyapi_rts.generated.rtdsINDMdef import rtdsINDMdef


class LoadUnitsTest(unittest.TestCase):
    """
    Test for the loadunit calculations.
    """

    def test_indm(self):
        """
        Gets the load untes for _rtdds_INDM.def (24+ld1+ld2)
        """
        indm: rtdsINDMdef = rtdsINDMdef()
        self.assertEqual(indm.load_units, 24 + indm.ld1() + indm.ld2())


if __name__ == "__main__":
    unittest.main()
