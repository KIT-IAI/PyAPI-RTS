from enum import Enum
import itertools

import networkx as nx


class EdgeType(Enum):
    GRID = 1
    """Default connection type. This is defined by connection points touching on the grid."""
    NAME = 2
    """Connections defined by bus labels touching hierarchies."""
    LABEL = 3
    """Connections defined by wire labels."""
    TLINE = 4
    """Connections between endpoints of a transmission line or cable."""
    XRTRF = 5
    """Connections between endpoints of a cross-rack transformer."""
    LINK = 6
    """Connections defined by linked bus labels or nodes."""
    TLINE_CALC = 7
    """Connections between the endpoints of a transmission line or cable\
        and the corresponding calculation block."""


def add_xrack_connections(
    xrack_connections: dict[tuple[str, str], list[str]], graph: nx.MultiGraph, mark_xrack: bool
) -> None:
    """Add the xrack connections to the graph. From a given dictionary.

    :param xrack_connections: Dictionary mapping name and component type to a list of uuids.
    :type xrack_connections: dict[tuple[str, str], list[str]]
    :param graph: The graph to add the connections to.
    :type graph: Graph
    :param mark_xrack: Whether to mark the connections as xrack connections.
    :type mark_xrack: bool
    """
    for key, value in xrack_connections.items():
        ctype = None
        if key[1] in {"lf_rtds_sharc_sld_TLINE", "_rtds_CABLE1.def"}:
            ctype = EdgeType.TLINE
        elif key[1] == "lf_rtds_sharc_sld_TL16CAL":
            for endpoint in xrack_connections.get((key[0], "lf_rtds_sharc_sld_TLINE"), []):
                if not graph.has_edge(value[0], endpoint):
                    graph.add_edge(value[0], endpoint, type=EdgeType.TLINE_CALC, xrack=mark_xrack)
        elif key[1] == "_rtds_CBLCAL.def":
            for endpoint in xrack_connections.get((key[0], "_rtds_CABLE1.def"), []):
                if not graph.has_edge(value[0], endpoint):
                    graph.add_edge(value[0], endpoint, type=EdgeType.TLINE_CALC, xrack=mark_xrack)
        elif "rtds_XRTRF" in key[1]:
            ctype = EdgeType.XRTRF
        for i, j in itertools.combinations(value, 2):
            if not graph.has_edge(i, j):
                graph.add_edge(i, j, type=ctype, xrack=mark_xrack)


def get_connected_to(
    graph: nx.MultiGraph,
    source: str,
    excluded_edge_types: set[EdgeType] | None = None,
) -> list[str]:
    """Returns all components connected to a certain component, including those from hierarchies

    :param component: UUID of initial component to search from
    :type component: str
    :param excluded_edge_types: Set of edge types to exclude from the search. Defaults to TLINE_CALC.
    :type excluded_edge_types: set[EdgeType], optional
    :return: List of UUIDs of all components connected to the given component
    :rtype: list[str]
    """
    components: list[str] = []

    if excluded_edge_types is None:
        excluded_edge_types = {EdgeType.TLINE_CALC}

    visited = {source}
    stack = [(source, iter(graph[source]))]
    while stack:
        parent, children = stack[-1]
        try:
            child = next(children)
            if child not in visited:
                etype = graph.edges[parent, child, 0].get("type")
                if etype not in excluded_edge_types:
                    components.append(child)
                stack.append((child, iter(graph[child])))
                visited.add(child)
        except StopIteration:
            stack.pop()

    return components
