import networkx

from pyapi_rts.component_graph.constants import COMPONENT_TYPE
from pyapi_rts.component_graph.reshape import find_valid_root_element


def resolve_loops_in_oriented_component_graph(oriented_component_graph: networkx.DiGraph):
    link_node_variable_name_lookup = {
        'rtds_sharc_sld_BUSLABEL': 'linkNodes',
        'rtds_sharc_node': 'linkNode'
    }

    for node, data in list(oriented_component_graph.nodes(data=True)):
        excess_predecessors = list(oriented_component_graph.predecessors(node))[1:]
        if not excess_predecessors:
            continue
        _, multivalued_node = find_valid_root_element(oriented_component_graph, [node])
        if multivalued_node is not None:
            node_data = oriented_component_graph.nodes[node]
            node_data[
                link_node_variable_name_lookup[node_data[COMPONENT_TYPE]]
            ] = 'Yes'
            for idx, predecessor in enumerate(excess_predecessors):
                linked_node = f'{node}_linked_{idx}'
                oriented_component_graph.add_node(linked_node, **node_data)
                edge_data = oriented_component_graph.edges[predecessor, multivalued_node]
                oriented_component_graph.add_edge(predecessor, linked_node, **edge_data)
                oriented_component_graph.remove_edge(predecessor, multivalued_node)
        else:
            # this is for example a line, transformer, or any other element that has more predecessors but is not a bus
            for idx, predecessor in enumerate(excess_predecessors):
                predecessor_data = oriented_component_graph.nodes(data=True)[predecessor]
                predecessor_data[link_node_variable_name_lookup[predecessor_data[COMPONENT_TYPE]]] = 'Yes'
                linked_node = f'{predecessor}_linked_from_{node}'
                oriented_component_graph.add_node(linked_node, **predecessor_data)

                edge_data = oriented_component_graph.get_edge_data(predecessor, node)
                oriented_component_graph.add_edge(node, linked_node, **edge_data)
                oriented_component_graph.remove_edge(predecessor, node)
