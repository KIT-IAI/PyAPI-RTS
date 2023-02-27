# LGPL-3.0 License
# Copyright (c) 2023 KIT-IAI-ESA

from .ext_enum_parameter import ExtEnumParameter
from .ext_parameter import ExtParameter
from ..utils import valid_file_name


class CompDefParameter:
    """
    A parameter of a component read from the definition file
    """

    def __init__(
        self, key, description, descValid, mystery, _type, default, _from, _to, _if
    ) -> None:
        #: The key of the parameter
        self.key = key
        #: The description of the parameter
        self.description = description
        self.desc_valid = descValid
        #: A number with undetermined purpose
        self.mystery = mystery
        self._type = _type
        #: The default value of the parameter
        self.default = default
        self._from = _from
        self._to = _to
        self._if = _if

    @property
    def comp_type(self):
        """
        The type of the component
        """
        return self._type

    def as_ext_parameter(self) -> tuple[ExtParameter, ExtEnumParameter | None]:
        """
        Converts the parameter to an ExtParameter maybe the dependent ExtEnumParameter

        :raises Exception: Type of parameter not supported
        :return: ExtParameter and ExtEnumParameter if dependent
        :rtype: tuple[ExtParameter, ExtEnumParameter | None]
        """
        if self._type.upper() == "REAL":
            return (
                ExtParameter(
                    self.key,
                    valid_file_name(self.key),
                    "FloatParameter",
                    self.default,
                    self.description,
                ),
                None,
            )
        if self._type.upper() == "INTEGER":
            return (
                ExtParameter(
                    self.key,
                    valid_file_name(self.key),
                    "IntegerParameter",
                    self.default,
                    self.description,
                ),
                None,
            )
        if self._type.upper() in ("CHARACTER", "CHAR"):
            return (
                ExtParameter(
                    self.key,
                    valid_file_name(self.key),
                    "StringParameter",
                    self.default,
                    self.description,
                ),
                None,
            )
        if self._type.upper() == "NAME":
            return (
                ExtParameter(
                    self.key,
                    valid_file_name(self.key),
                    "NameParameter",
                    self.default,
                    self.description,
                ),
                None,
            )
        if self._type == "TOGGLE":
            e = ExtEnumParameter(valid_file_name(self.key))
            for o in self.desc_valid.split(";"):
                e.options.append(o)

            p = ExtParameter(
                self.key, self.key, e._type, self.default, self.description
            )
            return (p, e)
        if self._type == "COLOR":
            return (
                ExtParameter(
                    self.key, self.key, "ColorParameter", self.default, self.description
                ),
                None,
            )
        if self._type in ("HEX", "ALPHANUM", "REAL_ARRAY", "FILE"):
            # Types are known but not explicitly supported
            return (
                ExtParameter(
                    self.key,
                    self.key,
                    "StringParameter",
                    self.default,
                    self.description,
                ),
                None,
            )

        # Fallback
        raise Exception("Unknown type: " + self._type)
