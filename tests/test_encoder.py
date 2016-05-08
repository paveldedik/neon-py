# -*- coding: utf-8 -*-


import pytest

import neon


NEON_DECODE_SAMPLE = """
# neon file - edit it now!

name: Homer

address:
    street: 742 Evergreen Terrace
    city: "Springfield"

#asdf
    country:
        - a
    whatever:
        - b

phones: { home: 555-6528, work: {
            asdf: 555-7334,
        wtf: 1234,
            }
        }

whoa: [a, b, c, 1e5, 0x22, 2014-01-01]

children:
    - Bart
    - Lisa
    - Maggie
    - (type=whatever, wtf=(wtf=5))

entity: Column(type=integer)

special: "#characters put in quotes"

# this is a comment
"""


def test_decode_sample():
    assert neon.decode(NEON_DECODE_SAMPLE)


NEON_SIMPLE_DICT = """
a: b
c: d
"""


def test_simple_dict():
    assert neon.decode(NEON_SIMPLE_DICT) == {'a': 'b', 'c': 'd'}


NEON_SIMPLE_LIST = """
- a
- b
"""


def test_simple_list():
    assert neon.decode(NEON_SIMPLE_LIST) == ['a', 'b']


NEON_SIMPLE = """
a:
    -
    - d
b:
    e:
    g: h
"""


def test_simple():
    expected = {'a': [None, 'd'], 'b': {'e': None, 'g': 'h'}}
    assert neon.decode(NEON_SIMPLE) == expected


NEON_ENTITY = """
entity: Column(something, type=int)
"""


def test_entity():
    expected = {'entity': neon.entity.Entity(
        'Column', {0: 'something', 'type': 'int'})}
    assert neon.decode(NEON_ENTITY) == expected


NEON_TYPES = """
string: "a () #' text"
integer: 5902
hexint: 0xAA
float: 5.234
floatbig: 5e10
nones: [NULL, null, Null]
bools: [TRUE, True, true, YES, Yes, yes, ON, On, on,
        FALSE, False, false, NO, No, no, OFF, Off, off]
"""


def test_types():
    expected = {
        'string': 'a () #\' text',
        'integer': 5902,
        'hexint': 0xAA,
        'float': 5.234,
        'floatbig': 5e10,
        'nones': [None] * 3,
        'bools': [True] * 9 + [False] * 9,
    }
    result = neon.decode(NEON_TYPES)
    for key in expected:
        assert result[key] == expected[key]
