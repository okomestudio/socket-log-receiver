#!/usr/bin/env python
# -*- coding: utf-8 -*-
import codecs
import os
import re

from setuptools import find_packages
from setuptools import setup

here = os.path.abspath(os.path.dirname(__file__))


def fread(filename):
    with codecs.open(os.path.join(here, filename), "r", encoding="utf-8") as f:
        return f.read()


def meta(category, fpath="src/socket_log_receiver/__init__.py"):
    here = os.path.abspath(os.path.dirname(__file__))
    with codecs.open(os.path.join(here, fpath), "r") as f:
        package_root_file = f.read()
    matched = re.search(
        r"^__{}__\s+=\s+['\"]([^'\"]*)['\"]".format(category), package_root_file, re.M
    )
    if matched:
        return matched.group(1)
    raise Exception("Meta info string for {} undefined".format(category))


requires = []

setup_requires = []

dev_requires = ["black>=19.10b", "flake8>=3.7.9", "isort>=4.3.21", "pre-commit>=2.2.0"]

tests_require = [
    "coverage>=4.5.4",
    "mock>=3.0.5",
    "pytest>=4.6.9",
    "pytest-cov>=2.8.1",
    "pytest-xprocess>=0.13.1",
]

setup(
    name="socket-log-receiver",
    version=meta("version"),
    description="A light-weight socket log receiver",
    long_description=fread("README.md"),
    long_description_content_type="text/markdown",
    author=meta("author"),
    author_email=meta("author_email"),
    license=meta("license"),
    url="https://github.com/okomestudio/socket-log-receiver",
    platforms=["Linux"],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7",
        "Topic :: Utilities",
    ],
    package_dir={"": "src"},
    packages=find_packages("src"),
    python_requires=">=2.7, !=3.0.*, !=3.1.*, !=3.2.*, !=3.3.*",
    install_requires=[],
    tests_require=tests_require,
    extras_require={"dev": dev_requires + tests_require, "test": tests_require},
    entry_points={
        "console_scripts": ["log_receiver=socket_log_receiver.__main__:main"]
    },
)
