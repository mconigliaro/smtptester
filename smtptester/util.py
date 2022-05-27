import ipaddress
import re
from typing import NamedTuple


class EmailAddress(NamedTuple):
    user: str
    domain: str


def is_ip_address(addr: str) -> bool:
    try:
        ipaddress.ip_address(addr)
        return True
    except ValueError:
        return False


def parse_email_address(address: str) -> EmailAddress:
    u_match = re.search(r"^([^@]*)@?", address)
    u = "" if u_match is None else u_match.group(1)

    d_match = re.search(r"@([^@]*)$", address)
    d = "" if d_match is None else d_match.group(1)

    return EmailAddress(user=u, domain=d)
