NEON for Python
===============

NEON is very similar to YAML. The main difference is that the NEON supports "entities" (so can be used e.g. to parse phpDoc annotations) and tab characters for indentation. NEON syntax is a little simpler.

Example of Neon code:

```
# neon example

name: Homer

address:
    street: 742 Evergreen Terrace
    city: Springfield

children:
    - Bart
    - Lisa
    - Maggie

entity: Column(type=integer)
```

Installation
------------

```
$ pip install neon-py
```
