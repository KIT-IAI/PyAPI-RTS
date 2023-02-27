# LGPL-3.0 License
# Copyright (c) 2023 KIT-IAI-ESA

import re
from typing import Callable, Union

from pyapi_rts.shared import BoundingBox


FONT_SIZE = 10


def line_to_coord(
    groups: tuple, norotate: bool, nomirror: bool
) -> Union[tuple, BoundingBox]:
    all_int = True
    try:
        x1 = int(groups[0])
    except ValueError:
        x1 = str(groups[0])
        all_int = False
    try:
        y1 = int(groups[1])
    except ValueError:
        y1 = str(groups[1])
        all_int = False
    try:
        x2 = int(groups[2])
    except ValueError:
        x2 = str(groups[2])
        all_int = False
    try:
        y2 = int(groups[3])
    except ValueError:
        y2 = str(groups[3])
        all_int = False

    if isinstance(x1, int) and isinstance(x2, int):
        x1, x2 = min(x1, x2), max(x1, x2)
    if isinstance(y1, int) and isinstance(y2, int):
        y1, y2 = min(y1, y2), max(y1, y2)

    if all_int:
        return (x1, y1, x2, y2, norotate, nomirror)
    return BoundingBox(x1, y1, x2, y2, norotate, nomirror)


def text_to_coord(
    groups: tuple, norotate: bool, nomirror: bool
) -> Union[tuple, BoundingBox]:
    try:
        x1 = int(groups[0]) - int(FONT_SIZE / 2)
        x2 = int(groups[0]) + int(FONT_SIZE / 2)
    except ValueError:
        x1 = f"{groups[0]}-{int(FONT_SIZE / 2)}"
        x2 = f"{groups[0]}-{int(FONT_SIZE / 2)}"
    try:
        y1 = int(groups[1]) - int(FONT_SIZE / 2)
        y2 = int(groups[1]) + int(FONT_SIZE / 2)
    except ValueError:
        y1 = f"{groups[1]}-{int(FONT_SIZE / 2)}"
        y2 = f"{groups[1]}-{int(FONT_SIZE / 2)}"

    if isinstance(x1, int) and isinstance(y1, int):
        return (x1, y1, x2, y2, norotate, nomirror)
    return BoundingBox(x1, y1, x2, y2, norotate, nomirror)


def circle_to_coord(
    groups: tuple, norotate: bool, nomirror: bool
) -> Union[tuple, BoundingBox]:
    all_int = True
    try:
        x = int(groups[0])
    except ValueError:
        x = str(groups[0])
        all_int = False
    try:
        y = int(groups[1])
    except ValueError:
        y = str(groups[1])
        all_int = False
    try:
        r = int(groups[2])
    except ValueError:
        r = str(groups[2])
        all_int = False
    
    if all_int:
        return (x - r, y - r, x + r, y + r, norotate, nomirror)
    return BoundingBox(f"{x}-{r}", f"{y}-{r}", f"{x}+{r}", f"{y}+{r}", norotate, nomirror)


def box_to_coord(
    groups: tuple, norotate: bool, nomirror: bool
) -> Union[tuple, BoundingBox]:
    all_int = True
    try:
        x1 = int(groups[0])
    except ValueError:
        x1 = str(groups[0])
        all_int = False
    try:
        y1 = int(groups[1])
    except ValueError:
        y1 = str(groups[1])
        all_int = False
    try:
        x2 = int(groups[2])
    except ValueError:
        x2 = str(groups[2])
        all_int = False
    try:
        y2 = int(groups[3])
    except ValueError:
        y2 = str(groups[3])
        all_int = False

    if isinstance(x1, int) and isinstance(x2, int):
        x1, x2 = min(x1, x2), max(x1, x2)
    if isinstance(y1, int) and isinstance(y2, int):
        y1, y2 = min(y1, y2), max(y1, y2)

    if all_int:
        return (x1, y1, x2, y2, norotate, nomirror)
    return BoundingBox(x1, y1, x2, y2, norotate, nomirror)


