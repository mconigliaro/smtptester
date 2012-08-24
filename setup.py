#!/usr/bin/env python

import os

import distribute_setup
distribute_setup.use_setuptools()
from setuptools import setup, find_packages

import smtptester


def read(file):
    with open(os.path.abspath(os.path.join(os.path.dirname(__file__), file))) as f:
        result = f.read()
    f.closed
    return result

setup(
    name = ''.join(smtptester.__name__.lower().split()),
    version = smtptester.__version__,

    author = smtptester.__author__,
    author_email = smtptester.__author_email__,
    description = smtptester.__description__,
    long_description = read('README.rst'),
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

    packages = find_packages(),
    scripts = ['bin/smtptester'],
    data_files = ['smtptester.xpm']
)
