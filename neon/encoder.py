# -*- coding: utf-8 -*-


from __future__ import unicode_literals


def format_list(list_, indent_level):
    indent = "\t" * indent_level
    newline = "\n" if indent_level else "\n\n"
    return newline.join(
        ["{}- {}".format(indent, to_string(value, indent_level + 1)) for value in list_]
    )


def format_dict(dict_, indent_level):
    indent = "\t" * indent_level
    newline = "\n" if indent_level else "\n\n"
    return newline.join(
        [
            "{}{}: {}".format(indent, key, to_string(value, indent_level + 1))
            for key, value in dict_.items()
        ]
    )


def to_string(obj, indent_level=0):
    """Encodes given object using the NEON syntax.

    :param obj: Object to encode.
    :return: Encoded object.
    :rtype: string
    """
    if isinstance(obj, dict):
        return "\n" + format_dict(obj, indent_level)
    elif isinstance(obj, list):
        return "\n" + format_list(obj, indent_level)
    elif obj is None:
        return "Null"
    return str(obj)
