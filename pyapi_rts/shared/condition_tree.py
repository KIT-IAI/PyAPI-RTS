# LGPL-3.0 License
# Copyright (c) 2023 KIT-IAI-ESA


from pyapi_rts.shared import BoundingBox, ParameterCondition
from pyapi_rts.class_extractor.extracted.ext_connection_point import ExtConnectionPoint


class ConditionTreeNode:
    """A generic class for nodes in a condition tree."""

    def to_code(self) -> list[str]:
        raise NotImplementedError


class IfNode(ConditionTreeNode):
    """A condition tree node that has condition and contains a list of other nodes."""

    def __init__(self, condition) -> None:
        super().__init__()
        self.condition: ParameterCondition = condition
        """The condition of the node."""
        self.body: list[ConditionTreeNode] = []
        """The list of nodes contained in this node."""

    def to_code(self) -> list[str]:
        lines = [f"if {self.condition}.check(dictionary):"]
        for node_internal in self.body:
            lines += [f"    {l}" for l in node_internal.to_code()]
        if len(lines) == 1:
            lines.append("    pass")
        return lines

    def __repr__(self) -> str:
        return "IfNode"


class NewConditionTree(ConditionTreeNode):
    """A condition tree that contains an if branch, and optionally an else branch and multiple elif branches."""

    def __init__(self, if_branch) -> None:
        super().__init__()
        self.if_branch: IfNode = if_branch
        """The mandatory if branch of the tree, consisting of a single IfNode."""
        self.else_branch: list[ConditionTreeNode] = []
        """The optional else branch, consisting of a list of condition tree nodes."""
        self.elif_branches: list[IfNode] = []
        """The optional elif branches, consisting of a list of if nodes."""

    def to_code(self) -> list[str]:
        lines = self.if_branch.to_code()
        for branch in self.elif_branches:
            branch_lines = branch.to_code()
            branch_lines[0] = "el" + branch_lines[0]
            lines += branch_lines
        if self.else_branch:
            lines.append("else:")
            for node_else in self.else_branch:
                lines += [f"    {l}" for l in node_else.to_code()]
        return lines

    def __repr__(self) -> str:
        return "ConditionTree"


class BBNode(ConditionTreeNode):
    def __init__(self) -> None:
        super().__init__()
        self.bboxes: list[BoundingBox] = []

    def to_code(self) -> list[str]:
        return [f"bboxes += [{', '.join((bbox.init_code() for bbox in self.bboxes))}]"]

    def __repr__(self) -> str:
        return "BBNode"


class CPNode(ConditionTreeNode):
    def __init__(self) -> None:
        super().__init__()
        self.nodes: list[ExtConnectionPoint] = []

    def to_code(self) -> list[str]:
        result = []
        for cp in self.nodes:
            result.append(f'result["{cp.name}"] = {cp.component_init()}')
        return result

    def __repr__(self) -> str:
        return "CPNode"
