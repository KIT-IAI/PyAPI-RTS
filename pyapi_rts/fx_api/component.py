from abc import ABC
from enum import Enum
import importlib
from typing import Self, Any

from pyapi_rts.api import Component
from pyapi_rts.fx_api.protocols import SubPageProtocol, ComponentProtocol


class FxComponent(Component, ABC):
    GENERATED_CLASS_MODULE_PATH = 'pyapi_rts.generated2'

    def __init__(
            self,
            handle: ComponentProtocol | None,
            location: tuple[int, int] = None,
            orientation: int = None,
            **_
    ):
        super().__init__()
        self.handle = handle
        if location is not None:
            self.location = location
        if orientation is not None:
            self.orientation = orientation

    def read_parameters(self, data: dict[str, Any]):
        for key, value in data.items():
            if not key.startswith('_'):
                self.set_parameter(key, value)

    def set_parameter(self, key: str, value: Any):
        self.set_by_key(key, value)
        if self.handle is not None:
            if isinstance(value, Enum):
                value = value.value
            self.handle.set_parameter(key, value)

    def attach(self, subpage: SubPageProtocol, x: int, y: int):
        handle: ComponentProtocol | None = subpage.insert_component(self.type, x, y)
        if handle is None:
            raise RuntimeError('Could not attach component')
        self.handle = handle
        self.x = x
        self.y = y
        self.sync_parameters()

    def sync_parameters(self, to_rscad: bool = True, from_rscad: bool = False):
        if self.is_detached:
            raise RuntimeError('Can only sync an attached component')
        for param in self.handle.parameters:
            if to_rscad:
                value = self.get_by_key(param)
                if isinstance(value, Enum):
                    value = value.value
                self.handle.set_parameter(param, value)
            if from_rscad:
                self.set_by_key(param, self.handle.get_parameter(param))
        if to_rscad:
            self.handle.orientation = self.orientation
            self.handle.location = self.location
        if from_rscad:
            self.orientation = self.handle.orientation
            self.location = self.handle.location

    @property
    def location(self) -> tuple[int, int]:
        return self.x, self.y

    @location.setter
    def location(self, loc: tuple[int, int]):
        self.x, self.y = loc
        if self.handle is not None:
            self.handle.location = loc

    @property
    def orientation(self) -> int:
        return self.rotation * 90

    @orientation.setter
    def orientation(self, orient: int):
        self.rotation = orient // 90
        if self.handle is not None:
            self.handle.orientation = orient

    @property
    def is_detached(self) -> bool:
        return self.handle is None

    @classmethod
    def create_new(cls, subpage: SubPageProtocol, component_type: str, x: int, y: int, **kwargs) -> Self:
        handle: ComponentProtocol | None = subpage.insert_component(component_type, x, y)
        if handle is None:
            return None
        return cls.create_from_handle(handle, **kwargs)

    @classmethod
    def create_detached(cls, component_type: str, **kwargs) -> Self:
        component_class = cls._get_component_class_from_type_string(component_type)
        component_class.type = component_type  # TODO discuss if we do that in the code gen instead
        return component_class(None, **kwargs)

    @classmethod
    def _get_component_class_from_type_string(cls, component_type: str) -> type[Self]:
        try:
            sanitized_name = component_type.replace('.', '_')
            module = importlib.import_module(f'{cls.GENERATED_CLASS_MODULE_PATH}.{sanitized_name}')
            for key in dir(module):
                item = getattr(module, key)
                if issubclass(item, cls) and item is not cls:
                    return item
        except Exception as e:
            raise Exception(f'import of {component_type} failed') from e
        raise Exception(f'component type "{component_type}" could not be found')

    @classmethod
    def create_from_handle(cls, handle: ComponentProtocol, **kwargs) -> Self:
        component_class = cls._get_component_class_from_type_string(handle.component_type)
        component_class.type = handle.component_type  # TODO discuss if we do that in the code gen instead
        return component_class(handle, **kwargs)
