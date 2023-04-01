# LGPL-3.0 License
# Copyright (c) 2023 KIT-IAI-ESA

import itertools

from pyapi_rts.api.component import Component
from pyapi_rts.shared.component_hook import ComponentHook


class TLineHook(ComponentHook):
    """
    Adds TLINE connections.

    :param ComponentHook: _description_
    :type ComponentHook: _type_
    """

    @classmethod
    def graph_connections(
        cls, components: list[Component], pos_dict: dict, link_dict: dict
    ) -> list[tuple[str, str]]:
        tnam1_dict = {}
        result = []
        for uuid, comps in pos_dict.items():

            for i in range(len(comps)):
                filtered = list(
                    filter(
                        (
                            lambda c: c.type == "lf_rtds_sharc_sld_TLINE"
                            and c.uuid == comps[i][1]
                        ),
                        components,
                    )
                )
                if len(filtered) > 0:
                    comp = filtered[0]

                    name = comp.enumeration.apply(comp.as_dict()["Tnam1"].value)
                    if name in tnam1_dict:
                        tnam1_dict[name].append(comp.uuid)
                    else:
                        tnam1_dict[name] = [comp.uuid]

        # Get Connection boxes
        for i in range(len(components)):
            comp = components[i]
            if comp.type == "lf_rtds_sharc_sld_TL16CAL":
                if comp.name in tnam1_dict:
                    tnam1_dict[comp.name].append(comp.uuid)
                else:
                    tnam1_dict[comp.name] = [comp.uuid]

        for _, uuids in tnam1_dict.items():
            for (left, right) in itertools.combinations(set(uuids), 2):
                result.append((left, right, "TLINE_CONNECTED"))

        return result
