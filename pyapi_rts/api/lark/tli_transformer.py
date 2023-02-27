# LGPL-3.0 License
# Copyright (c) 2023 KIT-IAI-ESA

import pathlib
from enum import Enum
from lark import Lark, Token, Transformer

PATH = pathlib.Path(__file__).parent.absolute()


class TliDataType(Enum):
    """
    Enum for the different data types in the tli file.
    """

    #: Allow both data types, keys in upper case use metadata, keys in lower case use data if both exist at path.
    ANY = 1
    #: Datatype from key-value entries in TliSections.
    DATA = 2
    #: Metadata, defined in TliRtdsMetadata.
    METADATA = 3
    #: Section, defined in TliSections.
    SECTION = 4


class TliRtdsMetadata:
    """
    Contains key-value metadata in \*.tli files
    """

    def __init__(self, key, value):
        #: The key of the metadata
        self.key = key
        #: The value of the metadata
        self.value = value


class TliSection:
    """
    Contains a section in a \*.tli file. The title can be a string or key-value pair.
    """

    def __init__(self, title, value=None):
        #: The title of the section.
        self.title_key: str = title
        #: The value of the title if it is a key-value pair. None otherwise.
        self.title_value: str | None = value
        #: The sections contained in this section
        self.sections: list[TliSection] = {}
        #: The key-value pairs contained in this section
        self.dictionary = {}
        #: The key-value pairs starting with '!RTDS_' in \*.tli files.
        self.metadata: list[TliRtdsMetadata] = []

    def write(self) -> str:
        """
        Returns the section as a string.
        """
        output = ""
        if self.title_value is None:
            output += f"{self.title_key}:\n"  # Simple title
        else:
            output += f"{self.title_key} = {self.title_value}\n"  # Key-value title
        output += "  {\n"

        for meta in self.metadata:
            output += f"  !RTDS_{meta.key} = {meta.value}\n"

        for key, value in self.dictionary.items():
            output += f"  {key} = {value}\n"

        for section in self.sections:
            section_write = section.write().split("\n")
            section_write = [f"  {line}" for line in section_write]
            output += "\n".join(section_write)

        output += "  }\n"

        return output

    def get(self, path: str, data_type: TliDataType = TliDataType.ANY) -> str:
        """
        Returns the data, metadata or section at the given path.

        :param path: Path to the section. If it only contains whitespace, returns the section itself.
        :type path: str
        :param data_type: The type of data to search for at path.
        :type data_type: TliDataType
        :return: The section at the given path
        :rtype: TliSection
        """
        path = path.split("/")

        if (
            len(path) == 1 and path[0].strip() == ""
        ):  # If path is empty, return the section itself.
            if data_type in (TliDataType.SECTION, TliDataType.ANY):
                return self
            else:
                raise ValueError(
                    "Path is empty and data_type is not TliDataType.SECTION or TliDataType.ANY"
                )

        item = None
        if path[0] in self.dictionary:
            item = self.dictionary[path[0]]
        metadata = None
        if path[0].lower() in map(lambda x: x.key.lower(), self.metadata):
            metadata = self.metadata[
                list(map(lambda x: x.key.lower(), self.metadata)).index(path[0].lower())
            ]

        if len(path) > 1:
            # Check next section in path
            section = next(filter((lambda x: x.title_key == path[0]), self.sections))
            return section.get("/".join(path[1:]), data_type)
        else:
            if data_type == TliDataType.DATA:
                if item is None:
                    raise Exception(f"No data found at {path[0]}")
                return item
            elif data_type == TliDataType.METADATA:
                if metadata is None:
                    raise Exception(f"No metadata found at {path[0]}")
                return metadata.value
            else:
                if item is None and metadata is None:
                    raise Exception(f"No data or metadata found at: {path[0]}")
                if item is None:
                    return metadata.value  # Only metadata was found
                if metadata is None:
                    return item  # Only item was found
                if "".join(
                    path[0].split("_")
                ).isupper():  # Check if key is all upper case or underscores
                    # Metadata has priority over data.
                    return metadata
                else:
                    # Data has priority over metadata.
                    return item


