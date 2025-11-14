from typing import Protocol, Any


class ComponentProtocol(Protocol):
    component_type: str
    parameters: list[str]

    def set_parameter(self, key: str, value: Any):
        ...

    def get_parameter(self, key: str) -> Any:
        ...


class SubPageProtocol(Protocol):
    def insert_component(self, component_type: str, x: int, y: int) -> ComponentProtocol:
        ...

    def create_wire(self, phase_count: int, points: list[tuple[int, int]]):
        ...


class CaseProtocol(Protocol):
    def save(self, path: str | None):
        ...

    def close(self):
        ...


class AppProtocol(Protocol):
    def new_case(self) -> CaseProtocol:
        ...

    def open_case(self, file: str) -> CaseProtocol:
        ...


class ComponentMock:
    def __init__(self, component_type: str, location: tuple[int, int]):
        self.component_type = component_type
        self.location = location
        self.parameters = {}

    def set_parameter(self, key: str, value: Any):
        self.parameters[key] = value

    def get_parameter(self, key: str) -> Any:
        return self.parameters[key]


class SubPageMock:
    def __init__(self):
        self.components: list[ComponentMock] = []
        self.wires: list[tuple[int, list[tuple[int, int]]]] = []

    def insert_component(self, component_type: str, x: int, y: int) -> ComponentMock:
        component = ComponentMock(component_type, (x, y))
        self.components.append(component)
        return component

    def create_wire(self, phase_count: int, points: list[tuple[int, int]]):
        self.wires.append((phase_count, points))
