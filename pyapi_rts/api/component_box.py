# LGPL-3.0 License
# Copyright (c) 2023 KIT-IAI-ESA

import copy
import itertools
import queue
from typing import Any, Optional, TYPE_CHECKING, Union

import networkx as nx
from networkx.classes.graph import Graph

from pyapi_rts.shared import NodeType
from pyapi_rts.api.component import Component

if TYPE_CHECKING:
    from .draft import Draft
    from .group import Group


class ComponentBox:
    """Abstract class for an object containing a list of components"""

    def __init__(self, parent: Optional[Union["ComponentBox","Draft"]] = None) -> None:
        self.box_parent = parent
        """The parent component box of this component box.
        Used to traverse up the hierarchies to the Draft object.
        """

        self._components: list[Component] = []
        self._conn_graph = None
        self._pos_dict: dict[str, list[tuple[str, str]]] = {}
        self._link_dict: dict[str, list[tuple[str, str, NodeType]]] | None = None
        self._draft_vars: dict[str, Component] = {}

    def get_rack_type(self) -> int | None:
        """Return the rack type of the component box by traversing up to the Draft object.

        :return: The rack type of the component box.
        :rtype: int
        """
        draft = self.get_draft()
        if draft is not None:
            return draft.get_rack_type()
        return None

    def get_groups(self) -> list["Group"]:
        """Return a list of all groups in the component box.

        :return: list of groups in the component box
        :rtype: list[Group]
        """
        from .group import Group
        return [c for c in self._components if isinstance(c, Group)]

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

        comps = (
            self._components
            + (
                [
                    c
                    for cb in self.get_groups()
                    for c in cb.get_components(recursive=False, clone=False, with_groups=True)
                ]
                if with_groups and not recursive
                else []
            )
            + (
                [
                    c
                    for cb in self.get_component_boxes(True)
                    for c in cb.get_components(False, clone=False)
                ]
                if recursive
                else []
            )
        )
        return copy.deepcopy(comps) if clone else comps

    def get_draft(self) -> Optional["Draft"]:
        """Return the draft of the component box.

        :return: The draft this component box is part of
        :rtype: Draft
        """
        from .draft import Draft
        if isinstance(self.box_parent, ComponentBox):
            return self.box_parent.get_draft()
        if isinstance(self.box_parent, Draft):
            # Parent of top-level component box is the draft object
            return self.box_parent
        return None

    def get_draft_vars(self, recursive: bool = True) -> dict[str, Component]:
        """Get a dictionary with the draft variables in the component box with names as key.

        :param recursive: If true, also return the draft variables of contained component boxes, defaults to True
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

        comp = next(
            filter(
                (lambda c: c.uuid == cid),
                self.get_components(False, False, with_groups),
            ),
            None,
        )
        if comp is None:
            if not recursive:
                return None
            for cb in self.get_component_boxes(recursive):
                comp = cb.get_by_id(cid, recursive, with_groups=with_groups)
                if comp is not None:
                    return copy.deepcopy(comp)
            return None
        return comp

    def add_component(self, component: Component) -> None:
        """Add a component to the component box and update
        the connection graph and other data structures.

        :param component: The component to add to this box
        :type component: Component
        """
        if isinstance(component, ComponentBox):
            component.box_parent = self
        else:
            component.parent = self

        self._components.append(component)

        if component.type == "rtds_draft_var":
            self._draft_vars[component.name] = component

        if self._conn_graph is not None:  # Only calculate changes in graph
            self._conn_graph.add_node(component.uuid, type=component.type)  # New node
            pos_dict = component.generate_pos_dict()
            for key, value in pos_dict.items():
                if key in self._pos_dict:
                    for _, cid in self._pos_dict[key]:
                        self._conn_graph.add_edge(component.uuid, cid)  # New edges
                    self._pos_dict[key] += value
                else:
                    self._pos_dict[key] = value

            self._link_dict = self.__generate_link_dict()

    def get_component_boxes(self, recursive: bool = False) -> list["ComponentBox"]:
        """Return a list of all component boxes in the component box."""
        # TODO: WHY? we also have get_hierarchies
        return (
            [cb for cb in self._components if isinstance(cb, ComponentBox)]
            if not recursive
            else [cb for cb in self._components if isinstance(cb, ComponentBox)]
            + [
                c
                for cb in self.get_component_boxes(False)
                for c in cb.get_component_boxes(recursive)
            ]
        )

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
                for group in self.get_groups():
                    if group.remove_component(cid):
                        return True
            return False
        self._components.remove(comp)

        if comp.type == "rtds_draft_var":
            self._draft_vars.pop(comp.name, None)

        if self._conn_graph is None:
            return True

        self._conn_graph.remove_node(cid)  # Remove node from graph
        for (
            key,
            _,
        ) in self._pos_dict.copy().items():  # Remove node from posDict
            pos_dict_entry = next(filter((lambda a: a[1] == cid), self._pos_dict[key]), None)
            if pos_dict_entry is not None:
                self._pos_dict[key].remove(pos_dict_entry)
                if len(self._pos_dict[key]) == 0:
                    self._pos_dict.pop(key)

        for (
            key,
            _,
        ) in self._link_dict.copy().items():  # Remove node from linkDict
            link_dict_entry = next(filter((lambda x: x[0] == cid), self._link_dict[key]), None)
            if link_dict_entry is not None:
                self._link_dict[key].remove(link_dict_entry)
                if len(self._link_dict[key]) == 0:
                    self._link_dict.pop(key)
        return True

    def modify_component(self, component: Component, recursive: bool = True) -> bool:
        """Modify a component in the component box and update the
        connection graph and other data structures.

        :param component: The component to modify
        :type component: Component
        :param recursive: Searches recursively, defaults to True
        :type recursive: bool, optional
        :return: Success of search and modification
        :rtype: bool
        """

        comp = self.get_by_id(component.uuid)
        if comp is None:
            if not recursive:
                return False
            for hier in self.get_component_boxes():
                if hier.modify_component(component, recursive):
                    return True
            return False

        self.remove_component(comp.uuid)
        self.add_component(component)

        if comp.type == "rtds_draft_var":
            self._draft_vars.pop(comp.name, None)
            self._draft_vars[component.name] = component

        return True

    def set_parameter_of(self, cid: str, param_key: str, value: Any) -> bool:
        """Set a parameter of the component with the given UUID

        :param cid: The component UUID
        :type cid: str
        :param paramKey: The key of the parameter to set
        :type paramKey: str
        :param value: The value to set
        :type value: Any
        :return: Success of operation
        :rtype: bool
        """
        comp = self.get_by_id(cid)
        if comp is None:
            return False
        setting_success = comp.set_by_key(param_key, value)
        if setting_success:
            setting_success = self.modify_component(comp)
        return setting_success

    def get_hierarchies(self, recursive: bool = False) -> list[Component]:
        """Return all hierarchy components in the component box

        :param recursive: Recusive search, defaults to False
        :type recursive: bool, optional
        :return: list of all hierarchies in the component box
        :rtype: list[Component]
        """

        local_hierarchies = [c for c in self._components if c.type == "HIERARCHY"]

        if not recursive:
            return local_hierarchies

        return local_hierarchies + [l for h in local_hierarchies for l in h.get_hierarchies(True)]

    def get_link_dict(self) -> dict[str, list[tuple[str, str, NodeType]]]:
        """Returns the link dictionary and generates it if it is not already generated.

        The link dictionary links the name of a connection point to a list of component UUIDs.
        It only includes NAME_CONNECTED connection points, e.g. of bus labels and wire labels.

        :return: The link dictionary; (Component.uuid, ConnectionPoint.name, ConnectionPoint.link_type)
        :rtype: dict[str, list[tuple[str, str, NodeType]]]
        """
        if self._link_dict is None:
            self._link_dict = self.__generate_link_dict()
        return self._link_dict

    def get_connection_graph(self) -> Graph:
        """Returns the connection graph and generates it if necessary.

        The connection graph only contains connections in the same hierarchy level and does not
        include connections via wire label.
        This method also triggers the generation of the link dictionary.

        :return: The connection graph
        :rtype: Graph
        """
        if self._conn_graph is None:
            (
                self._conn_graph,
                self._pos_dict,
                self._link_dict,
            ) = self.__generate_conn_graph()
        return self._conn_graph.copy()

    def __generate_conn_graph(self) -> tuple[Graph, dict, dict]:
        """
        Generates the connection graph, the position dictionary and the link dictionary

        :return: The connection graph, the position dictionary and the link dictionary
        :rtype: tuple[Graph, dict, dict]
        """
        position_dict: dict[str, list[tuple[str, str]]] = {}
        link_dict: dict[str, list[tuple[str, str, NodeType]]] = self.get_link_dict()
        edges = []

        for c_orig in self.get_components(clone=False, with_groups=True):
            original_dict = c_orig.generate_pos_dict()
            for key, values in original_dict.items():
                if key in position_dict:
                    for val in values:
                        position_dict[key].append(val)
                else:
                    position_dict[key] = values

        # Check if any two nodes at the same position are connected and not from the same component
        for _, values in position_dict.items():
            for left, right in itertools.combinations(range(len(values)), 2):
                if values[left][1] != values[right][1]:
                    edges.append((values[left][1], values[right][1]))

        graph = nx.Graph()
        for comp in self.get_components(clone=False, with_groups=True):
            graph.add_node(comp.uuid, type=comp.type)

        graph.add_edges_from(edges)

        # HOOKS WERE HERE
        for edge in graph_connections_linked(self.get_components(False, False, True)):
            if not graph.has_edge(edge[0], edge[1]):
                graph.add_edge(edge[0], edge[1], type=edge[2])

        for edge in graph_connections_tline(self.get_components(False, False, True), position_dict):
            if not graph.has_edge(edge[0], edge[1]):
                graph.add_edge(edge[0], edge[1], type=edge[2])

        # Add links (nodes connected by name on the same hierarchy level, e.g. linked bus label)
        for key, values in link_dict.items():
            for i, j in itertools.combinations(range(len(values)), 2):
                if (
                    values[i][0] != values[j][0]  # 2 different components
                    and values[i][2] == values[j][2]  # same connection type
                    and values[i][2] == NodeType.NAME_CONNECTED_LINKED
                ):
                    graph.add_edge(values[i][0], values[j][0])

        return (graph, position_dict, link_dict)

    def __generate_link_dict(self) -> dict[str, list[tuple[str, str, NodeType]]]:
        """Generate the link dictionary"""

        link_dict: dict[str, list[tuple[str, str, NodeType]]] = {}
        for comp in self.get_components(clone=False, with_groups=True):
            for node in comp.connection_points.values():
                if node.link_type != NodeType.OTHER:
                    link_name = comp.enumeration.apply(node.link_name)
                    if comp.name in link_dict:
                        link_dict[comp.name].append((comp.uuid, node.name, node.link_type))
                    else:
                        link_dict[comp.name] = [(comp.uuid, node.name, node.link_type)]

        for link_name, link_uuid, point_name, link_node_type in link_connections(
            self.get_components(False, False, True)
        ):
            if link_name in link_dict.keys():
                link_dict[link_name].append((link_uuid, point_name, link_node_type))
            else:
                link_dict[link_name] = [(link_uuid, point_name, link_node_type)]
        return link_dict

    def generate_full_graph(self) -> tuple[Graph, dict]:
        """Generate the full graph consisting of the union of all componentBoxes included in this one.

        :return: The graph and dictionary of cross-hierarchy connection points.
        :rtype: tuple[Graph, dict]
        """

        (
            local_graph,
            _,
            label_connections,
            linked_connections,
            xrack_connections,
        ) = self._generate_full_graph()

        for value in label_connections.values():
            for i, j in itertools.combinations(value, 2):
                local_graph.add_edge(i, j, type="LABEL_CONNECTED")

        for value in linked_connections.values():
            for i, j in itertools.combinations(value, 2):
                if not local_graph.has_edge(i, j):
                    local_graph.add_edge(i, j, type="LINK_CONNECTED")

        add_xrack_connections(xrack_connections, local_graph, mark_xrack=False)

        return local_graph, xrack_connections

    def _generate_custom_conn_graph(self) -> Graph:
        """
        Generates the connection graph, the position dictionary and the link dictionary

        :return: The connection graph, the position dictionary and the link dictionary
        :rtype: tuple[Graph, dict, dict]
        """
        position_dict: dict = {}
        edges = []

        for component in self.get_components(clone=False, with_groups=True):
            comp_pos_dict = component.generate_pos_dict()
            for key, values in comp_pos_dict.items():
                if key in position_dict:
                    for val in values:
                        position_dict[key].append(val)
                else:
                    position_dict[key] = values

        # Check if any two nodes at the same position are connected and not from the same component
        for _, values in position_dict.items():
            for left, right in itertools.combinations(range(len(values)), 2):
                if values[left][1] != values[right][1]:
                    edges.append((values[left][1], values[right][1]))

        graph = nx.Graph()
        for comp in self.get_components(clone=False, with_groups=True):
            graph.add_node(comp.uuid, type=comp.type)

        graph.add_edges_from(edges)
        nx.set_node_attributes(graph, 1, "depth")

        return graph

    def _generate_full_graph(self, depth: int = 0) -> tuple[Graph, dict, dict, dict, dict]:
        local_graph: Graph = self._generate_custom_conn_graph()
        nx.set_node_attributes(local_graph, depth, "depth")

        # link_dict enthält noch die buslabels, die eigentlich grid-based sind
        # wir brauchen hier eigentlich die labels, die non-grid-based
        # link_dict = self.get_link_dict()
        label_connections, linked_connections, xrack_connections = self._get_nongrid_connections()

        boxes = self.get_component_boxes()
        # box.uuid -> list of connected components
        box_connections: dict[str, list] = {}
        for box in boxes:
            box_connections[box.uuid] = self._get_box_connections(local_graph, box.uuid)

            (
                box_graph,
                _,
                box_label_connections,
                box_linked_connections,
                box_xrack_connections,
            ) = box._generate_full_graph(depth + 1)
            local_graph = nx.compose(local_graph, box_graph)

            for label in box_connections[box.uuid]:
                component = self.get_by_id(label)
                box_comps = box.search_by_name(component.name)
                for box_comp in box_comps:
                    if box_comp.type == component.type:
                        local_graph.add_edge(label, box_comp.uuid, type="NAME_CONNECTED")

            for key, value in box_label_connections.items():
                if label_connections.get(key) is None:
                    label_connections[key] = value
                else:
                    label_connections[key] += value

            for key, value in box_linked_connections.items():
                if linked_connections.get(key) is None:
                    linked_connections[key] = value
                else:
                    linked_connections[key] += value

            for key, value in box_xrack_connections.items():
                if xrack_connections.get(key) is None:
                    xrack_connections[key] = value
                else:
                    xrack_connections[key] += value

        return (
            local_graph,
            box_connections,
            label_connections,
            linked_connections,
            xrack_connections,
        )

    def _get_nongrid_connections(self) -> tuple[dict, dict, dict]:
        components = self.get_components(clone=False, with_groups=True)
        # node name -> list of uuids of components
        linked = {}
        xrack = {}
        labels = {}
        for c in components:
            if c.type == "rtds_sharc_sld_BUSLABEL":
                if c.Parameters.linkNodes.index == 1:
                    if linked.get(c.name) is None:
                        linked[c.name] = [c.uuid]
                    else:
                        linked[c.name].append(c.uuid)
            elif c.type == "rtds_sharc_node":
                if c.NODEPARAMETERS.linkNode.index == 1:
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
                name = c.CONFIGURATION.Tnam1.value
                label = (c.enumeration.apply(name), c.type)
                if xrack.get(label) is None:
                    xrack[label] = [c.uuid]
                else:
                    xrack[label].append(c.uuid)
            elif c.type in {"lf_rtds_sharc_sld_TL16CAL", "_rtds_CBLCAL.def"}:
                label = (c.enumeration.apply(c.name), c.type)
                if xrack.get(label) is None:
                    xrack[label] = [c.uuid]
                else:
                    xrack[label].append(c.uuid)
            elif "rtds_XRTRF" in c.type:
                name = c.enumeration.apply(c.get_by_key("Tnam1"))
                label = (name, c.type)
                if xrack.get(label) is None:
                    xrack[label] = [c.uuid]
                else:
                    xrack[label].append(c.uuid)
        return labels, linked, xrack

    def _get_box_connections(self, graph: nx.Graph, uuid: str) -> list[str]:
        box_connections = []
        visited = {uuid}
        stack = [(uuid, iter(graph[uuid]))]
        while stack:
            _, children = stack[-1]
            try:
                child = next(children)
                if child not in visited:
                    ctype = graph.nodes[child]["type"]
                    if ctype in {"rtds_sharc_sld_BUSLABEL"}:
                        box_connections.append(child)
                    if ctype in {"BUS"}:
                        stack.append((child, iter(graph[child])))
                    visited.add(child)
            except StopIteration:
                stack.pop()
        return box_connections

    def get_connected_to(
        self,
        component: Component,
        clone: bool = True,
        include_all_connections: bool = False,
    ) -> list[Component]:
        """
        Returns all components connected to a certain component, including those from hierarchies

        :param component: Initial component to search from
        :type component: Component
        :param clone: Whether to clone the components, defaults to True
        :type clone: bool, optional
        :param include_all_connections: Whether to include non-signal connections, e.g. TLINE to calc block.
        :type include_all_connections: bool, optional
        :return: list of all components connected to the given component
        :rtype: list[Component]
        """

        draft = self.get_draft()
        graph: nx.Graph = draft.generate_full_graph()
        components = []

        excluded_edge_types: set[str] = set()
        if not include_all_connections:
            excluded_edge_types = {"TLINE_CALC"}

        visited = {component.uuid}
        stack = [(component.uuid, iter(graph[component.uuid]))]
        while stack:
            parent, children = stack[-1]
            try:
                child = next(children)
                if child not in visited:
                    etype = graph.edges[parent, child].get("type")
                    if etype not in excluded_edge_types:
                        components.append(draft.get_by_id(child))
                    stack.append((child, iter(graph[child])))
                    visited.add(child)
            except StopIteration:
                stack.pop()

        if clone:
            return copy.deepcopy(components)
        return components

    def get_at_point(self, uuid: str, point_name: str) -> list[tuple[str, str]]:
        """
        Returns a list of connection points at a given position on the grid.

        :param uuid: The UUID of the component to search from.
        :type uuid: str
        :param point_name: The name of the connection point to search from.
        :type point_name: str
        :return: list of (uuid, point_name) tuples.
        :rtype: list[tuple[str, str]]
        """
        if self._conn_graph is None:
            (
                self._conn_graph,
                self._pos_dict,
                self._link_dict,
            ) = self.__generate_conn_graph()
        pos_dict = self._pos_dict
        filtered_pos = filter(
            (
                lambda value: (
                    any([(tuple[0] == point_name and tuple[1] == uuid) for tuple in value])
                )
            ),
            pos_dict.values(),
        )
        return list(itertools.chain.from_iterable(filtered_pos))

    def get_connected_to_label(
        self,
        label_name: str,
        return_connecting: bool = False,
        callers: list["ComponentBox"] | None = None,
    ) -> list[Component]:
        """Returns all components connected to a wire or bus with a label with the given name.
        Returns the empty list if the label does not exist.

        :param label_name: The label of the bus or wire connection
        :type label_name: str

        :param return_connecting: If true, returns the connecting components.
        :type return_connecting: bool

        :param callers: list of ComponentBoxes that have already been called.
        :type callers: list[ComponentBox]

        :return: list of all components connected to the given label
        :rtype: list[Component]
        """
        if callers is None:
            callers = []
        # Find label (Wire or Bus)
        labels = list(
            filter(
                (lambda c: c.name == label_name and c.is_label),
                self.get_components(recursive=False, clone=False, with_groups=True),
            )
        )

        if len(labels) == 0:
            return []
        # Label found, start get_connected_at_point
        result = []
        for label in labels:
            result.extend(
                self.get_connected_at_component_point(
                    label.uuid,
                    label_name,
                    return_connecting,
                    None,
                    callers,
                )
            )
        # Remove duplicates
        for i, res in enumerate(result):
            for j in range(i + 1, len(result)):
                if res.uuid == result[j].uuid:
                    result.pop(j)
                    break
        return result

    def get_connected_at_component_point(
        self,
        uuid: str,
        point_name: str,
        return_connecting: bool = False,
        component_type: str | None = None,
        callers: list["ComponentBox"] | None = None,
    ) -> list[Component]:
        """Returns a list of all components connected at the connection point with the given name.
        Filters for components of a given type if component_type is specified.

        :param point_name: Name of the connection point
        :type point_name: str
        :param component_type: Only return components of this type, defaults to None
        :type component_type: str or None optional
        :param callers: list of components that have already been called, defaults to []
        :type callers: list[ComponentBox] optional

        :return: list of all components connected to the given label
        :rtype: list[Component]
        """
        if callers is None:
            callers = []
        if self._conn_graph is None:
            (
                self._conn_graph,
                self._pos_dict,
                self._link_dict,
            ) = self.__generate_conn_graph()

        connected_components: list[Component] = []
        component_queue = queue.SimpleQueue()  # Type: Queue[tuple[uuid, point_name]]
        component_queue.put((point_name, uuid))

        hierarchy_queue = queue.SimpleQueue()  # Type: Queue[ComponentBox]

        connection_name = self.get_by_id(uuid).name if self.get_by_id(uuid).is_label else ""

        while not component_queue.empty():
            (p_name, p_uuid) = component_queue.get()
            connected_to = self.get_at_point(p_uuid, p_name)
            # Check link dictionary for new connections
            if any(
                map(
                    (lambda x: p_uuid in map(lambda entry: entry[0], x)),
                    self.get_link_dict().values(),
                )
            ):
                for _, values in self.get_link_dict().items():
                    link_uuids = list(map(lambda entry: entry[0], values))
                    if p_uuid in link_uuids:
                        for link_uuid in link_uuids:
                            if link_uuid != p_uuid:
                                # Add (Point name, uuid)
                                connected_to.append((values[1], link_uuid))

            for point_name, conn_uuid in connected_to:
                # Only add if not already in the list or the current component from the queue
                if (
                    not any(map((lambda c: c.uuid == conn_uuid), connected_components))
                    and conn_uuid != p_uuid
                ):
                    component = self.get_by_id(conn_uuid)
                    if component is not None and component.is_connecting:
                        # Add to the queue if it is a connecting component
                        component_queue.put((point_name, conn_uuid))

                    if (
                        component is not None
                        and not component.is_connecting
                        and not component.uuid in [c.uuid for c in connected_components]
                    ):
                        # Add to the result, but not the queue
                        connected_components.append(component)

                    # Set connection label for other layers
                    if component.is_label:
                        # Label found, set label for whole connection
                        if not connection_name in ("", component.name):
                            print(
                                "WARNING: Multiple labels found on connection: "
                                + f"{connection_name}, {component.name}"
                            )
                        connection_name = component.name

                    if isinstance(component, ComponentBox):
                        hierarchy_queue.put(component)

            if not p_uuid in [c.uuid for c in connected_components]:
                # Add component to the list of connected components
                new_component = self.get_by_id(p_uuid)
                connected_components.append(new_component)
                for conn_list in new_component.generate_pos_dict().values():
                    for point_name in [p[0] for p in conn_list]:
                        if point_name != p_name and new_component.is_connecting:
                            # Add connected components to result
                            component_queue.put((point_name, p_uuid))

        # Check if any of the connected components are hierarchy connecting
        if any(
            map(
                (lambda c: c.is_hierarchy_connecting),
                connected_components + [self.get_by_id(uuid)],
            )
        ):
            boxes: list[ComponentBox] = (
                [self.box_parent] if isinstance(self.box_parent, ComponentBox) else []
            )
            boxes += self.get_component_boxes(False)
            for box in boxes:
                hierarchy_queue.put(box)

        # Search in hierarchy queue
        hierarchies = []
        while not hierarchy_queue.empty():
            hierarchy = hierarchy_queue.get()
            if not hierarchy in hierarchies:
                hierarchies.append(hierarchy)

        for hierarchy in hierarchies:
            # hierarchy: ComponentBox = hierarchy_queue.get()
            if not hierarchy in callers:
                connected_components.extend(
                    hierarchy.get_connected_to_label(
                        connection_name, return_connecting, callers + [self]
                    )
                )

        if not return_connecting:
            connected_components = [
                c
                for c in connected_components
                if not (c.is_connecting or c.is_hierarchy_connecting)
            ]
        if component_type is not None:
            connected_components = [c for c in connected_components if c.type == component_type]

        for i, conn_comp in enumerate(connected_components):
            for j in range(i + 1, len(connected_components)):
                if conn_comp.uuid == connected_components[j].uuid:
                    connected_components.pop(j)
                    break

        return connected_components


def add_xrack_connections(xrack_connections: dict, graph: Graph, mark_xrack: bool) -> None:
    for key, value in xrack_connections.items():
        ctype = None
        if key[1] in {"lf_rtds_sharc_sld_TLINE", "_rtds_CABLE1.def"}:
            ctype = "TLINE_CONNECTED"
        elif key[1] == "lf_rtds_sharc_sld_TL16CAL":
            endpoints = xrack_connections.get((key[0], "lf_rtds_sharc_sld_TLINE"))
            if endpoints:
                for e in endpoints:
                    if not graph.has_edge(value[0], e):
                        graph.add_edge(value[0], e, type="TLINE_CALC", xrack=mark_xrack)
        elif key[1] == "_rtds_CBLCAL.def":
            endpoints = xrack_connections.get((key[0], "_rtds_CABLE1.def"))
            if endpoints:
                for e in endpoints:
                    if not graph.has_edge(value[0], e):
                        graph.add_edge(value[0], e, type="TLINE_CALC", xrack=mark_xrack)
        elif "rtds_XRTRF" in key[1]:
            ctype = "XRTRF_CONNECTED"
        for i, j in itertools.combinations(value, 2):
            if not graph.has_edge(i, j):
                graph.add_edge(i, j, type=ctype, xrack=mark_xrack)


## PREVIOUS HOOK METHODS
# xr_trf_hook
def link_connections(components: list) -> list[tuple[str, str, str, NodeType]]:
    """Add entries to link_dict for Crossrack Transformers.

    :param components: list of components
    :type components: list[Component]
    :return: list of connections in form [(name, component_uuid, point_name, node_type), ...]
    :rtype: list[tuple[str, str, str, node_type]]
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
                    NodeType.NAME_CONNECTED_LINKED,
                )
            )
    return result


# linked_node_hook
def graph_connections_linked(components: list) -> list[tuple[str, str, str]]:
    """Connects nodes that have the "linkNode" property set to "yes"."""
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
        for left, right in itertools.combinations(names, 2):
            edges.append((left, right, "LINK_CONNECTED"))

    return edges


# tline_hook
def graph_connections_tline(components: list, pos_dict: dict) -> list[tuple[str, str, str]]:
    tnam1_dict = {}
    result = []
    for _, comps in pos_dict.items():
        for i in range(len(comps)):
            filtered = list(
                filter(
                    (lambda c: c.type == "lf_rtds_sharc_sld_TLINE" and c.uuid == comps[i][1]),
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
    for i, _ in enumerate(components):
        comp = components[i]
        if comp.type == "lf_rtds_sharc_sld_TL16CAL":
            if comp.name in tnam1_dict:
                tnam1_dict[comp.name].append(comp.uuid)
            else:
                tnam1_dict[comp.name] = [comp.uuid]

    for _, uuids in tnam1_dict.items():
        for left, right in itertools.combinations(set(uuids), 2):
            result.append((left, right, "TLINE_CONNECTED"))

    return result
