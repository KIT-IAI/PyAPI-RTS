# LGPL-3.0 License
# Copyright (c) 2023 KIT-IAI-ESA

def valid_file_name(string: str) -> str:
    """
    Converts a string to a valid file name

    :param string: The string to convert
    :type string: str
    :return: The converted string
    :rtype: str
    """
    string = string.replace("''", "subtr")
    string = string.replace("'", "tr")
    return ("d" if len(string) > 0 and string[0].isdigit() else "") + "".join(
        [c if c.isalnum() else "" for c in string]
    )