def to_to_coord(
    groups: tuple, norotate: bool, nomirror: bool
) -> Union[tuple, BoundingBox]:
    all_int = True
    try:
        x = int(groups[0])
    except ValueError:
        x = str(groups[0])
        all_int = False
    try:
        y = int(groups[1])
    except ValueError:
        y = str(groups[1])
        all_int = False

    if all_int:
        return (x, y, x, y, norotate, nomirror)
    return BoundingBox(x, y, x, y, norotate, nomirror)


NOROTATE = re.compile(r"\bNoRotate\b", re.IGNORECASE)
ENDNOROTATE = re.compile(r"\bEndNoRotate\b", re.IGNORECASE)
NOMIRROR = re.compile(r"\bNoMirror\b", re.IGNORECASE)
ENDNOMIRROR = re.compile(r"\bEndNoMirror\b", re.IGNORECASE)

GRAPHICS_REGEXS = {
    "line": re.compile(
        r"\bLine\s*\(\s*([^,]+),\s*([^,]+),\s*([^,]+),\s*([^,]+)\)", re.IGNORECASE
    ),
    "dashedline": re.compile(
        r"\bDashedLine\(\s*([^,]+),\s*([^,]+),\s*([^,]+),\s*([^,]+)\)", re.IGNORECASE
    ),
    "text": re.compile(
        r"\bText\(\s*([^,]+),\s*([^,]+),\s*([^)]+)\)", re.IGNORECASE
    ),  # variable
    "ptext": re.compile(
        r"PText\(\s*([^,]+),\s*([^,]+),\s*([^)]+)\)", re.IGNORECASE
    ),  # both
    "ftext": re.compile(
        r'FText\(\s*([^,]+),\s*([^,]+),\s*\"([^"]*)\"\)', re.IGNORECASE
    ),  # label
    "circle": re.compile(r"\bCircle\(\s*([^,]+),\s*([^,]+),\s*([^,]+)\)", re.IGNORECASE),
    "filledcircle": re.compile(
        r"FilledCircle\(\s*([^,]+),\s*([^,]+),\s*([^,]+)\)", re.IGNORECASE
    ),
    "box": re.compile(
        r"\bBox\(\s*([^,]+),\s*([^,]+),\s*([^,]+),\s*([^,]+)\)", re.IGNORECASE
    ),
    "filledbox": re.compile(
        r"FilledBox\(\s*([^,]+),\s*([^,]+),\s*([^,]+),\s*([^,]+)\)", re.IGNORECASE
    ),
    "arc": re.compile(
        r"Arc\(\s*([^,]+),\s*([^,]+),\s*([^,]+),\s*([^,]+),\s*([^,]+)\)", re.IGNORECASE
    ),
    "dot": re.compile(r"Dot\(\s*([^,]+),\s*([^,]+),\s*([^,]+)\)", re.IGNORECASE),
    "moveto": re.compile(r"MOVETO\(\s*([^,]+),\s*([^,]+)\)", re.IGNORECASE),
    "lineto": re.compile(r"LINETO\(\s*([^,]+),\s*([^,]+)\)", re.IGNORECASE),
}

GRAPHICS_REGEXS_EXT = {
    "setcolor": re.compile(r"SetColor\(\s*([^)]+)\)", re.IGNORECASE),
    "fontsize": re.compile(r"FontSize\(\s*([^)]+)\)", re.IGNORECASE),
    "linewidth": re.compile(r"LineWidth\(\s*([^)]+)\)", re.IGNORECASE),
    "overlay": re.compile(r"TransparentOverlay\(\s*([^)]+)\)", re.IGNORECASE),
    "group": re.compile(r"\bGroup(Start|End)", re.IGNORECASE)
}

GRAPHICS_FUNCTIONS: dict[str, Callable[[tuple], tuple]] = {
    "line": line_to_coord,
    "dashedline": line_to_coord,
    "text": text_to_coord,
    "ptext": text_to_coord,
    "ftext": text_to_coord,
    "circle": circle_to_coord,
    "box": box_to_coord,
    "filledcircle": circle_to_coord,
    "filledbox": box_to_coord,
    "arc": circle_to_coord,  # approximate with full circle
    "dot": circle_to_coord,
    "moveto": to_to_coord,
    "lineto": to_to_coord,
}
