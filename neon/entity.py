# -*- coding: utf-8 -*-


from ._compat import OrderedDict


class Entity(object):
    """Representation of Foo(bar=1) literal."""

    def __init__(self, value=None, attrs=None):
        self.value = value
        self.attributes = OrderedDict(attrs) or OrderedDict()

    def __repr__(self):
        keywords = ", ".join(
            [
                "{}={}".format(key, value) if pos != key else str(value)
                for pos, (key, value) in enumerate(self.attributes.items())
            ]
        )
        return "{}({})".format(self.value, keywords)

    def __str__(self):
        return repr(self)

    def __eq__(self, other):
        return self.value == other.value and self.attributes == other.attributes
