#!/usr/bin/env python

import os
import setuptools
import smtptester

setuptools.setup(
    name="smtptester",
    version=smtptester.VERSION,
    author=smtptester.AUTHOR,
    author_email="mike@conigliaro.org",
    description="A graphical and command line SMTP diagnostic tool",
    long_description=open(os.path.join(os.path.dirname(__file__), "README.md")).read(),
    long_description_content_type="text/markdown",
    url="https://github.com/mconigliaro/smtptester",
    packages=setuptools.find_packages(),
    package_data={"smtptester": ["data/*"]},
    scripts=["bin/smtptester", "bin/smtptester-gui"],
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Console",
        "Environment :: X11 Applications :: Qt",
        "Intended Audience :: Information Technology",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Topic :: Communications :: Email",
        "Topic :: System :: Systems Administration",
        "Topic :: Utilities",
    ],
    python_requires=">=3.7",
    install_requires=[
        "dnspython >=1.16, <2.0",
        "pyside2 >=5.14, <6.0"
    ]
)
