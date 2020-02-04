#!/usr/bin/env python

"""
    Protean - A prometheus client.
"""

import os
from setuptools import setup, find_packages


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name="pytheus",
    version="0.1",
    author="Joao Grilo",
    author_email="joao.grilo@gmail.com",
    description="Generate promteheus metrics",
    license="MIT",
    keywords="python prometheus exporter",
    url="https://github.com/grilo/pytheus",
    packages=find_packages(),
    long_description=read('README.md'),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "License :: OSI Approved :: MIT License",
    ],
    tests_require=['pytest-runner', 'pylint', 'pytest', 'pytest-cov', 'pytest-mock'],
    entry_points={
    'console_scripts': [
        'pytheus = pytheus.cli:main', # Meant to be used as a library, CLI for debugging
        ],
    },
)
