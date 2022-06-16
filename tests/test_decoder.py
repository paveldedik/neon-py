from datetime import datetime

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
    expected = {
        "name": "Homer",
        "address": {
            "street": "742 Evergreen Terrace",
            "city": "Springfield",
            "country": ["a"],
            "whatever": ["b"],
        },
        "phones": {
            "home": "555-6528",
            "work": {
                "asdf": "555-7334",
                "wtf": 1234,
            },
        },
        "whoa": ["a", "b", "c", 100000.0, 34, datetime(2014, 1, 1, 0, 0)],
        "children": [
            "Bart",
            "Lisa",
            "Maggie",
            {
                "type": "whatever",
                "wtf": {"wtf": 5},
            },
        ],
        "entity": neon.entity.Entity("Column", {"type": "integer"}),
        "special": "#characters put in quotes",
    }
    assert neon.decode(NEON_DECODE_SAMPLE) == expected


NEON_UTF8_SUPPORT = """
- ěšíčťľĺ
- 5 × 6 ÷ 7 ± ∞ - π
"""


def test_utf8_support():
    expected = ["ěšíčťľĺ", "5 × 6 ÷ 7 ± ∞ - π"]
    assert neon.decode(NEON_UTF8_SUPPORT) == expected
