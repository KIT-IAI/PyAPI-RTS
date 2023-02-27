# LGPL-3.0 License
# Copyright (c) 2023 KIT-IAI-ESA

import os
import hashlib
from pathlib import Path


class ClassGenerator:
    """
    A generator for a python class file with some helper functions and constants
    """

    GENERATED_PATH = "pyapi_rts.generated."
    BASIC_COMPONENT_PATH = "pyapi_rts.api.parameters"
    BASIC_COMPONENTS = [
        "BooleanParameter",
        "StringParameter",
        "NameParameter",
        "IntegerParameter",
        "FloatParameter",
        "ColorParameter",
    ]
    ENUM_PATH = "pyapi_rts.generated.enums."

    def __init__(self) -> None:
        self._cache: dict[str, list[str]] = {}

    def read_file(self, path: Path) -> list[str]:
        """
        Reads the file

        :param path: The path to the file
        :type path: Path
        :return: The lines of the file
        :rtype: list[str]
        """
        lines = []
        if self._cache.get(str(path)) is not None:
            lines = self._cache.get(str(path))
        else:
            with open(path, "r", encoding="utf8") as file:
                lines = file.readlines()
                lines = [file.name.split("\\")[-1].split("/")[-1].split(".txt")[0]] + [
                    l.rstrip() for l in lines
                ]
                self._cache[str(path)] = lines
        return lines

    def write_file(self, path: Path, lines: list[str]) -> bytes:
        """
        Writes the lines to the file

        :param path: The path to the file
        :type path: Path
        :param lines: The lines to write
        :type lines: list[str]
        :return: Hash of content of file
        :rtype: bytes
        """
        os.makedirs(path.parent, exist_ok=True)
        try:
            with open(path, "w", encoding="utf8") as file:
                lines_out = "\n".join(lines[1:])
                file.write(lines_out)
                hashing = hashlib.new("sha256")
                hashing.update(str.encode(lines_out))
                file_hash = str.encode(hashing.hexdigest())
                return file_hash
        except Exception as e:
            print("Error writing file: " + str(path) + ": " + str(e))
            return b""

    def replace(self, lines: list[str]) -> list[str]:
        """
        Replaces the lines in the file with the generated lines

        :param lines: The lines to replace
        :type lines: list[str]
        :return: The replaced lines
        :rtype: list[str]
        """
        return lines
