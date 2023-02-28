# LGPL-3.0 License
# Copyright (c) 2023 KIT-IAI-ESA

from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor
import copy
import getopt
import hashlib
import os
import pathlib
import shutil
import sys
import time
from typing import Any

from progress.bar import Bar

from pyapi_rts.class_extractor import EnumHashPool
from pyapi_rts.class_extractor.readers.blocks import ComponentDefFile, GraphicsBlock
from pyapi_rts.class_extractor.extracted import (
    ExtComponent,
    ExtEnumParameter,
    ExtParameter,
    ExtParameterColl,
    ExtRectangle,
)
from pyapi_rts.class_extractor.generators import (
    ClassLoaderGenerator,
    ComponentGenerator,
    EnumGenerator,
    GraphicsMacroGenerator,
    ParameterCollectionGenerator,
)
from pyapi_rts.class_extractor.utils import valid_file_name
from pyapi_rts.shared import BoundingBox, Stretchable
from pyapi_rts.shared.condition_tree import BBNode
from pyapi_rts.class_extractor.hooks import __all__ as hook_names


PATH = pathlib.Path(__file__).parent.resolve()


def reverse_dictionary(dictionary: dict[Any, list[Any]]) -> dict:
    """
    Reverses a dictionary with multiple entries per key.

    :param dictionary: Dictionary to reverse.
    :type dictionary: dict[Any, list[Any]]
    :return: Reversed dictionary.
    :rtype: dict
    """
    reverse_dict = defaultdict(list)
    for key, value in dictionary.items():
        for v in value:
            reverse_dict[v].append(key)

    return reverse_dict


def read_component_tags(path: str) -> dict[str, list[str]]:
    """
    Reads the component tags from a file.

    :param path: Path to the file.
    :type path: str
    :return: Dictionary with component tags (Component Type Name -> Tag list).
    :rtype: dict[str, list[str]]
    """
    component_tags: dict[str, list[str]] = {}
    tag = ""
    comp_list = []
    with open(path, "r") as f:
        lines = f.readlines()
        for line in lines:
            if line.lstrip() == line:
                if len(tag.strip()) > 0:
                    component_tags[tag] = copy.deepcopy(comp_list)
                tag = line.rstrip()
                comp_list = []
            else:
                comp_list.append(line.strip())
            if tag != "" and len(comp_list) > 0:
                component_tags[tag] = comp_list
    return reverse_dictionary(component_tags)


def read_file(
    file_path: str, tag_dict: dict[str, list[str]]
) -> tuple[ExtComponent, list[ExtEnumParameter]]:
    """
    Reads a component definition file.

    :param path: Path to a component definition file.
    :type path: str
    :param tag_dict: Dictionary with component tags (read_component_tags()).
    :type tag_dict: dict[str, list[str]]
    :return: The component and the list of enum parameters.(None, []) if the file could not be read.
    :rtype: tuple[ExtComponent, list[ExtEnumParameter]]
    """
    cdf = ComponentDefFile()
    print(file_path)

    if not cdf.read_from_file(file_path):
        return (None, [])

    _list: list[ExtParameterColl] = []
    _param_list: list[ExtParameter] = []
    _enum_list: list[ExtEnumParameter] = []
    _rectangle: ExtRectangle = None

    component = ExtComponent()
    component.set_type(file_path.name)
    component.apply_tag_dict(tag_dict)

    # ParameterCollections / Sections
    for section in cdf.blocks[0].results["section"]:
        _list.append(ExtParameterColl(valid_file_name(section.name)))
        for comp in section.comps:
            parameter, enum = comp.as_ext_parameter()
            _list[-1].parameters.append(parameter)
            if not enum is None:
                parameter.set_type(enum.enum_type)
                _enum_list.append(enum)

    # Parameters
    for comp in cdf.blocks[0].results["parameter"]:
        parameter, enum = comp.as_ext_parameter()
        _param_list.append(parameter)
        if not enum is None:
            _enum_list.append(enum)

    hidden_params = next(
        filter(
            (lambda c: c.name.upper() == "HIDDEN PARAMETERS"),
            cdf.blocks[0].blocks[0].results["section"],
        ),
        None,
    )
    _rectangle = ExtRectangle()
    if len(cdf.blocks[1].results["nodes"]) > 0 or hidden_params is not None:
        x1_param, y1_param, x2_param, y2_param = None, None, None, None
        if hidden_params is not None:
            x1_param = next(
                filter((lambda p: p.key == "x1"), hidden_params.comps), None
            )
            y1_param = next(
                filter((lambda p: p.key == "y1"), hidden_params.comps), None
            )
            x2_param = next(
                filter((lambda p: p.key == "x2"), hidden_params.comps), None
            )
            y2_param = next(
                filter((lambda p: p.key == "y2"), hidden_params.comps), None
            )

        if (
            x1_param is not None
            and y1_param is not None
            and x2_param is not None
            and y2_param is not None
        ):
            bbnode = BBNode()
            bbnode.bboxes.append(BoundingBox("$x1", "$y1", "$x2", "$y2"))
            _rectangle.graphics = [bbnode]

    if len(cdf.blocks[1].results["nodes"]) == 1:
        _rectangle.connection_points = cdf.blocks[1].results["nodes"][0]

    if len(cdf.blocks[3].results["bbox"]) == 1 and _rectangle.graphics is None:
        _rectangle.graphics = cdf.blocks[3].results["bbox"][0]

    stretchable = cdf.blocks[2].results["stretchable"]
    _rectangle.stretchable = stretchable[0] if len(stretchable) > 0 else Stretchable.NO
    if len(cdf.blocks[2].results["name"]) > 0:
        component.name_parameter_key = cdf.blocks[2].results["name"][0]
    if len(cdf.blocks[2].results["linked"]) > 0:
        _rectangle.linked = True

    # Computations
    component.computations = cdf.blocks[4].results["computations"]

    component.collections = _list
    component.collections.sort(key=lambda c: c.name)
    component.parameters = _param_list
    component.parameters.sort(key=lambda p: p.name)
    if _rectangle is not None:
        component.rectangle = _rectangle
    _enum_list.sort(key=lambda x: x.enum_type)
    return (component, _enum_list)


