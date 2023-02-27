# LGPL-3.0 License
# Copyright (c) 2023 KIT-IAI-ESA

from pyapi_rts.api.internals.blockreader import BlockReader


class DfxFileReader(BlockReader):
    """
    A BlockReader loading a draft from a dfx file
    """

    def __init__(self, path: str) -> None:
        """
        Inititalize a DfxFileReader

        :param path: Path to .dfx file
        :type path: str
        """
        with open(path, "r", encoding="cp1252") as draft_in:
            BlockReader.__init__(self, draft_in.readlines())
