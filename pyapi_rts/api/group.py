# LGPL-3.0 License
# Copyright (c) 2023 KIT-IAI-ESA

import re
from typing import Any

from pyapi_rts.api.internals.block import Block
from pyapi_rts.api.internals.blockreader import BlockReader
from pyapi_rts.api.component import Component
from pyapi_rts.api.component_box import ComponentBox


class Group(Component, ComponentBox):
    """
    Group of components
    """

    _COMPONENT_TYPE_NAME = "GROUP"
    _title_regex = re.compile(r"^GROUP-START:\s?\n?$")

    def __init__(self) -> None:
        super().__init__(self._COMPONENT_TYPE_NAME)

    def get_box_type(self) -> int:
        return self.parent.get_box_type()

    def read_block(self, block: Block, check=True):
        import pyapi_rts.generated.class_loader as ClassLoader
        from pyapi_rts.api.hierarchy import Hierarchy

        if not self.check_title(block.title):
            raise Exception(
                "Group read_block() called with malformed title: " + block.lines[0]
            )
        reader = BlockReader(block.lines)
        super().read_block(reader.current_block, False)  # Read the group component
        next_exists = reader.next_block()  # Move to start of components in group
        if not next_exists:
            return

        while True:

            if Group.check_title(
                reader.current_block.title
            ):  # Read subhierarchy recursively
                sub_hier = Group()
                sub_hier.read_block(reader.current_block)
                self.add_component(sub_hier)
            elif Hierarchy.check_title(
                reader.current_block.title
            ):  # Read subhierarchy recursively
                sub_hier = Hierarchy()
                sub_hier.read_block(reader.current_block)
                self.add_component(sub_hier)
            elif Component.check_title(reader.current_block.title):  # Read component
                new_component = ClassLoader.get_by_key(
                    reader.current_block.title.split("COMPONENT_TYPE=")[1].rstrip()
                )  # Create new component from typeId
                new_component.read_block(reader.current_block)
                self.add_component(new_component)

            if not reader.next_block():  # Stop if there are no more blocks
                break

    def block(self) -> list[str]:
        """
        Writes the hierarchy to a .dfx block

        :return: Hierarchy block of a .dfx file
        :rtype: list[str]
        """
        lst = []
        lst.append("GROUP-START:")
        lst += ["" + l for l in super().block()[:2]]  # Group component
        for comp in self.get_components():
            # Add components and subhierarchies
            lst += ["" + l for l in comp.block()]
        lst.append("GROUP-END:")
        return lst

    def _read_parameters(self, dictionary: dict[str, str]) -> None:
        return

    def _write_parameters(self) -> list[str]:
        return []

    def as_dict(
        self,
    ) -> dict[str, Any]:
        return {}

    def get_by_key(self, key: str) -> Any | None:
        return None

    def has_key(self, key: str) -> bool:
        return False

    def set_by_key(self, key: str, value: Any) -> bool:
        return False
