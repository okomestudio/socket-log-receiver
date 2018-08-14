# -*- coding: utf-8 -*-
import codecs
import os
import re

from setuptools import find_packages
from setuptools import setup


def find_meta(category, fpath='src/socket_log_receiver/__init__.py'):
    here = os.path.abspath(os.path.dirname(__file__))
    with codecs.open(os.path.join(here, fpath), 'r') as f:
        package_root_file = f.read()
    matched = re.search(
        r"^__{}__\s+=\s+['\"]([^'\"]*)['\"]".format(category),
        package_root_file, re.M)
    if matched:
        return matched.group(1)
    raise Exception('Meta info string for {} undefined'.format(category))


setup(
    name='socket_log_receiver',
    description='Socket log server',
    author=find_meta('author'),
    author_email=find_meta('author_email'),
    license=find_meta('license'),
    version=find_meta('version'),
    platforms=['Linux'],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Topic :: Utilities'],
    package_dir={'': 'src'},
    packages=find_packages('src'),
    url='https://github.com/okomestudio/socket_log_server',
    install_requires=[],
    extras_require={
        'dev': ['coverage>=4.5.1',
                'mock>=2.0.0',
                'pytest==3.7.0',
                'pytest-cov>=2.5.1',
                'pytest-xprocess>=0.12.1']
    },
    entry_points={
        'console_scripts': [
            'receiver=socket_log_receiver:main',
        ]
    }
)
