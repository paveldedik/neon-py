# -*- coding: utf-8 -*-


__author__ = 'Pavel Dedik'
__version__ = '0.1.0'


from .decoder import parse


__all__ = ('decode', 'encode')


def decode(config):
    try:
        string = config.read()
    except AttributeError:
        string = config
    return parse(string)


def encode(tree):
    raise NotImplementedError
