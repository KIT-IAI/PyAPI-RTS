from pathlib import Path
from typing import Self

import networkx

from pyapi_rts.component_graph.constants import *
from pyapi_rts.fx_api.component import FxComponent
from pyapi_rts.fx_api.protocols import SubPageProtocol, ComponentProtocol


class LayoutGenerator:
    def __init__(
            self,
            column_count: int,
            row_count: int,
            default_width=160,
            default_height=160,
            x_offset=144,
            y_offset=144,
            block_size=32
    ):
        self.block_size = block_size
        self.grid = [
            [
                (
                    x * default_width,
                    y * default_height,
                    (x + 1) * default_width - block_size,
                    (y + 1) * default_height - block_size
                )
                for y in range(row_count)
            ]
            for x in range(column_count)
        ]
        self.column_count = column_count
        self.row_count = row_count
        self.x_offset = x_offset
        self.y_offset = y_offset
        self.components: dict[int, dict[int, FxComponent | None]] = {
            x: {
                y: None
                for y in range(row_count)
            }
            for x in range(column_count)
        }
        # self.connections: dict[tuple[int, int, int], tuple[int, str, str]] = {}
        self.simple_connections: dict[tuple[int, int, int], int] = {}

    @property
    def grid_size(self) -> tuple[int, int]:
        x, y = self.get_end_position(self.column_count - 1, self.row_count - 1)
        return x + self.block_size // 2, y + self.block_size // 2

    @classmethod
    def create_from_component_tree(cls, tree: networkx.DiGraph, subpage: SubPageProtocol | None, **kwargs) -> Self:
        column_count = max(column for _, column in tree.nodes(data=COLUMN)) + 1
        row_count = max(max_row for _, max_row in tree.nodes(data=MAX_ROW)) + 1
        layout_generator = cls(column_count, row_count, **kwargs)
        layout_generator.fill_from_graph(tree, subpage)
        return layout_generator

    def render_grid_with_annotations(self, subpage: SubPageProtocol):
        for x in range(self.column_count):
            for y in range(self.row_count):
                x_pos, y_pos = self.get_position(x, y)
                grid_corner: ComponentProtocol | None = subpage.insert_component(
                    'annotation',
                    x_pos,
                    y_pos - self.block_size
                )
                if grid_corner is None:
                    raise RuntimeError('Could not place annotation for grid')
                grid_corner.set_parameter('AL1', '')
                grid_corner.set_parameter('AL2', '_|_')

    def get_position(self, x: int, y: int) -> tuple[int, int]:
        return self.x_offset + self.grid[x][y][0], self.y_offset + self.grid[x][y][1]

    def get_end_position(self, x: int, y: int) -> tuple[int, int]:
        return self.x_offset + self.grid[x][y][2], self.y_offset + self.grid[x][y][3]

    def place_component(self, component: FxComponent, x: int, y: int):
        if self.components[x][y] is not None:
            raise RuntimeError('Slot is already taken')
        self.components[x][y] = component

    def place_component_in_range(self, component: FxComponent, x: int, y_range: list[int]):
        for y in y_range:
            self.place_component(component, x, y)

    def get_component_y_span(self, component: FxComponent, column: int) -> tuple[int, int]:
        column_items = self.components[column]
        for start_row, row_component in column_items.items():
            if row_component is component:
                row = start_row
                while row_component is component:
                    row += 1
                    row_component = column_items.get(row, None)
                return start_row, row - 1
        raise ValueError('Component not found in specified column')

    def _collect_connections(self, tree: networkx.DiGraph):
        for u, v, edge_type in tree.edges(data=EDGE_TYPE):
            source_column = tree.nodes[u][COLUMN]
            target_column = tree.nodes[v][COLUMN]
            row = tree.nodes[v][MIN_ROW]
            self.simple_connections[(source_column, target_column, row)] = 3 if edge_type == 'ABC' else 1

    def fill_from_graph(self, component_graph: networkx.DiGraph, subpage: SubPageProtocol | None):
        self._collect_connections(component_graph)
        ordered_node_list = sorted(component_graph.nodes(data=True), key=lambda n: n[1].get('_column'))
        for node, data in ordered_node_list:
            x = data[COLUMN]
            y_range = list(range(data[MIN_ROW], data[MAX_ROW] + 1))

            if subpage is None:
                component = FxComponent.create_detached(
                    data[COMPONENT_TYPE],
                    **data
                )
            else:
                component = FxComponent.create_new(
                    subpage,
                    data[COMPONENT_TYPE],
                    *self.get_position(x, y_range[0]),
                    **data
                )
                self._vertical_wiring(component, x, (y_range[0], y_range[-1]), subpage)
                self._horizontal_wiring(component, x, y_range[0], subpage)
            self.place_component_in_range(component, x, y_range)

    def _vertical_wiring(self, component: FxComponent, column: int, y_span: tuple[int, int], subpage: SubPageProtocol):
        if component.is_detached:
            raise RuntimeError('Can only wire an attached component')
        # height = y_span[1] - y_span[0] + 1
        # if height > 1:
        if component.is_connecting:
            connecting_point = next(iter(component.connection_points.values())).position_abs
            _, end_y = self.get_end_position(column, y_span[1])
            subpage.create_wire(len(component.connection_points), [
                connecting_point,
                (connecting_point[0], end_y)
            ])
            _ = 42

    def _horizontal_wiring(
            self,
            component: FxComponent,
            column: int,
            row: int,
            # tree: networkx.DiGraph,
            subpage: SubPageProtocol
    ):
        # Connects a component to its direct predecessor
        if component.is_detached:
            raise RuntimeError('Can only wire an attached component')
        if column == 0:
            return
        predecessor = self.components[column - 1][row]
        assert predecessor is not None
        phase_count = self.simple_connections[(column - 1, column, row)]

        start_coordinates = get_rightmost_connection_point_coordinates(predecessor)
        end_coordinates = get_leftmost_connection_point_coordinates(component)
        middle_points = []

        if predecessor.is_connecting:
            # use the y component from the target if we connect a bus on the left and the point is equal or below
            if end_coordinates[1] >= start_coordinates[1]:
                start_coordinates = (start_coordinates[0], end_coordinates[1])

        if start_coordinates[1] != end_coordinates[1]:
            # y mismatch between the coordinates -> need to add a middle point
            middle_points.append((end_coordinates[0], start_coordinates[1]))

        subpage.create_wire(phase_count, [
            start_coordinates,
            *middle_points,
            end_coordinates
        ])

    def attach(self, subpage: SubPageProtocol):
        for column, row_lookup in self.components.items():
            for row, component in row_lookup.items():
                if component is not None and component.is_detached:
                    x, y = self.get_position(column, row)
                    bb_offset = get_grid_aligned_bounding_box_offset(component)
                    component.attach(
                        subpage,
                        x - bb_offset[0],
                        y - bb_offset[1]
                    )
                    row_range = self.get_component_y_span(component, column)
                    self._vertical_wiring(component, column, row_range, subpage)
                    self._horizontal_wiring(component, column, row_range[0], subpage)

    # TODO the following two calculate methods have just been copied from the old layout code and might need modifications
    def calculate_height(self, base_height: int, block_size=32, level_height=5) -> int:
        return base_height * block_size * level_height + (base_height - 1) * block_size

    def calculate_y(self, slot_y: int, start_y: int, block_size=32, level_height=5) -> int:
        return start_y + slot_y * block_size * (level_height + 1)


def get_rightmost_connection_point_coordinates(component: FxComponent) -> tuple[int, int]:
    return max(component.connection_points.values(), key=lambda cp: cp.position_abs[0]).position_abs


def get_leftmost_connection_point_coordinates(component: FxComponent) -> tuple[int, int]:
    return min(component.connection_points.values(), key=lambda cp: cp.position_abs[0]).position_abs


def load_prepared_component_graph(path: Path) -> networkx.DiGraph:
    graph = networkx.read_graphml(path, edge_key_type=tuple[str, str])
    return graph


def get_grid_aligned_bounding_box_offset(component: FxComponent, grid_size=32) -> tuple[int, int]:
    return (
        (component.bounding_box[0] // grid_size) * grid_size,
        (component.bounding_box[1] // grid_size) * grid_size,
    )

