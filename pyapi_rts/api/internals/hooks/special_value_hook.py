# LGPL-3.0 License
# Copyright (c) 2023 KIT-IAI-ESA

from typing import Any

from pyapi_rts.api.internals.hooks.component_hook import ComponentHook


class SpecialValueHook(ComponentHook):
    """
    A hook providing default values for some of the undocumented special values.
    """

    @classmethod
    def special_value(cls, component, key: str) -> Any | None:
        """
        Adds new special values to components.
        :param component: Component to evaluate.
        :type component: Component
        :return: Value of the special key or None if it does not exist for this component.
        :rtype: Any | None
        """

        if key.lower() == "frequency":
            if component.has_key("Freq"):
                return component.get_by_key("Freq").value
            elif component.has_key("Freq_Hz"):
                return component.get_by_key("Freq_Hz").value
            return 50.0  # Default frequency

        return None
