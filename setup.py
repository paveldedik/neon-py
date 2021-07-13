# -*- coding: utf-8 -*-


import re

from setuptools import find_packages, setup

# determine version and the author
code = open("neon/__init__.py", "r").read(1000)
version = re.search(r"__version__ = \"([^\"]*)\"", code).group(1)
author = re.search(r"__author__ = \"([^\"]*)\"", code).group(1)

install_deps = ["python-dateutil", "more-itertools"]
tests_deps = ["pytest"]
extras_deps = {"test": tests_deps}

setup(
    name="neon-py",
    version=version,
    author=author,
    description="NEON parser for Python",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    keywords=["neon", "parser", "config file"],
    author_email="dedikx@gmail.com",
    url="https://github.com/paveldedik/neon-py",
    license="BSD",
    packages=find_packages(exclude=["tests"]),
    install_requires=install_deps,
    tests_require=tests_deps,
    extras_require=extras_deps,
    include_package_data=True,
    zip_safe=False,
    classifiers=[
        "Programming Language :: Python",
        "Operating System :: OS Independent",
        "Topic :: Utilities",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
    ],
)