class TliTransformer(Transformer):
    """
    Transformer for the lark parser for .tli files
    """

    def __init__(self):
        super().__init__()

    def value(self, val):
        return val[0].value

    def pair(self, args):
        return args[0].value.strip(), args[1]

    def dict(self, items):
        return items

    def section(self, items):
        title = ""
        title_value = None
        if items[0] is None:
            # Empty section
            title = ""
        elif isinstance(items[0], tuple):
            title = items[0][0]
            title_value = items[0][1]
        else:
            # Section
            title = items[0].value

        # Sort children into data and rtds metadata
        dictionary = {}
        sections = []
        rtds_metadata = []
        last_key: str = ""  # The last key written to the dictionary

        for item in items[1]:
            if isinstance(item, TliRtdsMetadata):
                rtds_metadata.append(item)
            elif isinstance(item, tuple):
                dictionary[item[0]] = item[1]
                last_key = item[0]
            elif isinstance(item, TliSection):
                if item.title_key == "":
                    item.title_key = last_key
                    item.title_value = dictionary.pop(last_key)
                sections.append(item)
            else:
                raise Exception("Unexpected item in section: " + str(item))

        title = title.strip()  # Remove whitespace

        tli_section = TliSection(title, title_value)
        tli_section.dictionary = dictionary
        tli_section.sections = sections
        tli_section.metadata = rtds_metadata

        return tli_section

    def rtds_meta(self, content):
        key = "".join(content[:-1])
        value = content[-1]
        if isinstance(value, Token):
            value = value.value
        return TliRtdsMetadata(key, value)

    def start(self, items):
        tli_file = TliFile()
        for item in items:
            if isinstance(item, TliSection):
                tli_file.sections.append(item)
            elif isinstance(item, TliRtdsMetadata):
                tli_file.metadata.append(item)
            else:
                pass
        return tli_file


class TliFile:
    """
    The class for a .tli file.
    """

    def __init__(self):
        self.sections: list[TliSection] = []
        self.metadata: list[TliRtdsMetadata] = []

    def get(
        self, path: str, data_type: TliDataType = TliDataType.ANY
    ) -> str | TliSection:
        """
        Gets the value of the key at the path.

        :param path: The path to the key through the sections, split by '/'.
        :type path: str
        :param data_type: The type of data to search for at path.
        :type data_type: TliDataType
        :return: The value of the key at the path.
        :rtype: str
        """

        path = path.split("/")
        # Check for metadata on top level of file
        metadata = next(
            filter(
                (lambda x: x.key.lower() == path[0].lower()),
                self.metadata,
            ),
            None,
        )

        for section in self.sections:
            if section.title_key == path[0]:
                if len(path) == 1:
                    if data_type != TliDataType.DATA:
                        if not metadata is None:
                            return metadata.value  # Metdata takes priority over section
                return section.get(
                    "/".join(path[1:]), data_type
                )  # Return data or section at path

        if not metadata is None:
            return metadata.value

    @classmethod
    def from_file(cls, file_path: str) -> "TliFile":
        """
        Creates a TliFile from a file.

        :param file_path: The path to the file.
        :type file_path: str
        :return: The TliFile created from the file.
        :rtype: TliFile
        """
        tli_file = TliFile()
        tli_file.read_file(file_path)
        return tli_file

    def read_file(self, path: str) -> None:
        """
        Reads a .tli file from the path and fills the object with the data
        :param path: The path to the .tli file
        :type path: str
        :return: None
        """

        tli_parser = Lark.open(
            PATH / "definitions/tli.lark",
            parser="earley",
        )

        with open(path, "r") as file:
            parsed = tli_parser.parse(file.read())
            new_tli = TliTransformer().transform(parsed)
            self.sections = new_tli.sections
            self.metadata = new_tli.metadata

    def __str__(self):
        """
        Returns a string representation of the object.

        :return: A string representation of the object.
        :rtype: str
        """
        output = ""
        for meta in self.metadata:
            output += f"!RTDS_{meta.key.upper()} = {meta.value}\n"
        for section in self.sections:
            output += section.write()
            output += "\n"
        return output

    def write_file(self, path: str) -> bool:
        """
        Writes the .tli file to the path.

        :param path: The path to write the .tli file to.
        :type path: str
        :return: True if the file was written, False otherwise.
        :rtype: bool
        """
        try:
            with open(path, "w") as file:
                file.write(str(self))
        except Exception as e:
            print(f"Error writing *.tli file: {e}")
            return False
        return True
