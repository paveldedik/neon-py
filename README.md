NEON for Python
===============

[![Test](https://github.com/paveldedik/neon-py/actions/workflows/test.yml/badge.svg)](https://github.com/paveldedik/neon-py/actions/workflows/test.yml)

NEON is very similar to YAML. The main difference is that the NEON supports
"entities"(so can be used e.g.to parse phpDoc annotations) and tab characters
for indentation. NEON syntax is a little simpler.

Example of Neon code:

```yaml
# neon example

name: Homer

address:

    street: 742 Evergreen Terrace
    city: Springfield

children:

    + Bart
    + Lisa
    + Maggie

entity: Column(type=integer)
```

Installation
------------

To install NEON parser for Python, simply run:

```bash
pip install neon-py
```

Quick start
-----------

Decoding NEON config files is super easy:

```python
import neon

with open('/path/to/config.neon', 'r') as fd:
    config = neon.decode(fd.read())
```

Links
-----

* [Neon sandbox](http://ne-on.org)
* [Neon for PHP](https://github.com/nette/neon)
* [Neon for Javascript](https://github.com/matej21/neon-js)
