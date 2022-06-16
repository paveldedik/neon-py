from datetime import datetime

from dateutil.tz import tz

import neon

NEON_ENTITY = """
entity: Column(something, type=int)
"""


def test_entity():
    expected = {"entity": neon.entity.Entity("Column", {0: "something", "type": "int"})}
    assert neon.decode(NEON_ENTITY) == expected


NEON_TYPES = """
string: "a () #' text"
integer: 5902
hexint: 0xAA
octint: 0o666
binint: 0b111000111
float: 5.234
floatbig: 5e10
nones: [NULL, null, Null]
bools: [TRUE, True, true, YES, Yes, yes, ON, On, on,
        FALSE, False, false, NO, No, no, OFF, Off, off]
"""


def test_types():
    expected = {
        "string": "a () #' text",
        "integer": 5902,
        "hexint": 0xAA,
        "octint": 0o666,
        "binint": 0b111000111,
        "float": 5.234,
        "floatbig": 5e10,
        "nones": [None] * 3,
        "bools": [True] * 9 + [False] * 9,
    }
    result = neon.decode(NEON_TYPES)
    for key in expected:
        assert result[key] == expected[key]


NEON_DATETIME = """
- 2013-04-23 13:24:55.123456+0000
- 2015-01-20
- 2015-5-10
"""


def test_datetime():
    expected = [
        datetime(2013, 4, 23, 13, 24, 55, 123456, tzinfo=tz.tzutc()),
        datetime(2015, 1, 20),
        datetime(2015, 5, 10),
    ]
    assert neon.decode(NEON_DATETIME) == expected


def test_string_escaping():
    assert neon.decode('key: "msg"') == {"key": "msg"}
    assert neon.decode('key: "msg \\" end"') == {"key": 'msg " end'}
    assert neon.decode("key: 'msg \\' end'") == {"key": "msg ' end"}
    assert neon.decode('src: "\\\\usr\\\\share"') == {"src": "\\usr\\share"}
