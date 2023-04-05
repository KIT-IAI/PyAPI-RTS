# LGPL-3.0 License
# Copyright (c) 2023 KIT-IAI-ESA

from typing import Any

from pyapi_rts.shared.node_type import NodeType


class ComponentHook:
    """
    Base class for components to be hooked into the main program.
    """

    def __init__(self) -> None:
        """
        Constructor.
        """

    @classmethod
    def graph_connections(
        cls, components, pos_dict: dict, link_dict: dict
    ) -> list[tuple[str, str, str]]:
        """
        Hook method.
        """
        return []

    @classmethod
    def link_connections(cls, components: list) -> list[tuple[str, str, str, NodeType]]:
        """
        Hook for adding entries to link_dict.

        :param components: list of components
        :type components: list[Component]
        :return: list of connections in form [(name, component_uuid, point_name, node_type), ...]
        :rtype: list[tuple[str, str, node_type]]
        """
        return []

    @classmethod
    def special_value(cls, component: Any, key: str) -> Any | None:
        """
        Adds new special values to components.

        :param component: Component to evaluate.
        :type component: Component
        :return: Value of the special key or None if it does not exist for this component.
        :rtype: Any | None
        """
        return None
