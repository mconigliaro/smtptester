# SMTP Tester

[![Continuous Integration](https://github.com/mconigliaro/smtptester/actions/workflows/ci.yml/badge.svg)](https://github.com/mconigliaro/smtptester/actions/workflows/ci.yml)

As a consultant at a managed services provider, I spent a long time searching for a tool that would help me troubleshoot SMTP problems quickly and easily without having to resort to telnet. Finally, I gave up and wrote my own.

![](https://raw.githubusercontent.com/mconigliaro/smtptester/master/screenshots/smtptester-gui.png)

## Features

- Command-line and [graphical](https://www.qt.io/qt-for-python) user interfaces
- Ability to override all DNS and SMTP settings
- Support for SMTP authentication and TLS encryption

## Installation

    pip install smtptester

## Running the Application

### With GUI

    smtptester-gui [options]

### CLI Only

    smtptester <options>

## Development

### Getting Started

    poetry install
    poetry shell
    ...

### Running Tests

    pytest

### Releases

1. Bump `version` in [pyproject.toml](pyproject.toml)
1. Update [CHANGELOG.md](CHANGELOG.md)
1. Run `make release`
