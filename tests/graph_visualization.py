# LGPL-3.0 License
# Copyright (c) 2023 KIT-IAI-ESA

import matplotlib.pyplot as plt
import networkx as nx


def visualize_graph(
    graph: nx.Graph,
    show_labels: bool = False,
    file_name: str = None,
    layout=None,
    width: float = 14,
    height: float = 14,
):
    """Visualize network graph."""

    colors = [_color_node_type(x[1]["type"]) for x in graph.nodes.data()]
    max_depth = max((x[1]["depth"] for x in graph.nodes.data()))
    min_depth = min((x[1]["depth"] for x in graph.nodes.data()))
    if max_depth == 0 or max_depth == min_depth:
        max_depth = 999
    alpha = [1 - (x[1]["depth"] / max_depth) * 0.85 for x in graph.nodes.data()]
    # alpha = [1 for x in graph.nodes.data()]

    edge_colors = [_color_edge_type(x[2].get("type")) for x in graph.edges.data()]
    edge_style = ["dashed" if x[2].get("xrack") else "solid" for x in graph.edges.data()]

    if layout is None:
        pos = nx.spring_layout(graph)
    else:
        pos = layout

    plt.figure(figsize=(width, height))
    nx.draw_networkx_nodes(
        graph,
        pos=pos,
        node_color=colors,
        alpha=alpha,
    )
    nx.draw_networkx_edges(
        graph,
        pos=pos,
        edge_color=edge_colors,
        style=edge_style,
    )
    if show_labels:
        labels = {n: graph.nodes[n]["type"] for n in graph}
        nx.draw_networkx_labels(graph, pos, labels=labels)

    plt.tight_layout()
    if file_name is not None:
        plt.savefig(file_name)
    else:
        plt.show()
    return pos


def _color_node_type(ntype: str) -> str:
    if ntype in {"BUS", "WIRE"}:
        return "#dddddd"
    if ntype == "rtds_sharc_sld_BUSLABEL":
        return "#d80000"
    if ntype == "HIERARCHY":
        return "#1ed30a"
    if ntype == "wirelabel":
        return "#eadb07"
    if ntype == "lf_rtds_sharc_sld_TLINE":
        return "#fc02f8"
    if ntype in {"lf_rtds_sharc_sld_TL16CAL"}:
        return "#fc92fa"
    if ntype == "rtds_sharc_node":
        return "#0000dd"
    return "#0a72d3"


def _color_edge_type(etype: str) -> str:
    if etype is None:
        # grid-based
        return "#000000"
    if etype == "NAME_CONNECTED":
        # grid-based hierarchy
        return "#d80000"
    if etype == "LABEL_CONNECTED":
        return "#eadb07"
    if etype in {"TLINE_CONNECTED", "XRTRF_CONNECTED"}:
        return "#fc02f8"
    if etype == "LINK_CONNECTED":
        return "#8302fc"
    if etype == "XRACK_CONNECTED":
        return "#05f0fc"
    if etype == "TLINE_CALC":
        return "#fc92fa"
    return "#000000"
