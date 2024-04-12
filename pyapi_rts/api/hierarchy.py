# LGPL-3.0 License
# Copyright (c) 2023 KIT-IAI-ESA

import re

from pyapi_rts.api.internals.block import Block
from pyapi_rts.api.internals.blockreader import BlockReader
from pyapi_rts.api.component import Component
from pyapi_rts.generated.HIERARCHY import HIERARCHY

from pyapi_rts.api.container import Container


class Hierarchy(HIERARCHY, Container):
    """A component of type hierarchy, can contain other components."""

    _title_regex = re.compile(r"^HIERARCHY-START:\s?\n?$")
    # class_loader = ClassLoader()

    def __init__(self) -> None:
        Container.__init__(self, None)
        HIERARCHY.__init__(self)

    def get_box_type(self) -> int:
        """Returns the type of the box.

        :return: Type of the box
        :rtype: int
        """
        return self.get_by_key("Type").value

    def read_block(self, block: Block) -> None:
        """
        Reads a hierarchy block of a .dfx file

        :param block: Hierarchy block of a .dfx file
        :type block: Block
        """
        from pyapi_rts.api.group import Group
        import pyapi_rts.generated.class_loader as ClassLoader

        reader = BlockReader(block.lines)
        super().read_block(reader.current_block)  # Read the hierarchy component
        next_exists = reader.next_block()  # Move to start of components in hierarchy
        if not next_exists:
            return

        while True:

            if Hierarchy.check_title(reader.current_block.title):  # Read subhierarchy recursively
                sub_hier = Hierarchy()
                sub_hier.read_block(reader.current_block)
                self.add_component(sub_hier)
            elif Group.check_title(reader.current_block.title):  # Read subhierarchy recursively
                sub_hier = Group()
                sub_hier.read_block(reader.current_block)
                self.add_component(sub_hier)
            elif Component.check_title(reader.current_block.title):  # Read component
                c = ClassLoader.get_by_key(
                    reader.current_block.title.split("COMPONENT_TYPE=")[1][:-1].rstrip()
                )  # Create new component from typeId
                c.read_block(reader.current_block)
                self.add_component(c)

            if not reader.next_block():  # Stop if there are no more blocks
                break

    def block(self) -> list[str]:
        """Write the hierarchy to a .dfx block

        :return: Hierarchy block of a .dfx file
        :rtype: list[str]
        """
        lst = []
        lst.append("HIERARCHY-START:")
        lst += ["" + l for l in super().block()]
        for comp in self.get_components():
            # Add components and subhierarchies
            lst += ["" + l for l in comp.block()]
        lst.append("HIERARCHY-END:")
        return lst
