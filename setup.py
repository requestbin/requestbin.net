#!/usr/bin/env python
import os
from setuptools import setup, find_packages

setup(
    name='requestbin.net',
    version='2.0',
    author='cuongmx',
    author_email='cuongmx@gmail.com',
    description='HTTP & DNS request collector and inspector',
    packages=find_packages(),
    install_requires=['feedparser'],
    data_files=[],
)
