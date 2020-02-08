import argparse as ap
import smtptester as meta
import smtptester.dns as dns
import smtptester.smtp as smtp


class Options(ap.Namespace):
    pass


def parse(args=None, interface=None):
    parser = ap.ArgumentParser(epilog=f"{meta.COPYRIGHT} (http://{meta.DOMAIN})")
    parser.add_argument(
        "-v", "--version", action="version", version=f"{meta.NAME} {meta.VERSION}"
    )

    parser.add_argument(
        "--log-level",
        choices=("debug", "info", "warning", "error", "critical"),
        default="info",
    )

    if interface == "cli":
        parser.add_argument("recipient", help="recipient email address")
        parser.add_argument("--sender", default=smtp.SMTP_DEFAULT_SENDER)
        parser.add_argument("--message", default=smtp.SMTP_DEFAULT_MESSAGE)

        parser.add_argument("--dns-host")
        parser.add_argument("--dns-port", type=int, default=dns.DNS_DEFAULT_PORT)
        parser.add_argument("--dns-timeout", type=int, default=dns.DNS_DEFAULT_TIMEOUT)
        parser.add_argument("--dns-proto", choices=dns.DNS_PROTOCOL_CHOICES)

        parser.add_argument("--smtp-host")
        parser.add_argument("--smtp-port", type=int, default=smtp.SMTP_DEFAULT_PORT)
        parser.add_argument(
            "--smtp-timeout", type=int, default=smtp.SMTP_DEFAULT_TIMEOUT
        )
        parser.add_argument("--smtp-helo", default=smtp.SMTP_DEFAULT_HELO)
        parser.add_argument(
            "--smtp-tls", choices=smtp.SMTP_TLS_CHOICES, default=smtp.SMTP_DEFAULT_TLS
        )
        parser.add_argument("--smtp-auth-user")
        parser.add_argument("--smtp-auth-pass")

    elif interface == "gui":
        parser.add_argument(
            "--defaults", action="store_true", help="reset to default settings"
        )

    return parser.parse_args(args, namespace=Options())


def log(options, redacted_keys=[], no_log_keys=[]):
    options_list = []
    for k, v in sorted(options):
        if k not in no_log_keys:
            if v and k in redacted_keys:
                v = "<redacted>"
            options_list.append(f"{k}={repr(v)}")
    return ", ".join(options_list)
