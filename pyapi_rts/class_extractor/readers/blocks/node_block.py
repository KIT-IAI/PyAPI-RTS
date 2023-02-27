# LGPL-3.0 License
# Copyright (c) 2023 KIT-IAI-ESA

import re
from typing import Union

from pyapi_rts.class_extractor.readers.lines import NodeConditionLineReader
from pyapi_rts.class_extractor.extracted import ExtConnectionPoint
from pyapi_rts.shared.condition_tree import CPNode, IfNode, NewConditionTree
from pyapi_rts.shared.node_type import NodeType, NodeIO

from .base_block_reader import BaseBlockReader


class NodeBlock(BaseBlockReader):
    """
    Reads the NODES block from the definition file.
    """

    def __init__(self) -> None:
        super().__init__()
        self.reg = re.compile(r"NODES:.*")
        self.node_reg = re.compile(
            r"\s*(\S+)\s+(-?\d+|\$\S+)[\s,]+(-?\d+|\$\S+)(?:\s+(\S+)"
            + r"(?:\s+(PHASE=\S+))?)?(?:\s+(NAME_CONNECTED\S*)\s+(\S+)\s*)?\n?"
        )
        self.results["nodes"] = []
        self.line_reader = NodeConditionLineReader()

    def read(self, lines: list[str]) -> None:
        blocks = []
        active_block = blocks
        stack = []

        for line in (l.strip() for l in lines[1:]):
            if len(line) == 0:
                continue

            if self.line_reader.is_if_line(line):
                # print("IF: start new condition tree")
                if_block = IfNode(self.line_reader.get_condition(line)[1])
                cond_tree = NewConditionTree(if_block)

                if active_block is not None:
                    active_block.append(cond_tree)
                else:
                    blocks.append(cond_tree)
                active_block = if_block.body
                stack.append(cond_tree)

            elif self.line_reader.is_else_line(line):
                # print("ELSE: add new lines to current_tree.else_branch")
                active_block = cond_tree.else_branch

            elif self.line_reader.is_elif_line(line):
                # print("ELIF: add new IfBlock to current_tree.elif_branches")

                if_block = IfNode(self.line_reader.get_condition(line)[1])
                cond_tree.elif_branches.append(if_block)
                active_block = if_block.body

            elif self.line_reader.is_end_line(line):
                # print("END: close current_tree; add following lines to its parent")

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

            else:
                result = self._read_line(line)
                if result is not None:
                    if not active_block or not isinstance(active_block[-1], CPNode):
                        # block is empty -> create new CPNode
                        cpnode = CPNode()
                        cpnode.nodes.append(result.as_ext_conn_point())
                        active_block.append(cpnode)
                    else:
                        active_block[-1].nodes.append(result.as_ext_conn_point())

        self.write_result("nodes", blocks)

    def _read_line(self, line: str) -> Union["CompDefNode", None]:
        match = self.node_reg.match(line)
        if bool(match):
            match_groups = match.groups()
            if self.__check_int_bound_param(
                match_groups[1]
            ) and self.__check_int_bound_param(match_groups[2]):
                return CompDefNode(
                    match_groups[0],
                    match_groups[1],
                    match_groups[2],
                    self.__check_node_io(match_groups[3]),
                    self.__check_node_type(match_groups[5]),
                    match_groups[6].replace("$", "")
                    if match_groups[6] is not None
                    else "",
                    match_groups[4] if match_groups[4] is not None else "",
                )

    def __check_node_type(self, _type: str) -> "NodeType":
        """
        Determines the node type.

        :param _type: Node type name
        :type _type: str
        :return: NodeType object
        :rtype: NodeType
        """
        if _type is None:
            return NodeType.OTHER
        type_list = list(filter((lambda x: x.value in _type), NodeType))
        if len(type_list) == 0:
            return NodeType.OTHER
        return type_list[0]

    def __check_node_io(self, _type: str) -> "NodeIO":
        """
        Determines the node IO.

        :param _type: Node IO name
        :type _type: str
        :return: NodeIO object
        :rtype: NodeIO
        """
        if _type is None:
            return NodeIO.UNDEFINED
        type_list = list(filter((lambda x: x.value in _type), NodeIO))
        if len(type_list) == 0:
            return NodeIO.UNDEFINED
        return type_list[0]

    def __check_int_bound_param(self, param: str) -> bool:
        """
        Checks if the parameter is an integer.

        :param param: Parameter name
        :type param: str
        :return: True if the parameter is an integer
        :rtype: bool
        """
        return (
            (param.startswith("-") and param[1:].isdigit())
            or param.isdigit()
            or param.startswith("$")
        )


class CompDefNode:
    """
    A node read from the node block of a component definition.
    """

    def __init__(
        self,
        name: str,
        x: str,
        y: str,
        io: NodeIO,
        _type: NodeType,
        link_name: str,
        phase: str,
    ) -> None:
        """
        Initializes the node.

        :param name: Node name
        :type name: str
        :param x: X coordinate
        :type x: str
        :param y: Y coordinate
        :type y: str
        :param io: IO type
        :type io: NodeIO
        :param _type: Node type
        :type _type: NodeType
        :param link_name: Link name
        :type link_name: str
        :param phase: Phase
        :type phase: str
        """
        self.name: str = name
        self.x: str = x
        self.y: str = y
        self.io: NodeIO = io
        self.type: NodeType = _type
        self.link_name: str = link_name
        self.phase: str = phase

    def as_ext_conn_point(self) -> ExtConnectionPoint:
        """
        Returns the node as an ExtConnectionPoint object.

        :return: Node converted to an ExtConnectionPoint
        :rtype: ExtConnectionPoint
        """
        ext_conn_point = ExtConnectionPoint()
        try:
            ext_conn_point.name = self.name
            ext_conn_point.x = self.x if str(self.x).startswith("$") else int(self.x)
            ext_conn_point.y = self.y if str(self.y).startswith("$") else int(self.y)
            ext_conn_point.type = self.type
            ext_conn_point.link_name = self.link_name
            ext_conn_point.io = self.io
        except ValueError as value_error:
            print("Error: " + self.name)
            raise ValueError from value_error
        return ext_conn_point
