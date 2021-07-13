# -*- coding: utf-8 -*-


from __future__ import unicode_literals

import neon

NEON_SIMPLE_DICT = """
a: b
c: d
"""


def test_simple_dict():
    assert neon.decode(NEON_SIMPLE_DICT) == {"a": "b", "c": "d"}


NEON_SIMPLE_LIST = """
- a
- b
"""


def test_simple_list():
    assert neon.decode(NEON_SIMPLE_LIST) == ["a", "b"]


NEON_SIMPLE = """
a:
    -
    - d
b:
    e:
    g: h
"""


def test_simple():
    expected = {"a": [None, "d"], "b": {"e": None, "g": "h"}}
    assert neon.decode(NEON_SIMPLE) == expected


NEON_LIST_OF_DICTS = """
- a:
    - b: False
- d: [1]
"""


def test_list_of_dicts():
    expected = [{"a": [{"b": False}]}, {"d": [1]}]
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
        "list": [1, "a", ["v", True]],
        "dict1": {"a": 5, "b": {1: [True]}},
        "dict2": {"d": 8, "e": {None: False}},
    }
    assert neon.decode(NEON_DATA_STRUCTURES) == expected


NEON_EMPTY_DATA_STRUCTURES = """
- {}
- []
- ()
- Tree()
"""


def test_empty_data_structures():
    expected = [{}, [], {}, neon.entity.Entity("Tree", {})]
    assert neon.decode(NEON_EMPTY_DATA_STRUCTURES) == expected
