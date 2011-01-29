from __future__ import absolute_import

import re
import socket


def is_ip(addr):
    result = False
    if re.search("^[0-9\.]+$", addr):
        try:
            aton = socket.inet_aton(addr)
            result = True
        except socket.error:
            pass
    return result
