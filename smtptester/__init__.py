import importlib.metadata
import logging
import sys
import time

import smtptester.dns as dns
import smtptester.smtp as smtp
import smtptester.cli as cli
import smtptester.util as util


META = importlib.metadata.metadata(__package__)

log = logging.getLogger(__name__)


class SMTPTester:
    def __init__(
        self,
        recipient: str,
        sender: str,
        message: str,
        dns_host: str,
        dns_port: int,
        dns_timeout: int,
        dns_proto: str,
        smtp_host: str,
        smtp_port: int,
        smtp_timeout: int,
        smtp_helo: str,
        smtp_tls: str,
        smtp_auth_user: str,
        smtp_auth_pass: str,
    ):
        log.info(f"Session started: {time.strftime('%Y-%m-%d %H:%M:%S %Z')}")
        options_list = cli.options_list(
            locals().items(),
            redacted_keys=["smtp_auth_user", "smtp_auth_pass"],
            no_log_keys=["self"],
        )
        log.debug(f"Options: {options_list}")

        self.recipient = recipient
        self.sender = sender
        self.message = message

        log.info(f"Sender: {self.sender}")
        log.info(f"Recipient: {self.recipient}")
        log.info(f"Message size: {sys.getsizeof(self.message)} bytes")

        self.resolver = dns.DNSResolver(
            host=dns_host, port=dns_port, timeout=dns_timeout, protocol=dns_proto
        )
        self.smtp_host = smtp_host
        self.smtp_port = smtp_port
        self.smtp_timeout = smtp_timeout
        self.smtp_helo = smtp_helo
        self.smtp_tls = smtp_tls
        self.smtp_auth_user = smtp_auth_user
        self.smtp_auth_pass = smtp_auth_pass

    def run(self):
        hosts = []
        try:
            if self.smtp_host:
                hosts = smtp.hosts_set(
                    self.resolver, self.smtp_host, port=self.smtp_port
                )
            else:
                domain = util.parse_email_address(self.recipient).domain
                hosts = smtp.hosts_discover(self.resolver, domain, port=self.smtp_port)
            log_hosts = [f"{h.name}({h.address}):{h.port}" for h in hosts]
            log.info(f"Using SMTP hosts: {', '.join(log_hosts)}")
        except dns.DNSException as e:
            log.error(e)

        for host in hosts:
            try:
                log_level = log.getEffectiveLevel()
                debuglevel = 1 if log_level == logging.DEBUG else 0
                smtp.send(
                    host,
                    self.recipient,
                    sender=self.sender,
                    message=self.message,
                    timeout=self.smtp_timeout,
                    helo=self.smtp_helo,
                    tls=self.smtp_tls,
                    auth_user=self.smtp_auth_user,
                    auth_pass=self.smtp_auth_pass,
                    debuglevel=debuglevel,
                )
                break
            except smtp.SMTPTemporaryError as e:
                log.warning(e)
                continue
            except smtp.SMTPPermanentError as e:
                log.error(e)
                break
            except KeyboardInterrupt:
                break
        else:
            log.error("No SMTP hosts available")
        log.info(f"Session finished: {time.strftime('%Y-%m-%d %H:%M:%S %Z')}")
