from typing import Any, Iterable

import networkx

from pyapi_rts.component_graph.constants import *


def find_longest_path_dfs(graph: networkx.Graph):
    def dfs(node, visited):
        paths = [[node]]
        for neighbor in graph.neighbors(node):
            if neighbor not in visited:
                for path in dfs(neighbor, visited | {neighbor}):
                    paths.append([node] + path)
        return paths

    longest = []
    for node in graph.nodes:
        for path in dfs(node, {node}):
            if len(path) > len(longest):
                longest = path
    return longest


def find_valid_root_element(graph: networkx.Graph, node_name_list: Iterable[str]) -> tuple[int, Any] | tuple[None, None]:
    for idx, name in enumerate(node_name_list):
        node = graph.nodes[name]
        component_type = node[COMPONENT_TYPE]

        valid_root_types = {  # TODO this list should be generated from the component classes - it should be checked somehow
            'rtds_sharc_sld_BUSLABEL',
            'rtds_sharc_node'
        }
        if component_type in valid_root_types:
            return idx, name
    return None, None


def find_center_bus(graph: networkx.Graph, longest_path: list[Any]) -> Any:
    middle_index = len(longest_path) // 2
    left_index, leftward_root = find_valid_root_element(graph, longest_path[middle_index::-1])
    if left_index is not None and left_index <= 1:
        root = leftward_root
    else:
        right_index, rightward_root = find_valid_root_element(graph, longest_path[middle_index:])
        if left_index is None and right_index is None:
            raise RuntimeError('No proper root can be found')
        elif left_index is None:
            root = rightward_root
        elif right_index is None:
            root = leftward_root
        elif left_index <= right_index:
            root = leftward_root
        else:
            root = rightward_root
    return root


def orient_graph_by_bfs(graph: networkx.Graph, root: Any):
    directed_graph = networkx.DiGraph()
    directed_graph.add_nodes_from(graph.nodes(data=True))

    tree = networkx.bfs_tree(graph, root)

    for u, v, data in graph.edges(data=True):
        # If edge direction is consistent with BFS depth, point downward
        if tree.has_node(u) and tree.has_node(v):  # checking for both nodes fixes islands
            depth_u = networkx.shortest_path_length(tree, root, u)
            depth_v = networkx.shortest_path_length(tree, root, v)

            if depth_u <= depth_v:
                directed_graph.add_edge(u, v, **data)
            elif depth_v < depth_u:
                directed_graph.add_edge(v, u, **data)
    return directed_graph


def convert_undirected_component_graph(graph: networkx.Graph, auto_balance=True) -> networkx.DiGraph:
    if auto_balance:
        longest_path = find_longest_path_dfs(graph)
        root = find_center_bus(graph, longest_path)
    else:
        _, root = find_valid_root_element(graph, graph.nodes)
    return orient_graph_by_bfs(graph, root)
