# LGPL-3.0 License
# Copyright (c) 2023 KIT-IAI-ESA

"""
Classes for handling parameters in RSCAD files.
"""

from .float_parameter import FloatParameter
from .integer_parameter import IntegerParameter
from .string_parameter import StringParameter
from .color_parameter import ColorParameter
from .name_parameter import NameParameter
from .connection_point import ConnectionPoint
from .parameter_collection import ParameterCollection
from .enum_parameter import EnumParameter
from .hex_parameter import HexParameter
from .parameter import Parameter


REAL = FloatParameter
INTEGER = IntegerParameter
CHAR = StringParameter
CHARACTER = StringParameter
NAME = NameParameter
COLOR = ColorParameter
STRING = StringParameter
# FILE
HEX = HexParameter
# IMAGE
# REAL_ARRAY
# TOGGLE is treated differently as it resolves an enum

__all__ = [
    "FloatParameter",
    "IntegerParameter",
    "StringParameter",
    "ColorParameter",
    "NameParameter",
    "ConnectionPoint",
    "ParameterCollection",
    "Parameter",
    "EnumParameter",
    "HexParameter",
    "REAL",
    "INTEGER",
    "CHAR",
    "CHARACTER",
    "NAME",
    "COLOR",
    "HEX",
    "STRING"
]