def read_graphics_files(paths):
    bboxes = {}
    for p in paths:
        print(p)
        lines = []
        with open(p, "r", encoding="cp1252") as file_stream:
            lines = file_stream.readlines()
        graphics_block = GraphicsBlock(incl_macros=False)
        graphics_block.read(lines)
        bboxes[p.stem] = graphics_block.results["bbox"][0][0]

    generator = GraphicsMacroGenerator(bboxes)
    lines = generator.read_file(PATH / "templates/graphics_macros.py.txt")
    lines = generator.replace(lines)
    generator.write_file(
        PATH / ("../generated/graphics_macros.py"),
        lines,
    )


def read_component_dir(
    dir_path: str,
    tag_dict: dict[str, list[str]],
    include_obsolete: bool = False,
    worker_count: int = 8,
) -> list[tuple[ExtComponent, list[ExtEnumParameter]]]:
    """
    Reads the contents of a directory.

    :param path: The path to the directory.
    :type path: str
    :param tag_dict: Dictionary with component tags (read_component_tags()).
    :type tag_dict: dict[str, list[str]]
    :param include_obsolete: Include obsolete components.
    :type include_obsolete: bool
    :param worker_count: The number of workers/threads to use.
    :type worker_count: int
    :return: list of components and their enum parameter types.
    :rtype: list[tuple[ExtComponent, list[ExtEnumParameter]]]
    """
    read_list: tuple[ExtComponent, list[ExtEnumParameter]] = []
    read_paths = []

    # Load all subfolders
    component_dir = list(
        map(
            (lambda e: pathlib.Path(e[0])),
            os.walk(dir_path, topdown=False, onerror=None, followlinks=False),
        )
    )
    component_dir.sort()
    # component_dir = component_dir[1:]
    # Load all files
    next_index = 0
    hash_input = hashlib.new("sha256")
    for subdir in filter(
        lambda f: True if include_obsolete else (not "OBSOLETE" in f.parts),
        component_dir,
    ):
        paths = list(os.scandir(str(subdir)))
        paths = list(
            filter(
                (lambda p: not p.path.endswith((".jpg", ".JPG")) and p.is_file()),
                paths,
            )
        )
        with Bar("Folder progress", max=len(paths)) as prog_bar:
            for param in paths:
                with open(param.path, "r", encoding="cp1252") as file_stream:
                    lines_out = file_stream.readlines()
                    hash_input.update(str.encode("\n".join(lines_out)))
                read_paths.append(pathlib.Path(param.path))
                prog_bar.next()
        print(
            "Read folder number "
            + str(next_index)
            + ": "
            + (str(paths[0].path) if paths != [] else "None")
        )
        next_index += 1

    print("Hash over read Component Builder files: ", hash_input.hexdigest())

    read_graphics_files(filter(lambda path: path.suffix == ".g", read_paths))

    # Create threads
    with ThreadPoolExecutor(max_workers=worker_count) as executor:
        read_list = executor.map((lambda path: read_file(path, tag_dict)), read_paths)

    read_list = list(read_list)
    read_list = list(filter((lambda x: x[0] is not None), read_list))
    return read_list


