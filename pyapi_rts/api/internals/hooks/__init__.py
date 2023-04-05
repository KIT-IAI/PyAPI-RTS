# LGPL-3.0 License
# Copyright (c) 2023 KIT-IAI-ESA

from .component_hook import ComponentHook
from .linked_node_hook import LinkedNodeHook
from .special_value_hook import SpecialValueHook
from .tline_hook import TLineHook
from .xr_trf_hook import XrTrfHook

__all__ = [
    "LinkedNodeHook",
    "SpecialValueHook",
    "TLineHook",
    "XrTrfHook",
]

hooks: list[ComponentHook] = [
    LinkedNodeHook,
    SpecialValueHook,
    TLineHook,
    XrTrfHook,
]