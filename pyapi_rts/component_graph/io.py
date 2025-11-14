import io
from pathlib import Path

import networkx

from pyapi_rts.component_graph.constants import *


def serialize_layouted_tree(tree: networkx.DiGraph, output: str | Path | io.TextIOBase):
    graph_data = tree.graph.setdefault('graph', {})
    graph_data['rankdir'] = 'LR'
    graph_data['layout'] = 'neato'
    add_graphviz_layout_info(tree)

    dot = dottify_graph(tree)

    if isinstance(output, str):
        output = Path(output)
    if isinstance(output, Path):
        output.write_text(dot)
    else:
        output.write(dot)


def dottify_graph(graph: networkx.Graph) -> str:
    return str(networkx.nx_pydot.to_pydot(graph))


def get_height_from_slot(slot: tuple[int, int]) -> int:
    return slot[1] - slot[0] + 1


def add_graphviz_layout_info(graph: networkx.Graph):
    for node, data in graph.nodes(data=True):
        slot = data[MIN_ROW], data[MAX_ROW]
        column = data[COLUMN]
        height = get_height_from_slot(slot)
        graph.nodes[node][GV_HEIGHT] = height
        graph.nodes[node][GV_POS] = f'{column},{slot[0] + height / 2}!'
