# LGPL-3.0 License
# Copyright (c) 2023 KIT-IAI-ESA

from enum import Enum


class NodeType(Enum):
    """
    Enum for the different types of nodes

    :param Enum: NAME_CONNECTED_LINKED, NAME_CONNECTED, OTHER
    :type Enum: Enum
    """

    NAME_CONNECTED_LINKED = "NAME_CONNECTED:LINKED"
    NAME_CONNECTED = "NAME_CONNECTED"
    OTHER = "OTHER"


class NodeIO(Enum):
    """
    Enum for the different types of nodes

    :param Enum: INPUT, OUTPUT, IO, EXTERNAL, UNDEFINED, DEFAULT, GROUND, SHORT, FPGA_SOLVER, VSC, ELECTRICAL
    :type Enum: Enum
    """

    UNDEFINED = "UNDEFINED"
    INPUT = "INPUT"
    OUTPUT = "OUTPUT"
    IO = "I/O"
    EXTERNAL = "EXTERNAL"
    DEFAULT = "DEFAULT"
    GROUND = "GROUND"
    SHORT = "SHORT"
    FPGA_SOLVER = "FPGA_SOLVER"
    VSC = "VSC"
    ELECTRICAL = "ELECTRICAL"
