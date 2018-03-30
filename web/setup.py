#!/usr/bin/env python
import os
from setuptools import setup, find_packages

setup(
    name='requestbin',
    version='2.0.0',
    author='Runscope',
    author_email='requestbin@runscope.com',
    description='HTTP request collector and inspector',
    packages=find_packages(),
    install_requires=['feedparser'],
    data_files=[],
)
