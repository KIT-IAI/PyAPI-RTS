# LGPL-3.0 License
# Copyright (c) 2023 KIT-IAI-ESA

from enum import Enum


class Stretchable(Enum):
    """
    Enum for the stretchable directives
    """

    NO = ("NO",)
    UP_DOWN = ("STRETCHABLE_UP_DOWN_LINE",)
    BOX = ("STRETCHABLE_BOX",)
