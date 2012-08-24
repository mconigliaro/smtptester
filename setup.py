#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os

from distribute_setup import use_setuptools
use_setuptools()
from setuptools import setup, find_packages

import smtptester


setup(
    name = ''.join(smtptester.__app_name__.lower().split()),
    version = smtptester.__version__,

    author = smtptester.__author__,
    author_email = smtptester.__author_email__,
    description = smtptester.__description__,
    long_description = open(os.path.abspath(os.path.join(
                            os.path.dirname(__file__), 'README.rst'))).read(),
    url = smtptester.__url__,

    keywords = 'smtp tester',
    classifiers = [
        'Development Status :: 5 - Production/Stable',
        'Environment :: MacOS X',
        'Environment :: Win32 (MS Windows)',
        'Environment :: X11 Applications :: GTK',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2.6',
        'Topic :: Communications :: Email',
        'Topic :: System :: Networking',
        'Topic :: System :: Systems Administration',
        'Topic :: Utilities'
    ],

    install_requires = ['setuptools', 'dnspython'],

    packages = ['smtptester'],
    package_data = {
        'smtptester': ['data/*']
    },
    scripts = ['bin/smtptester']
)
