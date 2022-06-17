import neon

NEON_INDENTED_LIST_VALUE = """
-
  aaa
"""


def test_indented_list_value():
    assert neon.decode(NEON_INDENTED_LIST_VALUE) == ["aaa"]


NEON_SIMPLE_VALUE = """
hello
"""


def test_simple_value():
    assert neon.decode(NEON_SIMPLE_VALUE) == "hello"


NEON_SIMPLE_LIST_VALUE = """
-
"""


def test_simple_list_value():
    assert neon.decode(NEON_SIMPLE_LIST_VALUE) == [None]
