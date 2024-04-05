# LGPL-3.0 License
# Copyright (c) 2023 KIT-IAI-ESA

import re

from pyapi_rts.api.internals.block import Block


class DfxBlock:
    """Abstract class for handling conversion between source blocks and internal objects."""

    _title_regex: re.Pattern

    @classmethod
    def check_title(cls, title: str) -> bool:
        """Checks if block title fits definition of class

        :param title: Block title
        :type title: str
        :return: True if title fits definition of class
        :rtype: bool
        """
        return bool(cls._title_regex.match(title))

    def read_block(self, block: Block) -> None:
        """Read object from source block

        :param block: A source block corresponding to this type
        :type block: list[str]
        """

    def block(self) -> list[str]:
        """Get source block representation of object

        :return: Source block representation of object
        :rtype: list[str]
        """
        return []
