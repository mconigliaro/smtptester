import pytest

import smtptester.dns as dns
import smtptester.smtp as smtp


@pytest.fixture
def resolver():
    return dns.DNSResolver(host="208.67.222.222")  # OpenDNS


def test_hosts_discover(resolver):
    assert isinstance(smtp.hosts_discover(resolver, "conigliaro.org")[0], smtp.SMTPHost)


def test_hosts_discover_no_domain(resolver):
    with pytest.raises(dns.DNSNoDomain):
        smtp.hosts_discover(resolver, "conigliaro.test")


def test_hosts_discover_no_mx_records(resolver):
    assert isinstance(
        smtp.hosts_discover(resolver, "www.conigliaro.org")[0], smtp.SMTPHost
    )


def test_hosts_set_with_ip(resolver):
    hosts = smtp.hosts_set(resolver, "127.0.0.1", port=0)
    assert hosts == [smtp.SMTPHost(name="", address="127.0.0.1", port=0, preference=0)]


def test_hosts_set_with_hostname(resolver):
    hosts = smtp.hosts_set(resolver, "conigliaro.org", port=0)
    assert isinstance(hosts[0], smtp.SMTPHost)


def test_hosts_set_with_invalid_hostname(resolver):
    with pytest.raises(dns.DNSNoDomain):
        smtp.hosts_set(resolver, "example.test", port=0)


def test_send_timeout(resolver):
    host = smtp.SMTPHost(name="", address="127.0.0.1", port=0, preference=0)
    with pytest.raises(smtp.SMTPTemporaryError):
        smtp.send(host, "recipient@example.test", timeout=1)
