import argparse
import logging
from typing import Iterable, Union

import smtptester
import smtptester.dns as dns
import smtptester.smtp as smtp


class Options(argparse.Namespace):
    pass


def parse(args: Union[list[str], None] = None, interface: str = "") -> Options:
    parser = argparse.ArgumentParser(
        add_help=False,
        epilog=f"{smtptester.META['Author']} <{smtptester.META['Author-email']}>",
    )
    parser.add_argument(
        "--help",
        action="help",
        help="show this help message and exit",
    )
    parser.add_argument(
        "-v",
        "--version",
        action="version",
        version=f"{smtptester.META['Name']} {smtptester.META['Version']}",
    )

    parser.add_argument(
        "-l",
        "--log-level",
        choices=("debug", "info", "warning", "error", "critical"),
        default="info",
    )

    if interface == "cli":
        parser.add_argument("recipient", help="recipient email address")
        parser.add_argument("-s", "--sender", default=smtp.SMTP_DEFAULT_SENDER)
        parser.add_argument("-m", "--message", default=smtp.SMTP_DEFAULT_MESSAGE)

        parser.add_argument("-d", "--dns-host")
        parser.add_argument("--dns-port", type=int, default=dns.DNS_DEFAULT_PORT)
        parser.add_argument("--dns-timeout", type=int, default=dns.DNS_DEFAULT_TIMEOUT)
        parser.add_argument("--dns-proto", choices=dns.DNS_PROTOCOL_CHOICES)

        parser.add_argument("-h", "--smtp-host")
        parser.add_argument("--smtp-port", type=int, default=smtp.SMTP_DEFAULT_PORT)
        parser.add_argument(
            "--smtp-timeout", type=int, default=smtp.SMTP_DEFAULT_TIMEOUT
        )
        parser.add_argument("--smtp-helo", default=smtp.SMTP_DEFAULT_HELO)
        parser.add_argument(
            "--smtp-tls", choices=smtp.SMTP_TLS_CHOICES, default=smtp.SMTP_DEFAULT_TLS
        )
        parser.add_argument("-u", "--smtp-auth-user")
        parser.add_argument("-p", "--smtp-auth-pass")

    elif interface == "gui":
        parser.add_argument(
            "--defaults", action="store_true", help="reset to default settings"
        )

    return parser.parse_args(args, namespace=Options())


def options_list(
    options: Iterable[tuple], redacted_keys: list = [], no_log_keys: list = []
) -> str:
    options_list = []
    for k, v in sorted(options):
        if k not in no_log_keys:
            if v and k in redacted_keys:
                v = "<redacted>"
            options_list.append(f"{k}={repr(v)}")
    return ", ".join(options_list)


def main():
    o = parse(interface="cli")

    log_format = "[%(levelname)s] %(message)s"
    log_level = getattr(logging, o.log_level.upper())
    logging.basicConfig(format=log_format, level=log_level)

    smtptester.SMTPTester(
        recipient=o.recipient,
        sender=o.sender,
        message=o.message,
        dns_host=o.dns_host,
        dns_port=o.dns_port,
        dns_timeout=o.dns_timeout,
        dns_proto=o.dns_proto,
        smtp_host=o.smtp_host,
        smtp_port=o.smtp_port,
        smtp_timeout=o.smtp_timeout,
        smtp_helo=o.smtp_helo,
        smtp_tls=o.smtp_tls,
        smtp_auth_user=o.smtp_auth_user,
        smtp_auth_pass=o.smtp_auth_pass,
    ).run()
