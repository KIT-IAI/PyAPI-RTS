# LGPL-3.0 License
# Copyright (c) 2023 KIT-IAI-ESA

from pyapi_rts.shared import NodeType, NodeIO


class ExtConnectionPoint:
    """
    A connection point of a rectangle.
    """

    def __init__(self) -> None:
        """
        Initializes the ExtConnectionPoint object.
        """
        #: X position of the connection point relative to the center.
        self.x: int | str = 0
        #: Y position of the connection point relative to the center.
        self.y: int | str = 0
        # Type of the connection point.
        self.type = NodeType.OTHER
        #: Link Name of the connection point.
        self.link_name: str = ""
        # IO of the connection point.
        self.io = NodeIO.UNDEFINED
        # Phases of the connection point.
        self.phase: float = 0
        # Name of the connection point.
        self.name: str = ""

    def component_init(self) -> str:
        """
        Returns the component initialization code in Python.

        :return: The component initialization code.
        :rtype: str
        """
        if self.type != NodeType.OTHER:
            return "ConnectionPoint({0}, {1}, {2}, NodeIO.{3}, self, (NodeType.{4}, {5}))".format(
                self.x * 32 if isinstance(self.x, int) else f'"{self.x}"',
                self.y * 32 if isinstance(self.y, int) else f'"{self.y}"',
                f'"{self.name}"',
                self.io.name,
                self.type.name,
                (
                    f'str(self.get_by_key("{self.link_name}"))'
                    if self.link_name is not None and self.link_name != ""
                    else "self.name"
                ),
            )
        return "ConnectionPoint({0}, {1}, {2}, NodeIO.{3}, self)".format(
            self.x * 32 if isinstance(self.x, int) else f'"{self.x}"',
            self.y * 32 if isinstance(self.y, int) else f'"{self.y}"',
            f'"{self.name}"'.format(),
            self.io.name,
        )

    def merge(self, other: "ExtConnectionPoint") -> None:
        """
        Merges the node with another node.

        :param other: Other node
        :type other: ExtConnectionPoint
        """
        self.type = (
            other.type
            if list(NodeType).index((other.type)) < list(NodeType).index(self.type)
            else self.type
        )
