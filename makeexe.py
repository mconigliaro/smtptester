#!/usr/bin/python
# -*- coding: utf-8 -*-
################################################################################
# SMTP Tester py2exe script
# Copyright (c) 2009 Michael Conigliaro <mike [at] conigliaro [dot] org>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
################################################################################
from distutils.core import setup
import os
import py2exe
import subprocess
import sys


CWD = os.path.abspath(sys.path[0])
MAKENSIS_PATH = os.path.join(os.environ["ProgramFiles"], "NSIS", "makensis.exe")
MAKENSIS_OPTS = "/V4"
MAKENSIS_SCRIPT = os.path.join(CWD, "smtptester.nsi")


# Initialize build environment
for d in ['dist', 'inst']:
    if not os.path.isdir(os.path.join(CWD, d)):
        os.mkdir(os.path.join(CWD, d))

# Build executable
sys.argv.append('py2exe')
setup(
    windows = [{
        'script': "smtptester.py",
        'icon_resources': [(0, "smtptester.ico")]
    }],
    options = { 'py2exe': {
        'packages': ['dns'],
        'dll_excludes': ["MSVCP90.dll"],
        'bundle_files': 1,
        'optimize': 2 }
    },
    zipfile = None,
    data_files = [],
)

# Build installer
subprocess.call("%s %s %s" % (MAKENSIS_PATH, MAKENSIS_OPTS, MAKENSIS_SCRIPT))
