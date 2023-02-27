# LGPL-3.0 License
# Copyright (c) 2023 KIT-IAI-ESA

import re

from pyapi_rts.class_extractor.readers.lines import GraphicsConditionLineReader
from pyapi_rts.class_extractor.graphics_parsing import (
    ENDNOMIRROR,
    ENDNOROTATE,
    GRAPHICS_FUNCTIONS,
    GRAPHICS_REGEXS,
    GRAPHICS_REGEXS_EXT,
    NOMIRROR,
    NOROTATE,
)
from pyapi_rts.shared import BoundingBox
from pyapi_rts.shared.condition_tree import BBNode, IfNode, NewConditionTree
from .base_block_reader import BaseBlockReader


class GraphicsBlock(BaseBlockReader):
    """
    Reads the GRAPHICS block from the definition file.
    """

    def __init__(self, incl_macros: bool = True) -> None:
        super().__init__()
        self.reg = re.compile(r"GRAPHICS:.*")
        self.results["bbox"] = []
        self.line_reader = GraphicsConditionLineReader(incl_macros)
        self.incl_macros = incl_macros

    def read(self, lines: list[str]) -> None:
        if self.incl_macros:
            from pyapi_rts.generated.graphics_macros import MACRO_FUNCTIONS, MACRO_REGEXS

        blocks = []
        active_block = blocks
        stack = []
        bboxes_int: list[tuple] = []
        bboxes_other: list[BoundingBox] = []

        norotate = False
        nomirror = False

        # don't throw away first line; could still contain information
        lines[0] = re.sub(r"GRAPHICS:\s*", "", lines[0])
        for line in (l.strip() for l in lines):
            if len(line) == 0:
                continue

            split_line = self.line_reader.get_line_components(line)
            for line in split_line:

                if self.line_reader.is_if_line(line):
                    # print("IF: start new condition tree")
                    if_block = IfNode(self.line_reader.get_condition(line)[1])
                    cond_tree = NewConditionTree(if_block)

                    # add accumulated bboxes to last active block
                    bbblock = self._create_bbblock(bboxes_int, bboxes_other)

                    if active_block is not None:
                        if bbblock.bboxes:
                            active_block.append(bbblock)
                        active_block.append(cond_tree)
                    else:
                        if bbblock.bboxes:
                            blocks.append(bbblock)
                        blocks.append(cond_tree)
                    active_block = if_block.body
                    stack.append(cond_tree)
                    # reset bbox collection
                    bboxes_int = []
                    bboxes_other = []

                elif self.line_reader.is_else_line(line):
                    # print("ELSE: add new lines to current_tree.else_branch")
                    # add accumulated bboxes to last active block
                    bbblock = self._create_bbblock(bboxes_int, bboxes_other)
                    if bbblock.bboxes:
                        active_block.append(bbblock)

                    active_block = cond_tree.else_branch
                    # reset bbox collection
                    bboxes_int = []
                    bboxes_other = []

                elif self.line_reader.is_elif_line(line):
                    # print("ELIF: add new IfBlock to current_tree.elif_branches")
                    # add accumulated bboxes to last active block
                    bbblock = self._create_bbblock(bboxes_int, bboxes_other)
                    if bbblock.bboxes:
                        active_block.append(bbblock)

                    if_block = IfNode(self.line_reader.get_condition(line)[1])
                    cond_tree.elif_branches.append(if_block)
                    active_block = if_block.body
                    # reset bbox collection
                    bboxes_int = []
                    bboxes_other = []

                elif self.line_reader.is_end_line(line):
                    # print("END: close current_tree; add following lines to its parent")
                    # add accumulated bboxes to last active block
                    bbblock = self._create_bbblock(bboxes_int, bboxes_other)
                    if bbblock.bboxes:
                        active_block.append(bbblock)

                    stack.pop()
                    if len(stack) == 0:  # we are on top level now
                        active_block = blocks  # not sure about this...
                    else:
                        cond_tree: NewConditionTree = stack[-1]
                        if cond_tree.else_branch:
                            active_block = cond_tree.else_branch
                        elif cond_tree.elif_branches:
                            active_block = cond_tree.elif_branches[-1].body
                        else:
                            active_block = cond_tree.if_branch.body
                    # reset bbox collection
                    bboxes_int = []
                    bboxes_other = []

                else:
                    # print("No condition line -> parse and add to current BBBlock")
                    readable = False

                    if NOROTATE.search(line):
                        norotate = True
                        readable = True
                    elif ENDNOROTATE.search(line):
                        norotate = False
                        readable = True
                    if NOMIRROR.search(line):
                        nomirror = True
                        readable = True
                    elif ENDNOMIRROR.search(line):
                        nomirror = False
                        readable = True

                    for key, reg in GRAPHICS_REGEXS.items():
                        for match in reg.findall(line):
                            readable = True
                            bbox = GRAPHICS_FUNCTIONS[key](match, norotate, nomirror)
                            if isinstance(bbox, BoundingBox):
                                bboxes_other.append(bbox)
                            elif bbox:
                                bboxes_int.append(bbox)

                    for key, reg in GRAPHICS_REGEXS_EXT.items():
                        for match in reg.findall(line):
                            readable = True

                    if self.incl_macros:
                        for key, reg in MACRO_REGEXS.items():
                            for match in reg.findall(line):
                                readable = True
                                bbox = MACRO_FUNCTIONS[key](match, norotate, nomirror)
                                if isinstance(bbox, BoundingBox):
                                    bboxes_other.append(bbox)
                                elif bbox:
                                    bboxes_int.append(bbox)
                    # if not readable:
                    #     print(f"not readable: {line.strip()}")

        if bboxes_int or bboxes_other:
            bbblock = self._create_bbblock(bboxes_int, bboxes_other)
            active_block.append(bbblock)

        self.write_result("bbox", blocks)

    def _calc_bbox(self, bboxes: list[tuple]) -> BoundingBox | None:
        if bboxes:
            x1 = min(bboxes, key=lambda x: x[0])[0]
            y1 = min(bboxes, key=lambda x: x[1])[1]
            x2 = max(bboxes, key=lambda x: x[2])[2]
            y2 = max(bboxes, key=lambda x: x[3])[3]
            return BoundingBox(x1, y1, x2, y2, bboxes[0][4], bboxes[0][5])

    def _create_bbblock(self, bboxes_int, bboxes_other):
        bbblock = BBNode()
        bboxes_int_sorted = {
            (True, True): [],
            (True, False): [],
            (False, True): [],
            (False, False): []
        }
        for bbox in bboxes_int:
            bboxes_int_sorted[(bbox[4], bbox[5])].append(bbox)

        for bboxes in bboxes_int_sorted.values():
            if bboxes:
                bbblock.bboxes.append(self._calc_bbox(bboxes))
        bbblock.bboxes += bboxes_other
        return bbblock
