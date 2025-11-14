import collections
from typing import Any

import networkx

from pyapi_rts.component_graph.constants import *
from pyapi_rts.component_graph.reshape import convert_undirected_component_graph
from pyapi_rts.component_graph.tree_forming import resolve_loops_in_oriented_component_graph


def subtree_depth(tree: networkx.DiGraph, node: Any):
    if tree.out_degree(node) == 0:
        return 0
    else:
        return 1 + max(subtree_depth(tree, child) for child in tree.successors(node))


def add_node_weights(tree: networkx.DiGraph, root: str, sort_by=COLUMN):
    tree.nodes[root][WEIGHT] = subtree_depth(tree, root)

    node_list = tree.nodes
    if sort_by is not None:
        node_list = sorted(tree.nodes, key=lambda n: tree.nodes[n][sort_by])

    for node in node_list:
        parent_weight = tree.nodes[node][WEIGHT]
        for child in tree.successors(node):
            tree.nodes[child][WEIGHT] = 10 * parent_weight + subtree_depth(tree, child)


def get_parent_dimensions(child_slots: list[tuple[int, int]], baseline: tuple[int, int]) -> tuple[int, int]:
    if not child_slots:
        return baseline
    if len(child_slots) == 1:
        return child_slots[0][0], child_slots[0][0]
    return child_slots[0][1], child_slots[-1][0]


def calculate_position_and_adjust_height_with_existing_column_data(tree: networkx.DiGraph, root: str):
    max_used_slot_per_level = collections.defaultdict(lambda: -1)

    def shift_children_if_necessary(node: str, delta: int):
        children = list(tree.successors(node))
        children.sort(key=lambda c: tree.nodes[c][WEIGHT], reverse=True)
        slot = tree.nodes[node][VERTICAL_POSITION]
        child_slots = [tree.nodes[child][VERTICAL_POSITION] for child in children]
        expected_slot = get_parent_dimensions(child_slots, slot)
        if expected_slot[0] < slot[0] or expected_slot[1] > slot[1]:
            # shift is necessary
            for child in children:
                child_slot = tree.nodes[child][VERTICAL_POSITION]
                set_node_positional_data(child, (child_slot[0] + delta, child_slot[1] + delta))
                shift_children_if_necessary(child, delta)

    def set_node_positional_data(node: str, slot: tuple[int, int]):
        depth = tree.nodes[node][COLUMN]
        max_used_slot_per_level[depth] = slot[1]
        tree.nodes[node][VERTICAL_POSITION] = slot

    def recurse(node: str, baseline: tuple[int, int]) -> tuple[int, int]:
        children = list(tree.successors(node))
        children.sort(key=lambda c: tree.nodes[c][WEIGHT], reverse=True)

        # child_intervals = []
        child_slots = []
        next_child_slot = last_child_slot = baseline
        # all_child_min = -1
        for child in children:
            child_min, child_max = last_child_slot = recurse(child, next_child_slot)
            # all_child_min = min(x for x in [child_min, all_child_min] if x >= 0)
            next_child_slot = (child_max + 1, child_max + 1)
            child_slots.append(last_child_slot)

        current_slot = get_parent_dimensions(child_slots, baseline)
        depth = tree.nodes[node][COLUMN]

        # current_slot = (max([*baseline, all_child_min]), min(last_child_slot))
        delta = max_used_slot_per_level[depth] + 1 - current_slot[0]
        if delta > 0:
            current_slot = (current_slot[0] + delta, current_slot[1] + delta)
        set_node_positional_data(node, current_slot)
        if delta > 0:
            shift_children_if_necessary(node, delta)
        return current_slot

    recurse(root, (0, 0))


# def assign_vertical_position_to_edges(tree: networkx.DiGraph):
#     for start, end, data in tree.edges(data=True):
#         start_pos = tree.nodes[start][VERTICAL_POSITION]
#         end_pos = tree.nodes[end][VERTICAL_POSITION]
#         result_pos_set = {*range(start_pos[0], start_pos[1] + 1)} & \
#             {*range(end_pos[0], end_pos[1] + 1)}
#         if len(result_pos_set) > 1:
#             raise RuntimeError('Could not exactly pin down edge location')
#         result_pos = result_pos_set.pop()
#         data[ROW] = result_pos


def convert_position_tuples(tree: networkx.DiGraph):
    for _, node_data in tree.nodes(data=True):
        pos = node_data[VERTICAL_POSITION]
        del node_data[VERTICAL_POSITION]
        node_data[MIN_ROW] = pos[0]
        node_data[MAX_ROW] = pos[1]


def calculate_minimum_height(tree: networkx.DiGraph, root: str):
    def recurse(node: str, depth: int):
        children = list(tree.successors(node))
        children.sort(key=lambda c: tree.nodes[c][WEIGHT], reverse=True)

        min_sizes = []
        for child in children:
            min_sizes.append(recurse(child, depth + 1))

        if not min_sizes:
            min_height = 1
        elif len(min_sizes) == 1:
            min_height = 1
        elif len(min_sizes) == 2:
            min_height = 2
        else:
            min_height = 2 + sum(min_sizes[1:-1])

        tree.nodes[node][MIN_HEIGHT] = min_height
        return min_height

    recurse(root, 0)


def find_root(tree: networkx.DiGraph) -> Any:
    first_node, first_data = next(iter(tree.nodes(data=True)))
    if COLUMN in first_data:
        return [node for node, data in tree.nodes(data=True) if data[COLUMN] == 0]
    potential_root_nodes = [
        node
        for node in tree.nodes
        if tree.out_degree(node) > 0
        and tree.in_degree(node) == 0
    ]
    if len(potential_root_nodes) != 1:
        raise ValueError('The specified graph seems to be malformed and no clear root could be found')
    return potential_root_nodes[0]


def add_node_column_data(tree: networkx.DiGraph, root: Any):
    # this does not handle potential cycles so the cycles must be removed first
    for node, data in tree.nodes(data=True):
        data[COLUMN] = networkx.shortest_path_length(tree, root, node)


def convert_undirected_component_graph_and_add_layout_info(
        graph: networkx.Graph,
        auto_balance=True
) -> networkx.DiGraph:
    directed_graph = convert_undirected_component_graph(graph, auto_balance)

    resolve_loops_in_oriented_component_graph(directed_graph)
    tree = directed_graph

    add_layout_info_to_component_tree(tree)
    return tree


def add_layout_info_to_component_tree(tree: networkx.DiGraph, root: Any = None):
    if root is None:
        root = find_root(tree)
    add_node_column_data(tree, root)
    add_node_weights(tree, root)
    calculate_minimum_height(tree, root)
    calculate_position_and_adjust_height_with_existing_column_data(tree, root)
    convert_position_tuples(tree)


