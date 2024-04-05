# LGPL-3.0 License
# Copyright (c) 2023 KIT-IAI-ESA

from typing import Any
from pyapi_rts.shared import (
    ParameterBoundProperty,
)
from pyapi_rts.shared.node_type import NodeType, NodeIO


class ConnectionPoint:
    """A connection point of a component rectangle."""

    def __init__(
        self,
        x: int | str,
        y: int | str,
        name: str,
        io: NodeIO,
        component: Any,
        link: tuple[NodeType, str] = (NodeType.OTHER, ""),
    ) -> None:
        """Initialize the ConnectionPoint object.

        :param x: X position
        :type x: int | str
        :param y: Y position
        :type y: int | str
        :param name: Name of the connection point
        :type name: str
        :param io: IO of the connection point
        :type io: NodeIO
        :param component: The component this connection point belongs to.
        :type component: Component
        :param link: Node link by name, defaults to ('NodeType.OTHER', "")
        :type link: tuple[NodeType, str], optional
        """
        from pyapi_rts.api import Component

        #: X position relative to the center of the component.
        self.x: ParameterBoundProperty = ParameterBoundProperty(x, int)
        #: Y position relative to the center of the component.
        self.y = ParameterBoundProperty(y, int)
        #: Name of the connection point.
        self.name = name
        #: Linking behaviour to other nodes.
        self.link_type: NodeType = link[0]
        #: IO Type of the connection point.
        self.io = io
        #: Link name.
        self.link: str = link[1]
        #: The component this connection point belongs to.
        self.component: Component = component

    @property
    def link_name(self) -> str:
        """The link name or the name of the connection point if no link is defined.

        :return: The key for the link dictionary.
        :rtype: str
        """
        return self.link if self.link is not None and len(self.link) > 0 else self.name

    @property
    def position(self) -> tuple[int, int]:
        return self.position_from_dict(self.component.as_dict())

    @property
    def position_abs(self) -> tuple[int, int]:
        pos = self.position
        return (pos[0] + self.component.x, pos[1] + self.component.y)

    def position_from_dict(self, comp_dict: dict, absolute: bool = False) -> tuple[int, int]:
        x = int(self.x.get_value(comp_dict))
        y = int(self.y.get_value(comp_dict))

        rotation = self.component.rotation
        mirror = self.component.mirror

        if mirror == 1:
            x = -x

        while rotation > 0:
            x, y = -y, x
            rotation -= 1

        if absolute:
            return (x + self.component.x, y + self.component.y)
        return (x, y)
