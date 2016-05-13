# -*- coding: utf-8 -*-


from __future__ import unicode_literals

import pytest

import neon
from neon import errors


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


NEON_LIST_OF_DICTS = """
- a:
    - b: False
- d: [1]
"""


def test_list_of_dicts():
    expected = [{'a': [{'b': False}]}, {'d': [1]}]
    assert neon.decode(NEON_LIST_OF_DICTS) == expected


NEON_DATA_STRUCTURES = """
list: [1, a,
       [v, True]
      ]
dict1: (
  a=5,
  b={1: [True]},
)
dict2: {
    d: 8,
  e: {Null: off},
}
"""


def test_data_structures():
    expected = {
        'list': [1, 'a', ['v', True]],
        'dict1': {'a': 5, 'b': {1: [True]}},
        'dict2': {'d': 8, 'e': {None: False}},
    }
    assert neon.decode(NEON_DATA_STRUCTURES) == expected


NEON_EMPTY_DATA_STRUCTURES = """
- {}
- []
- ()
- Tree()
"""


def test_empty_data_structures():
    expected = [{}, [], {}, neon.entity.Entity('Tree', {})]
    assert neon.decode(NEON_EMPTY_DATA_STRUCTURES) == expected


NEON_UTF8_SUPPORT = """
- ěšíčťľĺ
- 5 × 6 ÷ 7 ± ∞ - π
"""


def test_utf8_support():
    expected = ['ěšíčťľĺ', '5 × 6 ÷ 7 ± ∞ - π']
    assert neon.decode(NEON_UTF8_SUPPORT) == expected


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


NEON_ERROR_COLON1 = 'a: (a: B)'
NEON_ERROR_COLON2 = 'a: [1: 2]'

NEON_ERROR_COLON1_MSG = "Unexpected ':' on line 1, expected '=' or ',' or ')'."
NEON_ERROR_COLON2_MSG = "Unexpected ':' on line 1, expected ',' or ']'."


def test_error_colons():
    with pytest.raises(errors.ParserError) as excinfo:
        neon.decode(NEON_ERROR_COLON1)
    assert str(excinfo.value) == NEON_ERROR_COLON1_MSG

    with pytest.raises(errors.ParserError) as excinfo:
        neon.decode(NEON_ERROR_COLON2)
    assert str(excinfo.value) == NEON_ERROR_COLON2_MSG


NEON_BAD_INDENT = """
a:
  - b
   - c
"""
NEON_BAD_INDENT_MSG = "Unexpected indent on line 4."


def test_bad_indent():
    with pytest.raises(errors.ParserError) as excinfo:
        neon.decode(NEON_BAD_INDENT)
    assert str(excinfo.value) == NEON_BAD_INDENT_MSG


NEON_UNEXPECTED_END = 'a: ['
NEON_UNEXPECTED_END_MSG = "Unexpected end of file, expected ',' or ']'."


def test_unexpected_end():
    with pytest.raises(errors.ParserError) as excinfo:
        neon.decode(NEON_UNEXPECTED_END)
    assert str(excinfo.value) == NEON_UNEXPECTED_END_MSG
