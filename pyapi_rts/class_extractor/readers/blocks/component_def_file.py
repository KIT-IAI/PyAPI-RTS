# LGPL-3.0 License
# Copyright (c) 2023 KIT-IAI-ESA

from .graphics_block import GraphicsBlock
from .computations_block import ComputationsBlock
from .directives_block import DirectivesBlock
from .base_block_reader import BaseBlockReader
from .parameter_block import ParameterBlock
from .node_block import NodeBlock


class ComponentDefFile(BaseBlockReader):
    """
    Reads a component definition file
    """

    def __init__(self) -> None:
        super().__init__()
        self.blocks.append(ParameterBlock())
        self.blocks.append(NodeBlock())
        self.blocks.append(DirectivesBlock())
        self.blocks.append(GraphicsBlock())
        self.blocks.append(ComputationsBlock())

    def read_from_file(self, filename: str) -> bool:
        """
        Reads the file

        :param filename: Path to the file
        :type filename: str
        :returns: True if the file was read successfully
        :rtype: bool
        """
        lines = []
        try:
            with open(filename, "r", encoding="cp1252") as file_stream:
                lines = file_stream.readlines()
                if len(lines) == 0 or not "Component Builder" in lines[0]:
                    return False
                self.read(lines)
                return True
        except OSError as os_error:
            print("Error reading file: " + str(os_error))
            return False
        except UnicodeDecodeError as unicode_error:
            print("Error reading file: " + str(unicode_error))
            return False
