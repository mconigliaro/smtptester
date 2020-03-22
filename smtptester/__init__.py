import logging as log
import smtptester.dns as dns
import smtptester.smtp as smtp
import smtptester.opts as opts
import smtptester.util as util
import sys
import time as t

NAME = "SMTP Tester"
VERSION = "1.0.1"
AUTHOR = "Mike Conigliaro"
DOMAIN = "conigliaro.org"
COPYRIGHT = f"""Copyright (c) 2020 {AUTHOR}"""


class SMTPTester:
    def __init__(
        self,
        recipient,
        sender,
        message,
        dns_host,
        dns_port,
        dns_timeout,
        dns_proto,
        smtp_host,
        smtp_port,
        smtp_timeout,
        smtp_helo,
        smtp_tls,
        smtp_auth_user,
        smtp_auth_pass,
    ):

        log.info(f"Session started: {t.strftime('%Y-%m-%d %H:%M:%S %Z')}")
        options = opts.log(
            locals().items(),
            redacted_keys=["smtp_auth_user", "smtp_auth_pass"],
            no_log_keys=["self"],
        )
        log.debug(f"Options: {options}")

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
        try:
            hosts = []
            if self.smtp_host:
                hosts = smtp.hosts_set(
                    self.resolver, self.smtp_host, port=self.smtp_port
                )
            else:
                domain = util.parse_email_address(self.recipient).domain
                hosts = smtp.hosts_discover(self.resolver, domain, port=self.smtp_port)
            log_hosts = [f"{h.name}({h.address}):{h.port}" for h in hosts]
            log.info(f"Using SMTP hosts: {', '.join(log_hosts)}")
        except (dns.DNSConnectionError, dns.DNSNoDomain) as e:
            log.error(e)

        for host in hosts:
            try:
                log_level = log.getLogger().getEffectiveLevel()
                debuglevel = 1 if log_level == log.DEBUG else 0
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
        log.info(f"Session finished: {t.strftime('%Y-%m-%d %H:%M:%S %Z')}")
