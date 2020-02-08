import pytest as pt
import smtptester.dns as dns

dns_host = "208.67.222.222"  # OpenDNS
resolver = dns.DNSResolver(host=dns_host)
timeout_resolver = dns.DNSResolver(host=dns_host, timeout=-1)


def test_resolver_a_records():
    assert isinstance(resolver.a("conigliaro.org")[0], dns.ARecord)


def test_resolver_mx_records():
    assert isinstance(resolver.mx("conigliaro.org")[0], dns.MXRecord)


def test_resolver_no_domain():
    with pt.raises(dns.DNSNoDomain):
        resolver.a("conigliaro.test")


def test_resolver_no_records():
    with pt.raises(dns.DNSNoRecords):
        resolver.mx("www.conigliaro.org")


def test_resolver_timeout():
    with pt.raises(dns.DNSConnectionError):
        timeout_resolver.a("conigliaro.org")
