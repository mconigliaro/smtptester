import pytest

import smtptester.cli as cli


@pytest.mark.parametrize(
    "args, interface",
    [
        (("--log-level", "debug"), None),
        (("recipient@example.test",), "cli"),
        (("recipient@example.test", "--sender", "sender@example.test"), "cli"),
    ],
)
def test_parse(args, interface):
    assert isinstance(cli.parse(args, interface), cli.Options)


@pytest.mark.parametrize(
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
def test_options_list(options, redacted_keys, no_log_keys, expected):
    assert (
        cli.options_list(
            options.items(), redacted_keys=redacted_keys, no_log_keys=no_log_keys
        )
        == expected
    )
