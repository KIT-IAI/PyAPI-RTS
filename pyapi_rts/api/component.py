# LGPL-3.0 License
# Copyright (c) 2023 KIT-IAI-ESA

from abc import abstractmethod
from enum import Enum
from typing import Any, Callable
import copy
import itertools
import re
import uuid

from pyapi_rts.api.parameters import Parameter, ConnectionPoint, ParameterCollection
from pyapi_rts.shared import Stretchable, NodeIO
from pyapi_rts.shared.parameter_condition import get_enum_index

from .enumeration import Enumeration
from .internals.dfxblock import DfxBlock
from .internals.parameters_block import ParametersBlock
from .internals.block import Block
from .internals.hooks import hooks


class Component(DfxBlock):
    """
    A RSCAD component
    """

    _title_regex = re.compile(r"^COMPONENT_TYPE=(.+)\s?\n?$")

    _COMPONENT_TYPE_NAME = ""
    GRID_SIZE = 32
    LOAD_UNIT_NAMES = ["loadunit", "LoadUnit", "load"]
    LOAD_UNITS_DEFAULT = 10

    def __init__(
        self,
        type_name: str = None,
        stretchable: Stretchable = Stretchable.NO,
        linked: bool = None,
    ) -> None:
        from pyapi_rts.api.component_box import ComponentBox

        super().__init__()
        self.__id: str = uuid.uuid4().__str__()
        self._type: str = "" if type_name is None else type_name
        self._coord_x: int = 144
        self._coord_y: int = 144
        self._rotation: int = 0
        self._mirror: int = 0
        self._number: int = 0
        self._params: list[str] = []
        self._parameters_block: ParametersBlock = ParametersBlock()
        self._name_parameter_key: str = None
        self.enumeration: Enumeration = Enumeration()
        self._is_connecting = False
        self._is_hierarchy_connecting = False
        self._is_label = False
        #: The component that contains this component.
        self.parent: ComponentBox = None

        #: Stretchable dimensions of the component
        self.stretchable: Stretchable = stretchable

        # The name links the component to others of its type.
        self.linked: bool = linked

        self._parameters: dict[str, Parameter] = {}
        self._computations: dict[str, Callable] = {}
        self._collections: list[ParameterCollection] = []

    @property
    def uuid(self) -> str:
        """
        Returns the component uuid

        :return: The component UUID
        :rtype: str
        """
        return self.__id

    @property
    def name(self) -> str:
        """
        The parameter with key 'Name' with the enumerator applied
        """
        if self.has_key("Name"):
            return self.enumeration.apply(self.get_by_key("Name"))
        elif self._name_parameter_key is not None and self.has_key(
            self._name_parameter_key
        ):
            return self.enumeration.apply(self.get_by_key(self._name_parameter_key))
        else:
            return self.type

    @property
    def bounding_box(self) -> tuple[int, int, int, int]:
        return self.bounding_box_from_dict(self.as_dict())

    @property
    def bounding_box_abs(self) -> tuple[int, int, int, int]:
        return self.bounding_box_from_dict(self.as_dict(), absolute=True)

    def bounding_box_from_dict(
        self, dictionary: dict, absolute: bool = False
    ) -> tuple[int, int, int, int]:
        return (0, 0, 0, 0)

    @property
    def x1(self) -> int:
        return self.bounding_box[0]

    @property
    def y1(self) -> int:
        return self.bounding_box[1]

    @property
    def x2(self) -> int:
        return self.bounding_box[2]

    @property
    def y2(self) -> int:
        return self.bounding_box[3]

    @property
    def width(self) -> int:
        return self.bounding_box[2] - self.bounding_box[0]

    @property
    def height(self) -> int:
        return self.bounding_box[3] - self.bounding_box[1]

    def read_block(self, block: Block, check=True):
        """
        Reads a component from a list of lines

        :param block: A list of lines describing the component
        :type block: Block
        :param check: Checks the block format before parsing, defaults to True
        :type check: bool, optional
        """
        if check:
            super().read_block(block)
        if len(block.lines) == 0:
            return
        position = block.lines[0].split(" ")
        self._type = block.title.split("COMPONENT_TYPE=")[-1].strip()
        self._coord_x = int(position[0])
        self._coord_y = int(position[1])
        self._rotation = int(position[2])
        self._mirror = int(position[3])
        self._number = int(position[4])
        if block.reader.current_block is not None:
            while True:
                # Found "PARAMETER-START-END" block
                if ParametersBlock.check_title(block.reader.current_block.title):
                    self._parameters_block.read_block(block.reader.current_block)
                elif Enumeration.check_title(block.reader.current_block.title):
                    self.enumeration.read_block(
                        block.reader.current_block,
                        self._parameters_block._parameters.get("Name") or "",
                    )
                else:
                    pass  # Block not recognized, can be ignored
                if not block.reader.next_block():
                    break

        # Put parameters in their corresponding Parameter objects in component
        self._read_parameters(self._parameters_block._parameters)

    def block(self) -> list[str]:
        """
        Returns the component as a .dfx block

        :return: The component as a .dfx block
        :rtype: list[str]
        """
        lines = []
        lines.append("COMPONENT_TYPE=" + self.type)
        lines.append(
            f"\t{self._coord_x} {self._coord_y} {self._rotation} {self._mirror} {self._number}"
        )
        lines.append("\tPARAMETERS-START:")
        param_write = self._write_parameters()
        lines += ["\t" + l for l in param_write]
        lines.append("\tPARAMETERS-END:")
        lines = lines + ["\t" + l for l in self.enumeration.block()]
        return lines

    @property
    def type(self) -> str:
        """
        The component type

        :return: The component type
        :rtype: str
        """
        return self._type

    @property
    def x(self) -> int:
        """
        The x coordinate of the component

        :return: The x coordinate of the component
        :rtype: int
        """
        return self._coord_x

    @x.setter
    def x(self, x):
        if x % Component.GRID_SIZE != Component.GRID_SIZE / 2:
            raise ValueError(
                f"Coordinates need to be aligned on the grid: {Component.GRID_SIZE / 2} + n * {Component.GRID_SIZE}"
            )
        self._coord_x = x

    @property
    def y(self) -> int:
        """
        The y coordinate of the component

        :return: The y coordinate of the component
        :rtype: int
        """
        return self._coord_y

    @y.setter
    def y(self, y):
        if y % Component.GRID_SIZE != Component.GRID_SIZE / 2:
            raise ValueError(
                f"Coordinates need to be aligned on the grid: {Component.GRID_SIZE / 2} + n * {Component.GRID_SIZE}"
            )
        self._coord_y = y

    @property
    def rotation(self) -> int:
        """
        The rotation of the component

        :return: The rotation of the component (times 90 degrees)
        :rtype: int
        """
        return self._rotation

    @rotation.setter
    def rotation(self, rotation: int):
        """
        Sets the rotation of the component

        :param rotation: The new rotation
        :type rotation: int
        """
        self._rotation = rotation % 4

    @property
    def mirror(self) -> int:
        """
        The mirror state of the component

        :return: The mirror of the component (0: no mirror, 1: mirror)
        :rtype: int
        """
        return self._mirror

    @mirror.setter
    def mirror(self, mirror: int):
        """
        Sets the mirror state of the component

        :param mirror: The new mirror state
        :type mirror: int
        """
        self._mirror = mirror % 2

    @property
    def is_connecting(self) -> bool:
        """
        Whether the component is a connecting component like wire or bus

        :return: Whether the component is connecting
        :rtype: bool
        """
        return self._is_connecting

    @property
    def is_hierarchy_connecting(self) -> bool:
        """
        Whether the component is a connecting hierarchies without being a component box.

        :return: Whether the component is hierarchy connecting
        :rtype: bool
        """
        return self._is_hierarchy_connecting

    @property
    def is_label(self) -> bool:
        """
        Whether the component is a label

        :return: Whether the component is a label
        :rtype: bool
        """
        return self._is_label

    def get_special_value(self, key: str) -> str:
        """
        Returns the special value of the component.
        :param key: The key of the special value.
        :type key: str
        :return: The special value or empty string if not found.
        :rtype: str
        """
        if key.strip().lower() == "getboxparenttype()":
            return self.parent.get_box_type()
        if key.strip().lower() == "getracktype()":
            return self.parent.get_rack_type()
        if "." in key:
            # Reference to values of node
            return 1.0  # TODO: Return actual value

        for hook in hooks:
            value = hook.special_value(self, key)
            if value is not None:
                return value
        return 0.0

    @property
    def connection_points(self) -> dict[str, ConnectionPoint]:
        return self.connection_points_from_dict(self.as_dict())

    def connection_points_from_dict(self, dictionary) -> dict[str, ConnectionPoint]:
        return {}

    def get_connected_at_point(
        self,
        point_name: str,
        return_connecting: bool = False,
        component_type: str = None,
    ) -> list["Component"]:
        """
        Returns a list of all components connected at the connection point with the given name.
        Filters for components of a given type if component_type is specified.

        :param point_name: Name of the connection point
        :type point_name: str
        :param return_connecting: Returns the connecting components if True, otherwise only the end components are returned, defaults to False
        :type return_connecting: bool, optional
        :param component_type: The type of components to return, defaults to None
        :type component_type: str, optional
        :return: list of connected components
        :rtype: list[Component]
        """
        if point_name not in self.connection_points.keys() or self.parent is None:
            return []
        return self.parent.get_connected_at_component_point(
            self.uuid, point_name, return_connecting, component_type, []
        )

    def _read_parameters(self, dictionary: dict[str, str]):
        """
        Reads the parameters of the component from a dictionary

        :param dictionary: _description_
        :type dictionary: dict[str, str]
        """
        for key, param in self._parameters.items():
            param.set_str(dictionary.get(key))
        for collection in self._collections:
            collection.read_parameters(dictionary)

    def _write_parameters(self) -> list[str]:
        """
        Writes the parameters to a block of a .dfx file

        :return: A parameter block for a .dfx file.
        :rtype: list[str]
        """
        lines = []

        for key, param in self._parameters.items():
            lines.append(f"{key}\t:{param}")
        for collection in self._collections:
            lines += collection.write_parameters()

        return lines

    @abstractmethod
    def as_dict(self) -> dict[str, Parameter]:
        """
        Returns the parameters of the component as a dictionary

        :return: The parameters of the component as a dictionary
        :rtype: dict[str, Parameter]
        """

    def get_by_key(
        self,
        key: str,
        default: Any = None,
        as_int: bool = False,
        draft_vars: dict[str, "Component"] = None,
    ) -> Any | None:
        """
        Returns the parameter with a certain key

        :param key: The key of the parameter
        :type key: str
        :param default: The default value if the parameter is not found, defaults to None
        :type default: Any, optional
        :param as_int: Return Enum values as their index; ignored for other types.
        :type as_int: bool, optional
        :param draft_vars: A dictionary with draft variables for evaluation; see Draft.get_draft_vars()
        :type draft_vars: dict, optional
        :return: The parameter or the default value if not found
        :rtype: Any | None
        """
        value = None
        if key in self._parameters:
            value = self._parameters[key].value
        elif key in self._computations:
            value = self._computations[key]()
        else:
            for collection in self._collections:
                if collection.has_key(key):
                    value = collection.get_value(key)
                    break
        if value is not None:
            if as_int and isinstance(value, Enum):
                return get_enum_index(value)
            if (
                isinstance(value, str)
                and value.startswith("$")
                and draft_vars is not None
            ):
                return self._eval_draft_var(value, draft_vars)
            return value
        return default

    def _eval_draft_var(self, value: str, draft_vars: dict[str, "Component"]):
        if self.enumeration is None or "#" not in value:
            name = value
        else:
            name = self.enumeration.apply(value)

        draft_var = draft_vars[name[1:]]
        val_type = str(draft_var.Type)
        if val_type == "CHARACTER":
            return str(draft_var.Value.value)
        elif val_type == "REAL":
            return float(draft_var.Value.value)
        return int(draft_var.Value.value)

    def set_by_key(self, key: str, value: Any) -> bool:
        """
        Sets a parameter with a certain key

        :param key: The key of the parameter
        :type key: str
        :param value: The value of the parameter
        :type value: Any
        :return: True if the parameter was set successfully, False otherwise
        :rtype: bool
        """
        if key in self._parameters:
            self._parameters[key].value = value
            return True
        for collection in self._collections:
            if collection.has_key(key):
                collection.set_value(key, value)
                return True
        return False

    def has_key(self, key: str) -> bool:
        """
        Checks if a parameter with a certain key exists

        :param key: The key of the parameter
        :type key: str
        :return: True if the parameter exists, False otherwise
        :rtype: bool
        """
        return (
            key in self._parameters
            or key in self._computations
            or any(c.has_key(key) for c in self._collections)
        )

    def duplicate(self) -> "Component":
        """
        Creates a copy of the component with the same UUID

        :return: The copy of the component
        :rtype: Component
        """
        return copy.deepcopy(self)

    def overlaps(self, other: "Component") -> bool:
        """
        Checks if the rectangles overlap.

        :param other: Another component
        :type other: Component
        :return: True if the rectangles overlap, False otherwise
        :rtype: bool
        """

        bbox_self = list(self.bounding_box)
        bbox_other = list(other.bounding_box)

        bbox_self[0] += self.x
        bbox_self[2] += self.x
        bbox_self[1] += self.y
        bbox_self[3] += self.y

        bbox_other[0] += other.x
        bbox_other[2] += other.x
        bbox_other[1] += other.y
        bbox_other[3] += other.y

        return not (
            bbox_self[2] < bbox_other[0] or bbox_self[0] > bbox_other[2]
        ) and not (bbox_self[3] < bbox_other[1] or bbox_self[1] > bbox_other[3])

    def touches(
        self, comp: "Component"
    ) -> list[tuple[ConnectionPoint, ConnectionPoint]]:
        """
        Returns a list of connection points the two components touch at the same time

        :param comp: The component to check for touching connection points
        :type comp: Component
        :return: A list of connection points the two components touch at the same time
        :rtype: list[tuple[ConnectionPoint, ConnectionPoint]]
        """
        # FIXME: WARNING: THIS DOESN'T WORK!
        result = []
        cross = itertools.product(
            list(self.connection_points.values()),
            list(comp.connection_points.values()),
        )
        for left, right in cross:
            if (
                self.x1.get_value(self.as_dict()) + left.x.get_value()
                == comp.x1.get_value(comp.as_dict()) + right.x.get_value()
                and self.y1.get_value(self.as_dict()) + left.y.get_value()
                == comp.y1.get_value(comp.as_dict()) + right.y.get_value()
            ):
                result.append((left, right))
        return result

    def graph_similar_to(self, comp: "Component") -> bool:
        """
        Checks if the two components are identical for the purposes of the graph reperesentation.
        That is the case if:
        1. They have the same id
        2. They have the same coordinates, mirror and rotation
        3. They have the same rectangle position and size

        :param comp: The component to check for similarity.
        :type comp: Component
        :return: True if the two components are identical (for the graph).
        :rtype: bool
        """

        if self.uuid != comp.uuid:
            return False
        if self.x != comp.x or self.y != comp.y:
            return False
        if self.rotation != comp.rotation or self.mirror != comp.mirror:
            return False
        if self.bounding_box != comp.bounding_box:
            return False
        return True

    @property
    def load_units(self) -> int:
        """
        Returns the load units of the component based on the data available.
        :return: The load units of the component.
        :rtype: int
        """
        for load_unit_name in Component.LOAD_UNIT_NAMES:
            if self.has_key(load_unit_name):
                return (int)(self.__getattribute__(load_unit_name)())
        return Component.LOAD_UNITS_DEFAULT

    def generate_pos_dict(self) -> dict[str, list[tuple]]:
        """
        Creates a dictionary that maps positions to connection points
        Key: "{x-coord},{y-coord}" of connection point
        Value: tuple of name of connection point and id of component

        :return: The created dictionary
        :rtype: dict[str, list[tuple]]
        """

        position_dict = {}
        dictionary = self.as_dict()
        conns = list(self.connection_points_from_dict(dictionary).values())

        # Stretchable UP_DOWN components are things like wires with one stretchable axis
        if self.stretchable == Stretchable.UP_DOWN:
            # There are stretchable components with more than
            # two connection points, but the first two always
            # describe the top and bottom connection points.
            left, right = conns[0], conns[1]
            # use "raw" x and y values because ConnectionPoint.position is already transformed
            # we would need to invert the transformation when adding new ConnectionPoints
            x_s = [
                int(left.x.get_value(dictionary)),
                int(right.x.get_value(dictionary)),
            ]
            y_s = [
                int(left.y.get_value(dictionary)),
                int(right.y.get_value(dictionary)),
            ]
            i = 0
            stretch_cons = []
            # Add new dummy connection points with name scheme "stretch-{i}"
            for x in range(min(x_s), max(x_s) + 1, self.GRID_SIZE):
                for y in range(min(y_s), max(y_s) + 1, self.GRID_SIZE):
                    stretch_cons.append(
                        ConnectionPoint(
                            x, y, "stretch" + str(i), NodeIO.UNDEFINED, self
                        )
                    )
                    i += 1
            if len(stretch_cons) > 0:
                conns += stretch_cons[1:-1]

        elif self.stretchable == Stretchable.BOX:
            # BOXES are things like hierarchy boxes with two stretchable axis
            x_s = range(
                int(self.x1),
                int(self.x2) + 1,
                self.GRID_SIZE,
            )
            y_s = range(
                int(self.y1),
                int(self.y2) + 1,
                self.GRID_SIZE,
            )
            conns = []
            i = 0
            # Add new dummy connection points with name scheme "stretch-{i}"
            for x in [min(x_s), max(x_s)]:  # Top/Bottom line
                for y in y_s:
                    conns.append(
                        # TODO: might need to transform this back to norotation and nomirror
                        ConnectionPoint(
                            x, y, "stretch" + str(i), NodeIO.UNDEFINED, self
                        )
                    )
                    i += 1
            for y in [min(y_s), max(y_s)]:  # Right/Left line
                for x in list(x_s)[1:-1]:
                    conns.append(
                        ConnectionPoint(
                            x, y, "stretch" + str(i), NodeIO.UNDEFINED, self
                        )
                    )
                    i += 1
        for conn in conns:
            pos = conn.position_from_dict(dictionary, absolute=True)
            pos_str = f"{pos[0]},{pos[1]}"
            if pos_str not in position_dict:
                position_dict[pos_str] = [(conn.name, self.uuid)]
            else:
                position_dict[pos_str].append((conn.name, self.uuid))

        return position_dict

    def _calc_bounding_box(self, coordinates: list[tuple]) -> tuple:
        x1 = min(coordinates, key=lambda x: x[0])[0]
        y1 = min(coordinates, key=lambda x: x[1])[1]
        x2 = max(coordinates, key=lambda x: x[2])[2]
        y2 = max(coordinates, key=lambda x: x[3])[3]
        return (x1, y1, x2, y2)
