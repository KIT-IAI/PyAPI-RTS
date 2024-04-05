# LGPL-3.0 License
# Copyright (c) 2023 KIT-IAI-ESA

from datetime import date, datetime
from enum import Enum
import os
from pathlib import Path
import pathlib

import networkx as nx
from pyapi_rts.api.internals.blockreader import BlockReader
from pyapi_rts.api.lark.rlc_tline import RLCTLine

from pyapi_rts.api.lark.tli_transformer import TliFile
from pyapi_rts.api.component import Component
from pyapi_rts.api.component_box import ComponentBox, add_xrack_connections
from pyapi_rts.api.subsystem import Subsystem


class CompileMode(Enum):
    AUTO = "AUTO"
    PRIORITY = "PRIORITY"


class RealTime(Enum):
    Yes = "Yes"
    No = "No"


class RackType(Enum):
    NONE = -1
    GTWIF_UNUSED = 0
    GTWIF_GPC = 2
    GTWIF_PB = 3
    NOVACOR = 4


class Draft:
    """RSCAD Draft, containing multiple subsystems."""

    def __init__(
        self,
        version: str = "1.2",
        title: str = "Test Circuit",
        author_created: str = "pyapi_rts",
        author_changed: str = "pyapi_rts",
        date_created: date = date.today(),
        date_changed: date = date.today(),
        time_step_us: float = 50.0,
        realtime: RealTime = RealTime.Yes,
        non_rt_computation_us: int = 150,
        compile_mode: CompileMode = CompileMode.AUTO,
        show_feedback_warnings: bool = False,
        circuit_comments: list[str] | None = None,
        finish_time: float = 0.2,
        rack_number: int = 1,
        canvas_width: int = 1500,
        canvas_height: int = 850,
        subsys_index: int = 0,
        view_mode: int = 3,
        zoom: int = 100,
        top_left_point: tuple[int, int] = (0, 0),
    ) -> None:
        self.path: str = ""
        """The path of the dfx file."""
        self.version = version
        self.title = title
        self.author_created = author_created
        self.author_changed = author_changed
        self.date_created = date_created
        self.date_changed = date_changed
        self.time_step_us = time_step_us
        self.realtime = realtime
        self.non_rt_computation_us = non_rt_computation_us
        self.compile_mode = compile_mode
        self.show_feedback_warnings = show_feedback_warnings
        if circuit_comments is None:
            self.circuit_comments = []
        else:
            self.circuit_comments = circuit_comments
        self.finish_time = finish_time
        self.rack_number = rack_number
        self.canvas_width = canvas_width
        self.canvas_height = canvas_height
        self.subsys_index = subsys_index
        self.view_mode = view_mode
        self.zoom = zoom
        self.top_left_point = top_left_point
        self._subsystems: list[Subsystem] = []
        self._component_enumeration: list[str] = []
        self.rack_types: list[RackType] = []

    @classmethod
    def from_file(cls, path: str) -> "Draft":
        draft = cls()
        draft.read_file(path)
        return draft

    def add_subsystem(self, subsystem: Subsystem) -> None:
        """
        Adds a subsystem to the draft

        :param subsystem: Subsystem to add
        :type subsystem: Subsystem
        """
        self._subsystems.append(subsystem)

    @property
    def subsystems(self) -> list[Subsystem]:
        """
        Returns all subsystems in the draft

        :return: list of subsystems
        :rtype: list[Subsystem]
        """
        return self._subsystems

    def read_file(self, path: str) -> None:
        """Read a .dfx file from the path and fill the object with the data.

        :param path: Path to the .dfx file
        :type path: str
        """
        self._subsystems = []
        with open(path, "r", encoding="cp1252") as draft_in:
            reader = BlockReader(draft_in.readlines())
        self.version = reader.source[0].split("DRAFT ")[-1].strip()
        self._read_header(reader)
        self._read_subsystems(reader)

        self.path = path

    def write_file(self, path: str = "") -> None:
        """Write the object to a .dfx file

        :param path: Path to the .dfx file
        :type path: str
        """
        if isinstance(path, Path):
            path = str(path)

        if len(path) == 0 or path.isspace():
            path = self.path

        with open(path, "w", encoding="cp1252") as out:
            out.writelines("\n".join(self._lines()))

    @property
    def _header(self) -> list[str]:
        graphics = [
            "GRAPHICS: ",
            f"    CANVAS_WIDTH: {self.canvas_width}",
            f"    CANVAS_HEIGHT: {self.canvas_height}",
            f"    CURRENT_SUBSYSTEM_IDX: {self.subsys_index}",
            f"    DEFAULT_VIEW_MODE: {self.view_mode}",
            f"    DEFAULT_ZOOM: {self.zoom}",
            f"    DEFAULT_TOP_LEFT_POINT: {self.top_left_point[0]},{self.top_left_point[1]}",
        ]

        if self.realtime == RealTime.Yes:
            real_time = self.realtime.value
        else:
            real_time = f"{self.realtime.value} {self.non_rt_computation_us}"

        if self.compile_mode == CompileMode.AUTO and self.show_feedback_warnings:
            compile_mode = f"{self.compile_mode.value}    SHOW-FEEDBACK-WARNINGS"
        else:
            compile_mode = self.compile_mode.value

        data = [
            "DATA: ",
            f"    TITLE: {self.title}",
            f"    CREATED: {self.date_created.strftime('%b %d, %Y')} ({self.author_created})",
            f"    LAST-MODIFIED: {self.date_changed.strftime('%b %d, %Y')} ({self.author_changed})",
            f"    TIME-STEP: {self.time_step_us / (10**6)}",
            f"    FINISH-TIME: {self.finish_time}",
            f"    RTDS-RACK: {self.rack_number}",
            f"    COMPILE-MODE: {compile_mode}",
            "    DISTRIBUTION_MODE: 0",
            f"    RTDS REAL-TIME: {real_time}",
        ]

        comments = ["    CIRCUIT_COMMENTS: "]
        if len(self.circuit_comments) > 0:
            comments[0] += self.circuit_comments[0]
        if len(self.circuit_comments) > 1:
            comments += self.circuit_comments[1:]
        comments += ["END_CIRCUIT_COMMENTS:"]

        component_enumeration = ["COMPONENT_ENUMERATION_START:"]
        component_enumeration += self._component_enumeration
        component_enumeration += ["COMPONENT_ENUMERATION_END:"]

        return graphics + data + comments + component_enumeration

    def _lines(self) -> list[str]:
        """
        Convert the object to a list of lines

        :return: Content of a .dfx file
        :rtype: list[str]
        """
        lines = []
        lines.append(f"DRAFT {self.version}")
        lines += self._header
        for subsys in self._subsystems:
            lines += subsys.block()
        lines.append("")
        return lines

    def _read_header(self, reader: BlockReader) -> None:
        """Parse the header of the .dfx file

        :param reader: BlockReader object
        :type reader: BlockReader
        """
        graphics = reader.current_block.lines
        self.canvas_width = int(graphics[0].split(": ")[-1].strip())
        self.canvas_height = int(graphics[1].split(": ")[-1].strip())
        self.subsys_index = int(graphics[2].split(": ")[-1].strip())
        self.view_mode = int(graphics[3].split(": ")[-1].strip())
        self.zoom = int(graphics[4].split(": ")[-1].strip())
        x, y = graphics[5].split(": ")[-1].strip().split(",")
        self.top_left_point = (int(x), int(y))

        reader.next_block()
        data = reader.current_block.lines
        self.title = ": ".join(data[0].split(": ")[1:])
        self.date_created, self.author_created = self._read_date_author(data[1])
        self.date_changed, self.author_changed = self._read_date_author(data[2])
        self.time_step_us = float(data[3].split(": ")[-1]) * 10**6
        self.finish_time = float(data[4].split(": ")[-1])
        self.rack_number = int(data[5].split(": ")[-1])
        compile_mode = data[6].split(": ")[-1].split("    ")
        self.compile_mode = CompileMode[compile_mode[0]]
        self.show_feedback_warnings = len(compile_mode) > 1
        realtime = data[8].split(": ")[-1].split(" ")
        self.realtime = RealTime[realtime[0]]
        if len(realtime) > 1 and realtime[1] != "":
            self.non_rt_computation_us = int(realtime[1])

        comments = []
        if len(data) > 9 and "CIRCUIT_COMMENTS" in data[9]:
            comments.append(": ".join(data[9].split(": ")[1:]))

            line_index = 0
            for i, line in enumerate(reader.source):
                if "CIRCUIT_COMMENTS" in line:
                    line_index = i + 1
                    break

            while "END_CIRCUIT_COMMENTS:" not in reader.source[line_index]:
                comments.append(reader.source[line_index].strip())
                line_index += 1

        self.circuit_comments = comments
        reader.next_block()
        self._component_enumeration = [l.strip() for l in reader.current_block.lines]

    def _read_date_author(self, line: str) -> tuple[date, str]:
        created_str = ": ".join(line.split(": ")[1:])
        date_str, author = created_str.split(" (")
        result_date = datetime.strptime(date_str, "%b %d, %Y").date()
        return result_date, author[:-1]

    def _read_subsystems(self, reader: BlockReader) -> None:
        """Parse the subsystems from the .dfx file

        :param reader: BlockReader object
        :type reader: BlockReader
        """
        number = 1
        while True:
            if Subsystem.check_title(reader.current_block.title):
                self._subsystems.append(Subsystem(self, number=number))
                self._subsystems[-1].read_block(reader.current_block)
                number += 1
            if not reader.next_block():
                break

    def get_components(
        self, recursive: bool = True, clone: bool = True, with_groups: bool = False
    ) -> list[Component]:
        """
        Returns all components in the draft

        :param recursive: Include components from nested boxes, defaults to True
        :type recursive: bool, optional
        :return: list of components
        :rtype: list[Component]
        """
        return [
            comp
            for sub in self._subsystems
            for comp in sub.get_components(recursive, clone, with_groups)
        ]

    def get_components_by_type(
        self, type_name: str, recursive: bool = True, clone: bool = True, with_groups: bool = False
    ) -> list[Component]:
        """
        Returns all components of a given type in the draft

        :param type_name: Name of the component type
        :type type_name: str
        :param recursive: Recursive search, defaults to True
        :type recursive: bool, optional
        :return: list of components
        :rtype: list[Component]
        """
        return list(
            filter(
                (lambda c: c.type == type_name),
                self.get_components(recursive, clone, with_groups),
            )
        )

    def get_by_id(self, cid: str) -> Component | None:
        """
        Get a component from the draft by its id

        :param cid: Component UUID to search for
        :type cid: str
        :return: Component if it is found, else None
        :rtype: Component | None
        """

        for subsystem in self.subsystems:
            comp = subsystem.get_by_id(cid, True, True)
            if comp is not None:
                return comp
        return None

    def search_by_name(
        self, name: str, recursive: bool = False, case_sensitive: bool = False
    ) -> dict[str, list[Component]]:
        """
        Search for components by name

        :param name: Name to search for
        :type name: str
        :param recursive: Recursive search, defaults to False
        :type recursive: bool, optional
        :param case_sensitive: Case sensitive search, defaults to False
        :type case_sensitive: bool, optional
        :return: A mapping from the subsystem name to the list of found components
        :rtype: dict[str, list[Component]]
        """
        return dict(
            map(
                (
                    lambda s: (
                        s.tab_name,
                        s.search_by_name(name, recursive, case_sensitive),
                    )
                ),
                self.subsystems,
            )
        )

    def add_component(self, component: Component, box_id: str) -> bool:
        """
        Adds a component to the ComponentBox with the specified UUID/Index.

        :param component: Component to add to the draft.
        :type component: Component
        :param subsystem_id: The UUID or Subsystem index of the Component Box to add the component to.
        :type subsystem_id: str
        :return: Boolean success
        :rtype: bool
        """

        for subsystem in self.subsystems:
            if subsystem.index == box_id:
                return subsystem.add_component(component)
        component_box = self.get_by_id(box_id)
        if component_box is None or not isinstance(component_box, ComponentBox):
            return False
        return component_box.add_component(component)

    def remove_component(self, cid: str) -> bool:
        """
        Removes a component from the draft if it exists.

        :param cid: The UUID of the component to be removed.
        :type cid: str
        :return: Boolean success
        :rtype: bool
        """

        for subsystem in self.subsystems:
            if subsystem.remove_component(cid, True, True):
                return True
        return False

    def modify_component(self, component: Component) -> bool:
        """
        Modifies a component in the draft if it exists.

        :param component: The component to be modified.
        :type component: Component
        :return: Boolean success
        :rtype: bool
        """

        for subsystem in self.subsystems:
            if subsystem.modify_component(component, recursive=True):
                return True
        return False

    def get_draft_vars(self) -> dict[str, Component]:
        """Get a dictionary with all draft variables in the draft with names as key.

        :return: Dictionary of draft variables.
        :rtype: dict[str, Component]
        """
        draft_vars = {}

        for subsys in self._subsystems:
            draft_vars |= subsys.get_draft_vars(recursive=True)

        return draft_vars

    def get_connection_graph(self) -> nx.Graph:
        """
        Returns the combined connection graph from the subsystems.

        :return: Combined connection graph
        :rtype: Graph
        """

        graph = nx.Graph()
        for subsystem in self.subsystems:
            graph = nx.compose(graph, subsystem.get_connection_graph())
        return graph

    def generate_full_graph(self) -> nx.Graph:
        graph = nx.Graph()
        xrack = {}

        if len(self.subsystems) == 0:
            return graph

        for subsys in self.subsystems:
            sgraph, sxrack = subsys.generate_full_graph()
            graph = nx.compose(graph, sgraph)

            for key, value in sxrack.items():
                if xrack.get(key) is None:
                    xrack[key] = value
                else:
                    xrack[key] += value
        add_xrack_connections(xrack, graph, mark_xrack=True)

        return graph

    def get_tline_constants(self, name: str) -> TliFile | None:
        """
        Search and returns the TLI file with the specified name.

        :param name: Name of the TLine Constants file.
        :type name: str
        :return: Tli file data as dicitonaries. None if not found.
        :rtype: TliFile | None
        """
        name = name.split(".tli")[0]
        for file in list(os.scandir(Path(self.path).parent)):
            if name in file.name:
                tli_file = TliFile()
                tli_file.read_file(file.path)
                return tli_file
        return None  # File not found

    def get_rlc_tline(self, name: str) -> RLCTLine | None:
        """
        Returns the TLine Constants file as a RLC Tline.

        :param name: Name of the TLine file.
        :type name: str
        :returns: RLC TLine
        :rtype: RLCTLine
        """
        tli_file = self.get_tline_constants(name)
        if tli_file is None:
            return None
        return RLCTLine(name, tli_file)

    def get_rack_type(self) -> int:
        """
        Returns the rack type.

        :return: Rack type
        :rtype: int
        """

        rack_type_mapping = {
            "GTWIF": RackType.GTWIF_UNUSED,
            "GPC": RackType.GTWIF_GPC,
            "PB5": RackType.GTWIF_PB,
            "NOVACOR": RackType.NOVACOR,
        }

        if self.rack_types is None or len(self.rack_types) == 0:
            # Try to find config file
            path = pathlib.Path(__file__).parent.parent / "rack_config.txt"
            if path.exists():
                with path.open() as f:
                    lines = f.readlines()
                    self.rack_types = []
                    for line in lines:
                        if line.strip().startswith("CARD_TYPE = "):
                            _type = line.split(" = ")[1].strip()
                            if _type in rack_type_mapping:
                                # Other cases (GPC and PB5)
                                if _type == "GPC":
                                    if len(self.rack_types) > 0 and self.rack_types[-1] in [
                                        RackType.GTWIF_GPC,
                                        RackType.GTWIF_UNUSED,
                                        RackType.GTWIF_PB,
                                    ]:
                                        self.rack_types.pop()
                                elif (
                                    _type == "PB5"
                                    and len(self.rack_types) > 0
                                    and self.rack_types[-1]
                                    in (RackType.GTWIF_UNUSED, RackType.GTWIF_PB)
                                ):
                                    self.rack_types.pop()
                                self.rack_types.append(rack_type_mapping[_type])
                            else:
                                self.rack_types.append(RackType.NONE)

        return self.rack_types[self.rack_number].value
