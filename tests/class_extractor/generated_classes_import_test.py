# LGPL-3.0 License
# Copyright (c) 2023 KIT-IAI-ESA

import unittest
import pyapi_rts.generated.class_loader as ClassLoader


class GeneratedClassesImportTest(unittest.TestCase):
    """
    Tries to import the generated classes, asserts that no error is raised.
    """

    def test_import(self):
        """
        Tries to import the generated classes, asserts that no error is raised.
        """
        # class_ids = copy.deepcopy(list())
        for class_id in ClassLoader.COMPONENT_CLASS_DICT.keys():
            ClassLoader.get_by_key(class_id)


if __name__ == "__main__":
    unittest.main()
