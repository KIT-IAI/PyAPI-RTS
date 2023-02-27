# LGPL-3.0 License
# Copyright (c) 2023 KIT-IAI-ESA

import copy
from .extracted.ext_component import ExtComponent
from .extracted.ext_enum_parameter import ExtEnumParameter


class EnumHashPool:
    """
    Manages a collection of ExtEnumParameters in a hash table.
    """

    def __init__(self):
        """
        Initializes the hash table.
        """
        self.__pool: dict[int, ExtEnumParameter] = {}

    @property
    def pool(self):
        """
        Returns the pool.
        """
        return self.__pool

    def add(self, component: ExtComponent, enum: ExtEnumParameter):
        """
        Adds an ExtEnumParameter to the hash table.

        :param enum: The Enum Parameter to add.
        :type enum: ExtEnumParameter
        """
        existing_enum = (
            self.__pool[enum.options_hash] if enum.options_hash in self.__pool else None
        )
        if existing_enum is None:
            if any(
                map(
                    (lambda en: en.name.lower() == enum.name.lower()),
                    self.__pool.values(),
                )
            ):
                next_index = len(
                    list(
                        filter(
                            (
                                lambda en: self.remove_tailing_digits(en.name.lower())
                                == self.remove_tailing_digits(enum.name.lower())
                            ),
                            self.__pool.values(),
                        )
                    )
                )
                enum_copy = copy.deepcopy(enum)
                enum_copy.set_name(enum_copy.name + str(next_index))
                # enumPool.append(en)
                self.__pool[enum_copy.options_hash] = enum_copy
                existing_enum = enum_copy
            else:
                self.__pool[enum.options_hash] = enum
        if existing_enum is not None:
            for param in component.parameters:
                if param.comp_type == enum.enum_type:
                    param.set_type(existing_enum.name.title() + "EnumParameter")
            for coll in component.collections:
                for param in coll.parameters:
                    if param.comp_type == enum.enum_type:
                        param.set_type(existing_enum.name.title() + "EnumParameter")

    def load_from_file(self, pool_path: str) -> bool:
        """
        Load the enum pool from a file and generate the enum hash pool.

        :param path: The path to the file in enum pool format.
        :type path: str
        :return: list of enum parameters.
        :rtype: list[ExtEnumParameter]
        """
        try:
            with open(pool_path, "r", encoding="cp1252") as f:
                buffer = []
                for line in f:
                    if line.startswith("#") or line.strip() == "":
                        continue
                    if line.rstrip() == "END":
                        enum = ExtEnumParameter.read(buffer + [line])
                        self.__pool[enum.options_hash] = enum
                        buffer = []
                    else:
                        buffer.append(line.rstrip())

            return True
        except OSError as exception:
            print(f"Could not read hash pool: {exception}")
            return False

    def get_hash(self, name: str) -> int:
        """
        Returns the hash of the enum parameter with the given name.
        """
        for enum in self.__pool.values():
            if enum.name.lower() == name.lower():
                return enum.options_hash

    def remove_tailing_digits(self, string: str) -> str:
        """
        Removes the trailing digits from a string.

        :param s: The string to remove the trailing digits from.
        :type s: str
        :return: The string without the trailing digits.
        :rtype: str
        """
        while string[-1].isdigit():
            string = string[:-1]
        return string
