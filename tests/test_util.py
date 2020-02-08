import pytest as pt
import smtptester.util as util


@pt.mark.parametrize("addr, expected", [("127.0.0.1", True), ("example.test", False)])
def test_is_ip_address(addr, expected):
    assert util.is_ip_address(addr) == expected


@pt.mark.parametrize(
    "addr, expected",
    [
        ("", util.EmailAddress(user="", domain="")),
        ("@", util.EmailAddress(user="", domain="")),
        ("foo", util.EmailAddress(user="foo", domain="")),
        ("foo@", util.EmailAddress(user="foo", domain="")),
        ("@bar", util.EmailAddress(user="", domain="bar")),
        ("foo@bar", util.EmailAddress(user="foo", domain="bar")),
    ],
)
def test_parse_email_address(addr, expected):
    assert util.parse_email_address(addr) == expected
