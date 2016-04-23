# -*- coding: utf-8 -*-


import re
from setuptools import setup, find_packages


# determine version and the author
code = open('neon/__init__.py', 'r').read(1000)
version = re.search(r'__version__ = \'([^\']*)\'', code).group(1)
author = re.search(r'__author__ = \'([^\']*)\'', code).group(1)


setup(
    name='neon',
    version=version,
    author=author,
    packages=find_packages(exclude=['tests']),
    install_requires=['python-dateutil==2.5.3'],
    include_package_data=True,
)
