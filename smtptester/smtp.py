import getpass
import logging
import os
import smtplib
import socket
from typing import Iterable, NamedTuple

import smtptester.util as util
import smtptester.dns as dns


SMTP_DEFAULT_SENDER = f"{getpass.getuser()}@{socket.getfqdn()}"
SMTP_DEFAULT_PORT = 25
SMTP_DEFAULT_TIMEOUT = 3
SMTP_DEFAULT_HELO = socket.getfqdn()
SMTP_TLS_CHOICES = ("no", "try", "yes")
SMTP_DEFAULT_TLS = "try"
SMTP_DEFAULT_DEBUGLEVEL = 0
SMTP_DEFAULT_MESSAGE = f"Subject: Test{os.linesep * 2}Test"

log = logging.getLogger(__name__)


class SMTPHost(NamedTuple):
    name: str
    address: str
    port: int
    preference: int = 0


def hosts_discover(
    resolver: dns.DNSResolver, domain: str, port: int = SMTP_DEFAULT_PORT
) -> Iterable[SMTPHost]:
    hosts = []
    try:
        for mx in resolver.mx(domain):
            hosts.append(
                SMTPHost(
                    name=mx.name,
                    address=mx.address,
                    port=port,
                    preference=mx.preference,
                )
            )
    except dns.DNSNoRecords:
        address = resolver.a(domain)[0].address
        hosts.append(SMTPHost(name=domain, address=address, port=port))
    return hosts


def hosts_set(
    resolver: dns.DNSResolver, host: str, port=SMTP_DEFAULT_PORT
) -> Iterable[SMTPHost]:
    if util.is_ip_address(host):
        name = ""
        address = host
    else:
        name = host
        address = resolver.a(host)[0].address
    return [SMTPHost(name=name, address=address, port=port, preference=0)]


def send(
    host: SMTPHost,
    recipient: str,
    sender: str = SMTP_DEFAULT_SENDER,
    message: str = SMTP_DEFAULT_MESSAGE,
    timeout: int = SMTP_DEFAULT_TIMEOUT,
    helo: str = SMTP_DEFAULT_HELO,
    tls: str = SMTP_DEFAULT_TLS,
    auth_user: str = "",
    auth_pass: str = "",
    debuglevel: int = SMTP_DEFAULT_DEBUGLEVEL,
):

    log_host = f"{host.name}({host.address}):{host.port}"
    try:
        log.debug(f"Trying SMTP host: {log_host}")
        f = smtplib.SMTP_SSL if tls == 'yes' else smtplib.SMTP
        s = f(
            host=host.address, port=host.port, timeout=timeout, local_hostname=helo
        )
        s.set_debuglevel(debuglevel)
        s.ehlo_or_helo_if_needed()
        if (tls == "try" and s.has_extn("STARTTLS")):
            s.starttls()
        if auth_user or auth_pass:
            s.login(auth_user, auth_pass)
        headers = f"From: {sender}{os.linesep}"
        s.sendmail(sender, recipient, headers + message)
        s.quit()
        log.info(f"Message accepted by {log_host}")
    except smtplib.SMTPRecipientsRefused as e:
        raise SMTPPermanentError(exception_message(e.args)) from e
    except smtplib.SMTPResponseException as e:
        if e.smtp_code >= 500:
            exception = SMTPPermanentError
        else:
            exception = SMTPTemporaryError
        raise exception(f"{e.smtp_code} {e.smtp_error}") from e
    except smtplib.SMTPException as e:
        raise SMTPTemporaryError(exception_message(e.args)) from e
    # Base class for smtplib.SMTPConnectError, socket.timeout,
    # TimeoutError, etc. See: https://bugs.python.org/issue20903
    except OSError as e:
        msg = f"SMTP host failed: {log_host} Timeout={timeout}s"
        raise SMTPTemporaryError(msg) from e


def exception_message(args: tuple) -> str:
    if isinstance(args[0], str):
        return args[0]
    else:
        return ", ".join(f"{r[0]} {r[1].decode('utf-8')}" for r in args[0].values())


class SMTPException(Exception):
    pass


class SMTPTemporaryError(SMTPException):
    pass


class SMTPPermanentError(SMTPException):
    pass
