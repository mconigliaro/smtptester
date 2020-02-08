import pytest as pt
import smtptester.opts as opts


@pt.mark.parametrize(
    "args, interface",
    [
        (("--log-level", "debug"), None),
        (("recipient@example.test",), "cli"),
        (("recipient@example.test", "--sender", "sender@example.test"), "cli"),
    ],
)
def test_parse(args, interface):
    assert isinstance(opts.parse(args, interface), opts.Options)


@pt.mark.parametrize(
    "options, redacted_keys, no_log_keys, expected",
    [
        (
            {"key3": "value3", "key2": "value2", "key1": "value1"},
            ["key1"],
            ["key2"],
            "key1='<redacted>', key3='value3'",
        )
    ],
)
def test_log(options, redacted_keys, no_log_keys, expected):
    assert (
        opts.log(options.items(), redacted_keys=redacted_keys, no_log_keys=no_log_keys)
        == expected
    )
