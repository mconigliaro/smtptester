import pytest

import smtptester.dns as dns


@pytest.fixture
def dns_host():
    return "208.67.222.222"  # OpenDNS


@pytest.fixture
def resolver(dns_host):
    return dns.DNSResolver(host=dns_host)


@pytest.fixture
def timeout_resolver(dns_host):
    return dns.DNSResolver(host=dns_host, timeout=-1)


def test_resolver_a_records(resolver):
    assert isinstance(resolver.a("conigliaro.org")[0], dns.ARecord)


def test_resolver_mx_records(resolver):
    assert isinstance(resolver.mx("conigliaro.org")[0], dns.MXRecord)


def test_resolver_no_domain(resolver):
    with pytest.raises(dns.DNSNoDomain):
        resolver.a("conigliaro.test")


def test_resolver_no_records(resolver):
    with pytest.raises(dns.DNSNoRecords):
        resolver.mx("www.conigliaro.org")


def test_resolver_timeout(timeout_resolver):
    with pytest.raises(dns.DNSConnectionError):
        timeout_resolver.a("conigliaro.org")