if __name__ == "__main__":

    WORKER_COUNT = 8

    # Load arguments
    time_start = time.perf_counter()
    DELETE = False
    path = PATH / "COMPONENTS"
    INCLUDE_OBSOLETE = False

    try:
        opts, args = getopt.getopt(
            sys.argv[1:],
            "hp:dot:",
            ["help", "path=", "delete", "includeobsolete", "threads="],
        )
    except getopt.GetoptError as err:
        print(err)
        sys.exit(2)
    for opt, arg in opts:
        if opt in ("-h", "--help"):
            print(
                "Usage: python3 main.py [--path=<path>] [--delete] [--includeobsolete] [--threads=<count>]"
            )
            sys.exit()
        elif opt in ("-p", "--path"):
            path = arg
        elif opt in ("-d", "--delete"):
            DELETE = True
        elif opt in ("-o", "--includeobsolete"):
            INCLUDE_OBSOLETE = True
        elif opt in ("-t", "--threads"):
            WORKER_COUNT = int(arg)
        else:
            assert False, "unhandled option"

    tag_dict = read_component_tags(PATH / "component_tags.txt")
    read = read_component_dir(path, tag_dict, INCLUDE_OBSOLETE, WORKER_COUNT)
    TOTAL = 0

    # enumHashPool: dict[int, ExtEnumParameter] = enum_hash_pool_from_file(
    # PATH / "enum_pool.txt"
    # )

    hash_pool = EnumHashPool()
    hash_pool.load_from_file(PATH / "enum_pool.txt")

    file_hash = hashlib.new("sha256")

    # Delete 'generated' folder if specified by user
    if DELETE:
        shutil.rmtree(PATH / "../generated")
        os.mkdir(PATH / "../generated")

    read.sort(key=lambda x: x[0].type.lower())
    with Bar("Generating", max=TOTAL) as bar:
        TOTAL_TIME = 0
        for c, enum_list in read:
            for enum_entry in enum_list:
                hash_pool.add(c, enum_entry)

            bar.next()
            c.parameters.sort(key=lambda p: p.name)
            cg = ComponentGenerator(c)
            lines = cg.read_file(PATH / "templates/{{TypeName}}.py.txt")
            lines = cg.replace(lines)
            lines_combined = lines[:]
            bar.next()

            c.collections.sort(key=lambda c: c.name)
            for coll in c.collections:
                coll.parameters.sort(key=lambda p: p.name)
                collgen = ParameterCollectionGenerator(coll)
                lines = collgen.read_file(PATH / "templates/{{name}}.py.txt")
                lines = collgen.replace(lines)
                lines_combined += ["#-------------------------"] + lines[1:]
                bar.next()
            file_hash.update(
                cg.write_file(
                    PATH / ("../generated/" + lines_combined[0]),
                    lines_combined,
                )
            )
    print(f"{len(read)} Component classes generated")

    enum_list = list(hash_pool.pool.values())
    enum_list.sort(key=lambda x: x.enum_type)
    for enum_entry in enum_list:
        eg = EnumGenerator(enum_entry)
        lines = eg.read_file(PATH / "templates/{{name}}EnumParameter.py.txt")
        lines = eg.replace(lines)
        file_hash.update(
            eg.write_file(PATH / ("../generated/enums/" + lines[0]), lines[1:])
        )
        bar.next()
    print(f"{len(hash_pool.pool.values())} Enums generated")

    clg = ClassLoaderGenerator(list(map((lambda c: c[0]), read)), hook_names)
    lines = clg.read_file(PATH / "templates/class_loader.py.txt")
    lines = clg.replace(lines)
    file_hash.update(clg.write_file(PATH / ("../generated/" + lines[0]), lines[1:]))
    print("class_loader.py generated")

    # Copy hook files
    try:
        shutil.rmtree(PATH / "../generated/hooks")
    except NotADirectoryError:
        pass
    except FileNotFoundError:
        pass
    try:
        os.mkdir(PATH / "../generated/hooks")
    except FileExistsError:
        pass
    for hook in hook_names:
        shutil.copy(
            PATH / "hooks" / (hook + ".py"),
            PATH / "../generated/hooks" / (hook + ".py"),
        )

    print("Hash of generated files: ", file_hash.hexdigest())
    print(
        "Total time: "
        + str(time.perf_counter() - time_start)
        + f" with {WORKER_COUNT} threads"
    )
