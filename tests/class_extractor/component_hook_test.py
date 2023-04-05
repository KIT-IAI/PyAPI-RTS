# LGPL-3.0 License
# Copyright (c) 2023 KIT-IAI-ESA

import unittest

from pyapi_rts.api.internals.hooks.component_hook import ComponentHook


class ExampleComponentHook(ComponentHook):
    """
    A simple ComponentHook for testing
    """
    def __init__(self):
        super().__init__()
        self.test_value = 0

    @classmethod
    def graph_connections(
        cls, components, pos_dict: dict, link_dict: dict
    ) -> list[tuple[str, str]]:
        """
        Hook method.
        """
        return [("1", "2")]


class ComponentHookTest(unittest.TestCase):
    """
    Test the component hook.
    """

    def test_component_hook(self):
        """
        Test the component hook.
        """
        self.assertEqual(ExampleComponentHook.graph_connections([], {}, {}), [('1', '2')])


if __name__ == "__main__":
    unittest.main()
