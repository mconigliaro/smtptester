# SMTP Tester

As a consultant at a managed services provider, I spent a long time searching for a tool that would help me troubleshoot SMTP problems quickly and easily without having to resort to telnet. Finally, I gave up and wrote my own.

![](https://raw.githubusercontent.com/mconigliaro/smtptester/master/screenshots/smtptester-gui.png)

## Features

- Command-line and [graphical](https://www.qt.io/qt-for-python) user interfaces
- Ability to override all DNS and SMTP settings
- Support for SMTP authentication and TLS encryption

## Installation

    pip install smtptester

## Running the Application

    smtptester[-gui]

Use `--help` to see available options.

## Development

### Getting Started

    pip install pipenv
    pipenv install [--dev]
    pipenv shell
    ...

### Running Tests

    pytest

### Releases

1. Bump `VERSION` in [smtptester/\_\_init\_\_.py](smtptester/__init__.py)

1. Update [CHANGELOG.md](CHANGELOG.md)

1. Run `release` script:
    ```
    release <version>
    ```
