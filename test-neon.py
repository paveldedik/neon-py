# -*- coding: utf-8 -*-


import neon


with open('sample.neon', 'r') as fd:
    print neon.decode(fd)
