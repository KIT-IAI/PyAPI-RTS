# LGPL-3.0 License
# Copyright (c) 2023 KIT-IAI-ESA

from pyapi_rts.api.parameters.string_parameter import StringParameter


class ColorParameter(StringParameter):

    def __init__(self, value):
        super().__init__(value)
        self.type = "ColorParameter"
