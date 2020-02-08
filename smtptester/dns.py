import dns.resolver as res
import logging as log
import typing as t

DNS_DEFAULT_PORT = 53
DNS_DEFAULT_TIMEOUT = 3
DNS_PROTOCOL_CHOICES = ("udp", "tcp")
DNS_DEFAULT_PROTOCOL = "udp"


class ARecord(t.NamedTuple):
    name: str
    address: str


class MXRecord(t.NamedTuple):
    name: str
    address: str
    preference: int = 0


class DNSResolver:
    def __init__(
        self,
        host=None,
        port=DNS_DEFAULT_PORT,
        timeout=DNS_DEFAULT_TIMEOUT,
        protocol=DNS_DEFAULT_PROTOCOL,
    ):
        self.resolver = res.Resolver()
        if host:
            self.resolver.nameservers = [host]
        self.resolver.port = port
        self.timeout = timeout
        self.tcp = True if protocol == "tcp" else False
        hosts = ", ".join(
            f"{h}:{self.resolver.port}" for h in self.resolver.nameservers
        )
        log.debug(f"Using DNS hosts: {hosts}")

    def a(self, domain):
        rs = []
        for r in self._query(domain, "a"):
            log.debug(f"Got answer: {r.address}")
            rs.append(ARecord(name=domain, address=str(r.address).rstrip(".")))
        return rs

    def mx(self, domain):
        rs = []
        for r in sorted(self._query(domain, "mx"), key=lambda r: r.preference):
            log.debug(f"Got answer: {r.preference} {r.exchange}")
            name = str(r.exchange).rstrip(".")
            rs.append(
                MXRecord(
                    name=name, address=self.a(name)[0].address, preference=r.preference
                )
            )
        return rs

    def _query(self, qname, rdtype):
        try:
            log.debug(f"Looking up {rdtype.upper()} records for {qname}")
            return self.resolver.query(
                qname, rdtype, lifetime=self.timeout, tcp=self.tcp
            )
        except res.NoAnswer as e:
            raise DNSNoRecords(e) from e
        except res.NXDOMAIN as e:
            raise DNSNoDomain(e) from e
        except res.Timeout as e:
            host = self.resolver.nameservers[0]
            port = self.resolver.port
            protocol = "TCP" if self.tcp else "UDP"
            address = f"{host}:{port}({protocol})"
            msg = f"DNS host failed: {address} Timeout={self.timeout}s"
            raise DNSConnectionError(msg) from e


class DNSException(Exception):
    pass


class DNSConnectionError(DNSException):
    pass


class DNSResponseError(DNSException):
    pass


class DNSNoDomain(DNSResponseError):
    pass


class DNSNoRecords(DNSResponseError):
    pass
