# LGPL-3.0 License
# Copyright (c) 2023 KIT-IAI-ESA

import itertools

from pyapi_rts.shared.component_hook import ComponentHook


class LinkedNodeHook(ComponentHook):
    """
    Connects nodes that have the "linkNode" property set to "yes".
    """

    @classmethod
    def graph_connections(
        cls, components: list, pos_dict: dict, link_dict: dict
    ) -> list[tuple[str, str]]:
        edges = []
        name_dict: dict[str, list[str]] = {}
        for component in components:
            if (
                component.type == "rtds_sharc_node"
                and component.as_dict()["linkNode"]._value.value.lower() == "yes"
            ):
                if component.name not in name_dict:
                    name_dict[component.name] = []
                name_dict[component.name].append(component.uuid)

        for _, names in name_dict.items():
            for (left, right) in itertools.combinations(names, 2):
                edges.append((left, right, "LINK_CONNECTED"))

        return edges
