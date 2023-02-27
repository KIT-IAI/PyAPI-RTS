# LGPL-3.0 License
# Copyright (c) 2023 KIT-IAI-ESA

import tempfile
import unittest
import pathlib

from pyapi_rts.api.draft import Draft
from pyapi_rts.api.lark.tli_transformer import (
    TliDataType,
    TliFile,
    TliRtdsMetadata,
    TliSection,
)

PATH = pathlib.Path(__file__).parent.absolute()


class LarkTliTest(unittest.TestCase):
    """
    Tests for the lark parser for .tli files
    """

    def test_simple_tli(self):
        """
        Parses a simple *.tli file and transforms it to a TliFile object.
        """
        draft = Draft()
        draft.path = PATH / "models/non_existing.dfx"

        tli_file = draft.get_tline_constants("simple")
        self.assertEqual(
            tli_file.get("RLC Options/Zero Sequence Series Resistance"), "0.0891"
        )

        self.assertEqual(tli_file.get("RLC Options/Number of Phases"), "3")

        self.assertEqual(len(tli_file.sections), 3)
        self.assertEqual(len(tli_file.sections[2].dictionary), 8)

        self.assertEqual(tli_file.get("REVISION", TliDataType.METADATA), "2")

    def test_t250_tli(self):
        """
        Tests the parser for the t250x*.tli files.
        """

        draft = Draft()
        draft.path = PATH / "models/tli/non_existing.dfx"

        t250x3_file = draft.get_tline_constants("t250x3")
        self.assertEqual(
            t250x3_file.get("Line Constants Tower").metadata[0].key, "ROW_OFFSET"
        )
        self.assertEqual(t250x3_file.get("Line Summary/Line Length"), "250.0")

        t250x6_file = draft.get_tline_constants("t250x6")
        self.assertEqual(
            t250x6_file.get("Line Constants Tower").metadata[0].key, "ROW_OFFSET"
        )
        self.assertEqual(t250x6_file.get("Line Summary/Number of Conductors"), "6")

    def test_tli_file_get(self):
        """
        Tests the get function of TliFile and TliSection.
        """
        draft = Draft()
        draft.path = PATH / "models/non_existing.dfx"

        tli_file = draft.get_tline_constants("simple")
        self.assertEqual(
            tli_file.get("RLC Options", TliDataType.SECTION).title_key, "RLC Options"
        )
        with self.assertRaises(ValueError) as _:
            tli_file.get("RLC Options", TliDataType.METADATA)

        self.assertEqual(
            tli_file.get(
                "RLC Options/Zero Sequence Series Resistance", TliDataType.DATA
            ),
            "0.0891",
        )

        # Test data and metadata name collision
        draft.path = PATH / "models/tli/non_existing.dfx"
        tli_file = draft.get_tline_constants("get_test")
        self.assertEqual(
            tli_file.get("Test Section", TliDataType.SECTION).title_key, "Test Section"
        )
        self.assertEqual(tli_file.get("Test Section/testkey", TliDataType.DATA), "2.0")
        self.assertEqual(
            tli_file.get("Test Section/testkey", TliDataType.METADATA), "1.0"
        )

        self.assertEqual(tli_file.get("Test Section/testkey", TliDataType.ANY), "2.0")
        self.assertEqual(tli_file.get("Test Section/TESTKEY", TliDataType.ANY), "1.0")

        self.assertEqual(tli_file.get("Section Two/Sub Section/key"), "test")

    def test_tli_write(self):
        """
        Tests the write() methods for TliFile and TliSection.
        """
        tli_file: TliFile = TliFile()
        tli_file.sections = [TliSection("Test Section")]
        tli_file.sections[0].dictionary = {
            "testkey": "2.0",
            "testkey2": "3.0",
        }

        tli_file.sections[0].sections = [TliSection("Sub Section")]
        tli_file.sections[0].sections[0].dictionary = {"key": "test"}
        tli_file.sections[0].sections[0].metadata = [
            TliRtdsMetadata("INNER_META", "meta")
        ]

        tli_file.metadata = [TliRtdsMetadata("testkey", "1.0")]

        temp_dir = pathlib.Path(tempfile.mkdtemp())
        temp_file = temp_dir / "test.tli"
        tli_file.write_file(temp_file)
        self.assertTrue(temp_file.exists())

        tli_file2 = TliFile.from_file(temp_file)
        self.assertEqual(tli_file2.get("Test Section/testkey"), "2.0")
        self.assertEqual(tli_file2.get("Test Section/testkey2"), "3.0")

        self.assertEqual(tli_file2.get("Test Section/Sub Section/key"), "test")
        self.assertEqual(tli_file2.get("Test Section/Sub Section/INNER_META"), "meta")

        self.assertEqual(tli_file2.get("testkey", TliDataType.METADATA), "1.0")


if __name__ == "__main__":
    unittest.main()
