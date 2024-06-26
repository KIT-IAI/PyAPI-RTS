# LGPL-3.0 License
# Copyright (c) 2023 KIT-IAI-ESA

import copy
import itertools
from typing import Optional, TYPE_CHECKING, Union

import networkx as nx

from pyapi_rts.api.component import Component
from pyapi_rts.api.graph import EdgeType, add_xrack_connections

if TYPE_CHECKING:
    from .draft import Draft


class Container:
    """Abstract class for an object containing a list of components"""

    def __init__(self, parent: Optional[Union["Container", "Draft"]] = None) -> None:
        self.box_parent = parent
        """The parent component box of this component box.
        Used to traverse up the hierarchies to the Draft object.
        """

        self._components: dict[str, Component] = {}
        self._pos_dict: dict[tuple[int, int], dict[str, list[str]]] | None = None
        self._draft_vars: dict[str, Component] = {}

    def get_components(
        self, recursive: bool = False, clone: bool = True, with_groups: bool = False
    ) -> list[Component]:
        """Return a list of all components in the component box.

        :param recursive: Also lists components in component boxes \
            contained in this, defaults to False.
        :type recursive: bool, optional
        :return: list of components in the component box
        :param copy: Returns a copy of the list instead of the list itself, defaults to True
        :type copy: bool, optional
        :param with_groups: Include components in groups, defaults to False
        :type with_groups: bool, optional
        :rtype: list[Component]
        """

        comps = list(self._components.values())
        if recursive:
            comps += [
                c
                for cb in self.get_component_boxes(True)
                for c in cb.get_components(False, clone=False)
            ]
        elif with_groups:
            from .group import Group

            comps += [
                c
                for cb in [c for c in self._components.values() if isinstance(c, Group)]
                for c in cb.get_components(recursive=False, clone=False, with_groups=True)
            ]

        return copy.deepcopy(comps) if clone else comps

    def get_draft(self) -> Optional["Draft"]:
        """Return the draft of the component box.

        :return: The draft this component box is part of
        :rtype: Draft
        """
        from .draft import Draft

        if isinstance(self.box_parent, Container):
            return self.box_parent.get_draft()
        if isinstance(self.box_parent, Draft):
            # Parent of top-level component box is the draft object
            return self.box_parent
        return None

    def get_draft_vars(self, recursive: bool = True) -> dict[str, Component]:
        """Get a dictionary with the draft variables in the component box with names as key.

        :param recursive: If true, also return the draft variables of contained component boxes,\
            defaults to True
        :type recursive: bool, optional
        :return: Dictionary of draft variables.
        :rtype: dict[str, Component]
        """
        draft_vars: dict[str, Component] = {}

        if recursive:
            for box in self.get_component_boxes(recursive=False):
                draft_vars |= box.get_draft_vars(recursive=True)

        return draft_vars | self._draft_vars

    def search_by_name(
        self, name: str, recursive: bool = False, case_sensitive: bool = False
    ) -> list[Component] | None:
        """Search for components by their name

        :param name: Name to search for
        :type name: str
        :param recursive: Searches recursively in contained boxes, defaults to False
        :type recursive: bool, optional
        :param case_sensitive: Case sensitive search, defaults to False
        :type case_sensitive: bool, optional
        :return: list of components with the given name
        :rtype: list[Component]
        """
        return list(
            filter(
                (
                    lambda c: (
                        (str(c.name).lower() == name.lower())
                        if not case_sensitive
                        else (c.name == name)
                    )
                ),
                self.get_components(recursive, clone=False, with_groups=True),
            ),
        )

    def get_by_id(
        self, cid: str, recursive: bool = True, with_groups: bool = True
    ) -> Component | None:
        """Get a component by its id

        :param cid: Component UUID to search for
        :type cid: str
        :param recursive: Searches recursively in boxes, defaults to True
        :type recursive: bool, optional
        :param with_groups: Include components in groups, defaults to True
        :type with_groups: bool, optional
        :return: Component with the given UUID if found, None otherwise
        :rtype: Component | None
        """

        comp = self._components.get(cid, None)
        if comp is not None:
            return comp

        if recursive:
            # recursive includes groups
            for cb in self.get_component_boxes(recursive=True):
                comp = cb.get_by_id(cid, recursive=False, with_groups=False)
                if comp is not None:
                    return comp
        elif with_groups:
            from .group import Group

            for group in [c for c in self._components.values() if isinstance(c, Group)]:
                comp = group.get_by_id(cid, recursive=False, with_groups=False)
                if comp is not None:
                    return comp

        return comp

    def add_component(self, component: Component) -> None:
        """Add a component to the component box and update
        the connection graph and other data structures.

        :param component: The component to add to this box
        :type component: Component
        """
        if isinstance(component, Container):
            component.box_parent = self
        else:
            component.parent = self

        self._components[component.uuid] = component

        if component.type == "rtds_draft_var":
            self._draft_vars[component.name] = component

        if self._pos_dict is not None:
            pos_dict = component.generate_pos_dict()
            for key, value in pos_dict.items():
                if key in self._pos_dict:
                    self._pos_dict[key] |= value
                else:
                    self._pos_dict[key] = value

    def remove_component(self, cid: str, recursive: bool = False, with_groups: bool = True) -> bool:
        """Remove a component from the component box and update
        the connection graph and other data structures.

        :param cid: Component UUID to remove
        :type cid: str
        :param recursive: Searches recursively, defaults to False
        :type recursive: bool, optional
        :param with_groups: Include components in groups, defaults to True
        :type with_groups: bool, optional
        :return: Success of search and removal
        :rtype: bool
        """
        comp = self.get_by_id(cid, recursive=False, with_groups=False)  # Remove component from list
        if comp is None:
            if recursive:
                for comp_box in self.get_component_boxes():
                    if comp_box.remove_component(cid):
                        return True
            elif with_groups:
                from .group import Group

                for group in [c for c in self._components.values() if isinstance(c, Group)]:
                    if group.remove_component(cid):
                        return True
            return False
        self._components.pop(comp.uuid, None)

        if comp.type == "rtds_draft_var":
            self._draft_vars.pop(comp.name, None)

        if self._pos_dict is not None:
            for key in list(self._pos_dict):
                # Remove node from pos_dict
                if cid in self._pos_dict[key]:
                    del self._pos_dict[key][cid]
                    if len(self._pos_dict[key]) == 0:
                        del self._pos_dict[key]

        return True

    def update_component(self, component: Component) -> bool:
        """Update a component in the component box and update the
        connection graph and other data structures.

        :param component: The component to update
        :type component: Component
        :return: Success of search and modification
        :rtype: bool
        """

        comp = self.get_by_id(component.uuid, recursive=False, with_groups=True)
        if comp is None:
            return False

        self.remove_component(comp.uuid)
        self.add_component(component)

        return True

    def get_component_boxes(self, recursive: bool = False) -> list["Container"]:
        """Return a list of all component boxes in the component box."""
        return (
            [cb for cb in self._components.values() if isinstance(cb, Container)]
            if not recursive
            else [cb for cb in self._components.values() if isinstance(cb, Container)]
            + [
                c
                for cb in self.get_component_boxes(False)
                for c in cb.get_component_boxes(recursive)
            ]
        )

    def get_graph(self) -> tuple[nx.MultiGraph, dict[tuple[str, str], list[str]]]:
        """Generate the full graph consisting of the union of all componentBoxes included in this one.

        :return: The graph and dictionary of cross-hierarchy connection points.
        :rtype: tuple[Graph, dict]
        """

        (
            local_graph,
            label_connections,
            linked_connections,
            xrack_connections,
        ) = self._generate_full_graph()

        for value in label_connections.values():
            for i, j in itertools.combinations(value, 2):
                local_graph.add_edge(i, j, type=EdgeType.LABEL)

        for value in linked_connections.values():
            for i, j in itertools.combinations(value, 2):
                local_graph.add_edge(i, j, type=EdgeType.LINK)

        add_xrack_connections(xrack_connections, local_graph, mark_xrack=False)

        return local_graph, xrack_connections

    def _generate_full_graph(
        self, depth: int = 0
    ) -> tuple[
        nx.MultiGraph, dict[str, list[str]], dict[str, list[str]], dict[tuple[str, str], list[str]]
    ]:
        if self._pos_dict is None:
            self._pos_dict = self._generate_position_dict()

        local_graph = self._generate_position_graph(self._pos_dict)
        nx.set_node_attributes(local_graph, depth, "depth")

        label_connections, linked_connections, xrack_connections = self._get_nongrid_connections()

        for box in self.get_component_boxes():
            box_connections = self._get_box_connections(local_graph, box.uuid)

            (
                box_graph,
                box_label_connections,
                box_linked_connections,
                box_xrack_connections,
            ) = box._generate_full_graph(depth + 1)
            local_graph = nx.compose(local_graph, box_graph)

            for uuid in box_connections:
                component = self.get_by_id(uuid)
                box_comps = box.search_by_name(component.name)
                for box_comp in box_comps:
                    if box_comp.type == component.type:
                        local_graph.add_edge(uuid, box_comp.uuid, type=EdgeType.NAME)

            for key, value in box_label_connections.items():
                if key not in label_connections:
                    label_connections[key] = value
                else:
                    label_connections[key] += value

            for key, value in box_linked_connections.items():
                if key not in linked_connections:
                    linked_connections[key] = value
                else:
                    linked_connections[key] += value

            for key, value in box_xrack_connections.items():
                if key not in xrack_connections:
                    xrack_connections[key] = value
                else:
                    xrack_connections[key] += value

        return (
            local_graph,
            label_connections,
            linked_connections,
            xrack_connections,
        )

    def _generate_position_dict(self) -> dict[tuple[int, int], dict[str, list[str]]]:
        """Generates the position dictionary.

        :return: The position dictionary
        :rtype: dict[tuple[int, int], dict[str, list[str]]]
        """
        position_dict: dict[tuple[int, int], dict[str, list[str]]] = {}
        components = self.get_components(recursive=False, clone=False, with_groups=True)
        for component in components:
            comp_pos_dict = component.generate_pos_dict()
            for pos, connections in comp_pos_dict.items():
                if pos in position_dict:
                    position_dict[pos] |= connections
                else:
                    position_dict[pos] = connections
        return position_dict

    def _generate_position_graph(
        self, position_dict: dict[tuple[int, int], dict[str, list[str]]]
    ) -> nx.MultiGraph:
        """Generates the connection graph, the position dictionary and the link dictionary

        :return: The connection graph, the position dictionary and the link dictionary
        :rtype: MultiGraph
        """
        graph = nx.MultiGraph()
        components = self.get_components(recursive=False, clone=False, with_groups=True)
        for comp in components:
            graph.add_node(comp.uuid, type=comp.type)

        # Check if any two nodes at the same position are connected and not from the same component
        for single_pos_dict in position_dict.values():
            for left, right in itertools.combinations(single_pos_dict.keys(), 2):
                edge_key = graph.add_edge(left, right)
                graph.edges[left, right, edge_key].update(
                    {
                        "type": EdgeType.GRID,
                        left: single_pos_dict[left],
                        right: single_pos_dict[right],
                    },
                )

        return graph

    def _get_nongrid_connections(
        self,
    ) -> tuple[dict[str, list[str]], dict[str, list[str]], dict[tuple[str, str], list[str]]]:
        """Get the non-grid-based connections of the component box.

        :return: labels, linked, xrack\
            labels: Wirelabels. Maps names to uuids.\
            linked: Bus labels and nodes with 'linkNodes' activated. Maps names to uuids.\
            xrack: All xrack components. Maps name and type to uuids.
        :rtype: tuple[dict, dict, dict]
        """
        components = self.get_components(clone=False, with_groups=True)
        # node name -> list of uuids of components
        labels: dict[str, list[str]] = {}
        linked: dict[str, list[str]] = {}
        xrack: dict[tuple[str, str], list[str]] = {}
        for c in components:
            if c.type == "rtds_sharc_sld_BUSLABEL":
                if c.Parameters.linkNodes.index == 1:  # type: ignore
                    if linked.get(c.name) is None:
                        linked[c.name] = [c.uuid]
                    else:
                        linked[c.name].append(c.uuid)
            elif c.type == "rtds_sharc_node":
                if c.NODEPARAMETERS.linkNode.index == 1:  # type: ignore
                    if linked.get(c.name) is None:
                        linked[c.name] = [c.uuid]
                    else:
                        linked[c.name].append(c.uuid)
            elif c.type in {"wirelabel"}:
                if labels.get(c.name) is None:
                    labels[c.name] = [c.uuid]
                else:
                    labels[c.name].append(c.uuid)
            elif c.type in {"lf_rtds_sharc_sld_TLINE", "_rtds_CABLE1.def"}:
                name = c.CONFIGURATION.Tnam1.value  # type: ignore
                label = (c.enumeration.apply(name), c.type)
                if xrack.get(label) is None:
                    xrack[label] = [c.uuid]
                else:
                    xrack[label].append(c.uuid)
            elif c.type in {"lf_rtds_sharc_sld_TL16CAL", "_rtds_CBLCAL.def"}:
                label = (c.name, c.type)
                if xrack.get(label) is None:
                    xrack[label] = [c.uuid]
                else:
                    xrack[label].append(c.uuid)
            elif "rtds_XRTRF" in c.type:
                name = c.get_by_key("Tnam1")
                label = (c.enumeration.apply(name), c.type)
                if xrack.get(label) is None:
                    xrack[label] = [c.uuid]
                else:
                    xrack[label].append(c.uuid)
        return labels, linked, xrack

    def _get_box_connections(self, graph: nx.MultiGraph, box_uuid: str) -> list[str]:
        """Return a list of all BUSLABEL components connected to a certain component box.

        :param graph: The graph describing the position-based connections
        :type graph: nx.MultiGraph
        :param box_uuid: The uuid of the component box to search from
        :type box_uuid: str
        :return: The list of connected BUSLABEL components
        :rtype: list[str]
        """
        box_connections: list[str] = []
        visited = {box_uuid}
        stack = [(box_uuid, iter(graph[box_uuid]))]
        while stack:
            _, children = stack[-1]
            # iterate through the components connected to the first tuple entry component
            try:
                child = next(children)
                if child not in visited:
                    ctype = graph.nodes[child]["type"]
                    # if the component is a buslabel, add it to the list
                    if ctype in {"rtds_sharc_sld_BUSLABEL"}:
                        box_connections.append(child)
                    # if the component is a BUS, keep traversing and add it to the stack
                    elif ctype in {"BUS"}:
                        stack.append((child, iter(graph[child])))
                    visited.add(child)
            except StopIteration:
                stack.pop()
        return box_connections
