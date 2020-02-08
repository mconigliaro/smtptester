import ipaddress as ip
import re
import typing as t


class EmailAddress(t.NamedTuple):
    user: str
    domain: str


def is_ip_address(addr):
    try:
        ip.ip_address(addr)
        return True
    except ValueError:
        return False


def parse_email_address(address):
    u = re.search(r"^([^@]*)@?", address).group(1)
    try:
        d = re.search(r"@([^@]*)$", address).group(1)
    except AttributeError:
        d = ""
    return EmailAddress(user=u, domain=d)
