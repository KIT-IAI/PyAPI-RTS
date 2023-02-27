# LGPL-3.0 License
# Copyright (c) 2023 KIT-IAI-ESA

from pyapi_rts.api.parameters.string_parameter import StringParameter


class ColorParameter(StringParameter):
    default = "#000000"

    def __init__(self, key, value, from_str: bool = False):
        super().__init__(key, value, from_str)
        self.type = "ColorParameter"
