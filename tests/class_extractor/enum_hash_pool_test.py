# LGPL-3.0 License
# Copyright (c) 2023 KIT-IAI-ESA

import pathlib
import unittest
from pyapi_rts.class_extractor.extracted.ext_component import ExtComponent
from pyapi_rts.class_extractor.extracted.ext_enum_parameter import ExtEnumParameter

from pyapi_rts.class_extractor.enum_hash_pool import EnumHashPool

PATH = pathlib.Path(__file__).parent.resolve()


class EnumHashPoolTest(unittest.TestCase):
    """
    Tests for the EnumHashPool class.
    """

    def test_load_hash_pool(self):
        """
        Load HashPool from file.
        """
        hash_pool = EnumHashPool()
        self.assertFalse(hash_pool.load_from_file("doesnotexist.txt"))
        hash_pool.load_from_file(PATH / "enum_pool.txt")

        color_hash = hash_pool.get_hash("color")

        hash_pool2 = EnumHashPool()
        hash_pool2.load_from_file(PATH / "enum_pool.txt")
        self.assertEqual(len(hash_pool.pool), 4)
        self.assertEqual(hash_pool.pool[color_hash].name, "color")
        self.assertEqual(hash_pool.pool[color_hash].options_hash, color_hash)

    def test_add_hash_pool(self):
        """
        Tests adding a new enum to the pool.
        """
        hash_pool = EnumHashPool()
        hash_pool.load_from_file(PATH / "enum_pool.txt")
        self.assertEqual(len(hash_pool.pool), 4)

        hash_pool.add(ExtComponent(), ExtEnumParameter("test"))
        self.assertEqual(len(hash_pool.pool), 5)  # No hash collision

        hash_pool.add(ExtComponent(), ExtEnumParameter("test"))
        self.assertEqual(len(hash_pool.pool), 5)  # Hash collision

    def test_get_hash(self):
        """
        Tests getting the hash of an enum.
        """
        hash_pool = EnumHashPool()
        component = ExtComponent()
        hash_pool.add(component, ExtEnumParameter("test"))
        self.assertEqual(
            hash_pool.get_hash("test"),
            hash_pool.pool[hash_pool.get_hash("test")].options_hash,
        )

    def test_rename(self):
        """
        Tests the automatic renaming of enums with the same name but different hashes.
        """
        hash_pool = EnumHashPool()
        hash_pool.load_from_file(PATH / "enum_pool.txt")
        self.assertEqual(len(hash_pool.pool), 4)
        enum = ExtEnumParameter("color")
        enum.options.append("new_option")
        hash_pool.add(ExtComponent(), enum)
        self.assertEqual(len(hash_pool.pool), 5)
        self.assertEqual(hash_pool.pool[enum.options_hash].name, "color1")
        enum2 = ExtEnumParameter("color")
        enum2.options.append("new_option2")
        hash_pool.add(ExtComponent(), enum2)
        self.assertEqual(len(hash_pool.pool), 6)
        self.assertEqual(hash_pool.pool[enum2.options_hash].name, "color2")


if __name__ == "__main__":
    unittest.main()
