import pytest

import neon
from neon import errors

NEON_ERROR_COLON1 = "a: (a: B)"
NEON_ERROR_COLON2 = "a: [1: 2]"

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


NEON_UNEXPECTED_END = "a: ["
NEON_UNEXPECTED_END_MSG = "Unexpected end of file, expected ',' or ']'."


def test_unexpected_end():
    with pytest.raises(errors.ParserError) as excinfo:
        neon.decode(NEON_UNEXPECTED_END)
    assert str(excinfo.value) == NEON_UNEXPECTED_END_MSG
