# -*- coding: utf-8 -*-


from __future__ import unicode_literals

import sys

PY3 = sys.version_info >= (3, 0)
PY37 = sys.version_info >= (3, 7)


if PY3:
    unicode = str
else:
    unicode = unicode

if PY37:
    OrderedDict = dict
else:
    from collections import OrderedDict


__all__ = ("unicode", "OrderedDict")
