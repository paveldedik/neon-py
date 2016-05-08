# -*- coding: utf-8 -*-


from collections import OrderedDict


class Entity(object):
    """Representation of Foo(bar=1) literal."""

    def __init__(self, value=None, attrs=None):
        self.value = value
        self.attributes = OrderedDict(attrs) or OrderedDict()

    def __repr__(self):
        keywords = ', '.join(['{}={}'.format(key, value)
                             for key, value in self.attributes.items()])
        return '{}({})'.format(self.value, keywords)

    def __str__(self):
        return repr(self)
