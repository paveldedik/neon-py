# -*- coding: utf-8 -*-


import itertools


class classproperty(object):
    """Useful when class properties need to be defined."""

    def __init__(self, fget):
        self.fget = fget

    def __get__(self, obj, cls=None):
        if cls is None:
            cls = type(obj)
        return self.fget(cls)


def lstripped(string):
    """Number of potentially stripped characters on left.

    :return: A string of characters that will be stripped
        on the left side of the given string if the method
        `strip()` is called on it.
    :rtype: string
    """
    return ''.join(itertools.takewhile(str.isspace, string))


def variants(*strings):
    """Creates three variants of each string:

    - lowercase (e.g. `husky`)
    - title version (e.g. `Husky`)
    - uppercase (e.g. `HUSKY`)

    :return: A list of all variants of all given strings.
    :rtype: list
    """
    result = []
    for string in strings:
        lowercase = string.lower()
        result += [lowercase, lowercase.title(), string.upper()]
    return result
