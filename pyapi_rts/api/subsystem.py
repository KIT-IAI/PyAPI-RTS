# LGPL-3.0 License
# Copyright (c) 2023 KIT-IAI-ESA

from enum import Enum
import re
from typing import Any

from pyapi_rts.api.component import Component
from pyapi_rts.api.component_box import ComponentBox
from pyapi_rts.api.internals.block import Block
from pyapi_rts.api.internals.blockreader import BlockReader
from pyapi_rts.api.internals.dfxblock import DfxBlock
from pyapi_rts.api.group import Group
from pyapi_rts.api.hierarchy import Hierarchy
import pyapi_rts.generated.class_loader as ClassLoader


class SubsystemPrintLayout(Enum):
    PORTRAIT = "PORTRAIT"
    LANDSCAPE = "LANDSCAPE"


class SubsystemPaperType(Enum):
    LEGAL = "LEGAL"
    LETTER = "LETTER"
    LEDGER = "LEDGER"
    W11_7_H17 = "W11_7_H17"
    A3 = "A3"
    A4 = "A4"
    A5 = "A5"
    B4 = "B4"
    ANSI_C = "ANSI_C"
    ANSI_D = "ANSI_D"
    ANSI_E = "ANSI_E"


class Subsystem(DfxBlock, ComponentBox):
    """RSCAD subsystem, a canvas with components on it."""

    _title_regex = re.compile(r"^SUBSYSTEM-START:\s?\n?$")

    def __init__(
        self,
        draft: Any,
        number: int,
        canvas_size_x: int = 3000,
        canvas_size_y: int = 2000,
        print_layout: SubsystemPrintLayout = SubsystemPrintLayout.PORTRAIT,
        paper_type: SubsystemPaperType = SubsystemPaperType.LETTER,
    ) -> None:
        self.tab_name: str = ""
        self.number: int = number
        self.canvas_size_x: int = canvas_size_x
        self.canvas_size_y: int = canvas_size_y
        self.print_layout: SubsystemPrintLayout = print_layout
        self.paper_type: SubsystemPaperType = paper_type
        # self._class_loader: ClassLoader = ClassLoader()
        super().__init__(draft)

    def read_block(self, block: Block) -> None:
        """Read a subsystem block from a DFX file

        :param block: A subsystem block
        :type block: list[str]
        """
        self._read_info(block)
        self._read_components(block)

    def _read_info(self, block: Block) -> None:
        """Read the subsystem information from the .dfx file

        :param block: A subsystem block from a .dfx file
        :type block: list[str]
        """
        self.tab_name = block.lines[0].split("SUBSYSTEM-TAB-NAME: ")[-1].strip()
        if self.tab_name.strip() == "":
            self.tab_name = "SS #" + str(self.number)
        canvas_size = block.lines[1].split("SUBSYSTEM-CANVAS-SIZE:")[-1].split(",")
        self.canvas_size_x = int(canvas_size[0])
        self.canvas_size_y = int(canvas_size[1])
        self.print_layout = SubsystemPrintLayout[
            block.lines[2].split("SUBSYSTEM-PRINT-LAYOUT:")[-1].strip()
        ]
        self.paper_type = SubsystemPaperType[
            block.lines[3].split("SUBSYSTEM-PAPER-TYPE:")[-1].strip()
        ]

    def block(self) -> list[str]:
        """Writes the subsystem to a .dfx file

        :return: A list of strings representing the subsystem block
        :rtype: list[str]
        """
        lst = []
        lst.append("SUBSYSTEM-START:")
        lst.append(f"SUBSYSTEM-TAB-NAME: {self.tab_name}")
        lst.append(f"SUBSYSTEM-CANVAS-SIZE:{self.canvas_size_x},{self.canvas_size_y}")
        lst.append(f"SUBSYSTEM-PRINT-LAYOUT:{self.print_layout.value}")
        lst.append(f"SUBSYSTEM-PAPER-TYPE:{self.paper_type.value}")
        lst.append("SUBSYSTEM-COMPONENTS:")
        for comp in self.get_components():
            lst += comp.block()
        lst.append("SUBSYSTEM-END:")
        return lst

    def _read_components(self, block: Block) -> None:
        """Reads the components in the subsystem from the .dfx file

        :param block: The block describing the subsystem
        :type block: Block
        """
        reader = BlockReader(block.lines)
        comp: Component
        while reader.current_block is not None:
            if Hierarchy.check_title(reader.current_block.title):
                comp = Hierarchy()
                comp.read_block(reader.current_block)
                self.add_component(comp)
            elif Group.check_title(reader.current_block.title):
                comp = Group()
                comp.read_block(reader.current_block)
                self.add_component(comp)
            elif Component.check_title(reader.current_block.title):
                comp = ClassLoader.get_by_key(
                    reader.current_block.title.split("COMPONENT_TYPE=")[1][:-1].rstrip()
                )
                comp.read_block(reader.current_block)
                self.add_component(comp)

            if not reader.next_block():
                break
