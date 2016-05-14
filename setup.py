# -*- coding: utf-8 -*-


import re
from setuptools import setup, find_packages


# determine version and the author
code = open('neon/__init__.py', 'r').read(1000)
version = re.search(r'__version__ = \'([^\']*)\'', code).group(1)
author = re.search(r'__author__ = \'([^\']*)\'', code).group(1)


setup(
    name='neon-py',
    version=version,
    author=author,
    description='NEON parser for Python',
    long_description=open('README.rst').read(),
    keywords=['neon', 'parser', 'config file'],
    author_email='dedikx@gmail.com',
    url='https://github.com/paveldedik/neon-py',
    license=open('LICENSE').read(),
    packages=find_packages(exclude=['tests']),
    install_requires=['python-dateutil==2.5.3'],
    include_package_data=True,
    zip_safe=False,
    classifiers=[
        'Programming Language :: Python',
        'Operating System :: OS Independent',
        'Topic :: Utilities',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
    ]
)
