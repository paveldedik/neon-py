# -*- coding: utf-8 -*-


__author__ = "Pavel Dedik"
__version__ = "0.1.5"


from .decoder import parse
from .encoder import to_string

__all__ = ("decode", "encode")


def decode(config):
    try:
        string = config.read()
    except AttributeError:
        string = config
    return parse(string)


def encode(tree):
    return to_string(tree)
