===========
SMTP Tester
===========

I spent a long time searching for a tool that would help me troubleshoot SMTP
problems quickly and easily without having to resort to telnet. Finally, I gave
up and wrote my own.

Features
--------

- Tested on OSX, Linux, and Windows
- Graphical (no more telnet)
- Trace window showing live progress from DNS record look-ups through SMTP
  session
- Ability to override all DNS and SMTP settings
- Support for SASL and TLS

Screenshots
-----------

.. image:: https://github.com/mconigliaro/smtptester/raw/master/screenshots/osx.png

.. image:: https://github.com/mconigliaro/smtptester/raw/master/screenshots/linux.png

.. image:: https://github.com/mconigliaro/smtptester/raw/master/screenshots/windows.png

Installation
------------

Install `wxPython <http://wxpython.org/download.php>`_ (preferably version 2.9, although success has been reported for 2.8 on some platforms)

::

  # pip install smtptester

...or:

::

  # easy_install smtptester

This should add an **smtptester** executable to your **$PATH**.

License
-------

Copyright (C) 2012 Michael Paul Thomas Conigliaro

Permission is hereby granted, free of charge, to any person obtaining a copy of
this software and associated documentation files (the "Software"), to deal in
the Software without restriction, including without limitation the rights to
use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies
of the Software, and to permit persons to whom the Software is furnished to do
so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

Credits
-------

- `Michael Paul Thomas Conigliaro <http://conigliaro.org>`_: Original author
