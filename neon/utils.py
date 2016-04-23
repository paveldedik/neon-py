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
    """
    return ''.join(itertools.takewhile(str.isspace, string))
