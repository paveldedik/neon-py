__author__ = "Pavel Dedik"
from .decoder import parse
from .encoder import to_string
from .version import version as __version__

__all__ = ("decode", "encode")


def decode(config):
    try:
        string = config.read()
    except AttributeError:
        string = config
    return parse(string)


def encode(tree):
    return to_string(tree)
