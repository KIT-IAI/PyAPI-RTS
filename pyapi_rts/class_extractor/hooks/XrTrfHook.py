# LGPL-3.0 License
# Copyright (c) 2023 KIT-IAI-ESA


from pyapi_rts.shared.node_type import NodeType
from pyapi_rts.shared.component_hook import ComponentHook


class XrTrfHook(ComponentHook):
    """
    A hook for Cross Rack Transformers
    """

    @classmethod
    def link_connections(cls, components: list) -> list[tuple[str, str, NodeType]]:
        """
        Adds entries to link_dict for Crossrack Transformers.
        """
        result = []
        for component in components:
            if "rtds_XRTRF" in component.type:
                name = component.enumeration.apply(component.get_by_key("Tnam1"))
                result.append(
                    (
                        f"XRTRF-{name}",
                        component.uuid,
                        "XRTRF",
                        NodeType.NC_CONNECTED_LINKED,
                    )
                )
        return result
