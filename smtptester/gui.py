import logging as log
import os
import PySide2.QtCore as qtc
import PySide2.QtGui as qtg
import PySide2.QtWidgets as qtw
import smtptester as meta
import smtptester.dns as dns
import smtptester.smtp as smtp
import signal as sig
import sys

PORT_RANGE = (0, 65535)
LOG_DEFAULT_COLOR = "black"
LOG_COLORS = {
    "DEBUG": "darkGray",
    "INFO": "black",
    "WARNING": "darkMagenta",
    "ERROR": "darkRed",
    "CRITICAL": "darkRed",
}
ICON_PATH = os.path.join(os.path.dirname(__file__), "data", "smtptester.png")


class Worker(qtc.QThread):
    def run(self):
        self.task.run()


class LogSignal(qtc.QObject):
    signal = qtc.Signal(log.LogRecord)


class GuiHandler(log.Handler):
    def __init__(self, slot_function):
        super().__init__()
        self.log_signal = LogSignal()
        self.log_signal.signal.connect(slot_function)

    def emit(self, record):
        self.format(record)
        self.log_signal.signal.emit(record)


class CentralWidget(qtw.QWidget):
    def __init__(self, app, options):
        super().__init__()

        app.aboutToQuit.connect(self.quit)
        log.basicConfig(
            handlers=[GuiHandler(self.log_results)],
            format="%(message)s",
            level=getattr(log, options.log_level.upper()),
        )

        self.worker = Worker()
        self.worker.started.connect(self.working_mode_enable)
        self.worker.finished.connect(self.working_mode_disable)

        self.settings = qtc.QSettings()

        self._widgets()
        self._layout()

    def _widgets(self):
        self.sender = qtw.QLineEdit()
        self.sender.setText(self.settings.value("sender", smtp.SMTP_DEFAULT_SENDER))

        self.recipient = qtw.QLineEdit()
        self.recipient.setText(self.settings.value("recipient"))

        self.message = qtw.QTextEdit()
        self.message.setText(self.settings.value("message", smtp.SMTP_DEFAULT_MESSAGE))

        self.dns_set_host = qtw.QCheckBox("Specify DNS Server")
        self.dns_set_host.setCheckState(
            self.check_state_map(
                self.settings.value("dns_set_host", qtc.Qt.CheckState.Unchecked)
            )
        )
        self.dns_set_host.stateChanged.connect(self.toggle_dns_set_host)

        self.dns_host = qtw.QLineEdit()
        self.dns_host.setText(self.settings.value("dns_host"))

        self.dns_port = qtw.QSpinBox()
        self.dns_port.setRange(*PORT_RANGE)
        self.dns_port.setValue(self.settings.value("dns_port", dns.DNS_DEFAULT_PORT))

        self.dns_timeout = qtw.QSpinBox()
        self.dns_timeout.setValue(
            self.settings.value("dns_timeout", dns.DNS_DEFAULT_TIMEOUT)
        )

        self.dns_use_tcp = qtw.QCheckBox("Use TCP")
        self.dns_use_tcp.setCheckState(
            self.check_state_map(
                self.settings.value("dns_use_tcp", qtc.Qt.CheckState.Unchecked)
            )
        )

        self.smtp_set_host = qtw.QCheckBox("Specify SMTP Server")
        self.smtp_set_host.setCheckState(
            self.check_state_map(
                self.settings.value("smtp_set_host", qtc.Qt.CheckState.Unchecked)
            )
        )
        self.smtp_set_host.stateChanged.connect(self.toggle_smtp_set_host)

        self.smtp_host = qtw.QLineEdit()
        self.smtp_host.setText(self.settings.value("smtp_host"))

        self.smtp_port = qtw.QSpinBox()
        self.smtp_port.setRange(*PORT_RANGE)
        self.smtp_port.setValue(
            self.settings.value("smtp_port", smtp.SMTP_DEFAULT_PORT)
        )

        self.smtp_timeout = qtw.QSpinBox()
        self.smtp_timeout.setValue(
            self.settings.value("smtp_timeout", smtp.SMTP_DEFAULT_TIMEOUT)
        )

        self.smtp_helo = qtw.QLineEdit()
        self.smtp_helo.setText(self.settings.value("smtp_helo", smtp.SMTP_DEFAULT_HELO))

        self.smtp_use_auth = qtw.QCheckBox("Use Authentication")
        self.smtp_use_auth.setCheckState(
            self.check_state_map(
                self.settings.value("smtp_use_auth", qtc.Qt.CheckState.Unchecked)
            )
        )
        self.smtp_use_auth.stateChanged.connect(self.toggle_smtp_use_auth)

        self.smtp_auth_user = qtw.QLineEdit()
        self.smtp_auth_user.setEchoMode(qtw.QLineEdit.Password)
        self.smtp_auth_user.setText(self.settings.value("smtp_auth_user"))

        self.smtp_auth_pass = qtw.QLineEdit()
        self.smtp_auth_pass.setEchoMode(qtw.QLineEdit.Password)
        self.smtp_auth_pass.setText(self.settings.value("smtp_auth_pass"))

        self.smtp_use_tls = qtw.QCheckBox("Use TLS Encryption")
        self.smtp_use_tls.setTristate(True)
        self.smtp_use_tls.setCheckState(
            self.check_state_map(
                self.settings.value("smtp_use_tls", qtc.Qt.CheckState.PartiallyChecked)
            )
        )

        self.button_cancel = qtw.QPushButton("Cancel")
        self.button_cancel.clicked.connect(self.terminate_worker)

        self.button_ok = qtw.QPushButton("OK")
        self.button_ok.clicked.connect(self.start_worker)

        self.results = qtw.QTextEdit()
        self.results.setReadOnly(True)

    def _layout(self):
        message_gbox = qtw.QGroupBox("Message")
        message_vbox = qtw.QVBoxLayout()
        message_vbox.addWidget(qtw.QLabel("From:"))
        message_vbox.addWidget(self.sender)
        message_vbox.addWidget(qtw.QLabel("To:"))
        message_vbox.addWidget(self.recipient)
        message_vbox.addWidget(qtw.QLabel("Body:"))
        message_vbox.addWidget(self.message)
        message_gbox.setLayout(message_vbox)

        dns_gbox = qtw.QGroupBox("DNS")
        dns_grid = qtw.QGridLayout()
        dns_grid.addWidget(self.dns_set_host, 0, 0, 1, 3)
        dns_grid.addWidget(qtw.QLabel("Host:"), 1, 0)
        dns_grid.addWidget(qtw.QLabel("Port:"), 1, 1)
        dns_grid.addWidget(qtw.QLabel("Timeout:"), 1, 2)
        dns_grid.addWidget(self.dns_host, 2, 0)
        dns_grid.addWidget(self.dns_port, 2, 1)
        dns_grid.addWidget(self.dns_timeout, 2, 2)
        dns_grid.addWidget(self.dns_use_tcp, 3, 0, 1, 3)
        dns_gbox.setLayout(dns_grid)
        self.toggle_dns_set_host()

        smtp_gbox = qtw.QGroupBox("SMTP")
        smtp_grid = qtw.QGridLayout()
        smtp_grid.addWidget(self.smtp_set_host, 0, 0, 1, 3)
        smtp_grid.addWidget(qtw.QLabel("Host:"), 1, 0)
        smtp_grid.addWidget(qtw.QLabel("Port:"), 1, 1)
        smtp_grid.addWidget(qtw.QLabel("Timeout:"), 1, 2)
        smtp_grid.addWidget(self.smtp_host, 2, 0)
        smtp_grid.addWidget(self.smtp_port, 2, 1)
        smtp_grid.addWidget(self.smtp_timeout, 2, 2)
        smtp_grid.addWidget(qtw.QLabel("HELO/EHLO:"), 3, 0, 1, 3)
        smtp_grid.addWidget(self.smtp_helo, 4, 0, 1, 3)
        smtp_gbox.setLayout(smtp_grid)
        self.toggle_smtp_set_host()

        security_gbox = qtw.QGroupBox("Security")
        security_vbox = qtw.QVBoxLayout()
        security_vbox.addWidget(self.smtp_use_auth)
        security_vbox.addWidget(qtw.QLabel("Username:"))
        security_vbox.addWidget(self.smtp_auth_user)
        security_vbox.addWidget(qtw.QLabel("Password:"))
        security_vbox.addWidget(self.smtp_auth_pass)
        security_vbox.addWidget(self.smtp_use_tls)
        security_gbox.setLayout(security_vbox)
        self.toggle_smtp_use_auth()

        button_gbox = qtw.QGroupBox()
        button_hbox = qtw.QHBoxLayout()
        button_hbox.addWidget(self.button_cancel)
        button_hbox.addWidget(self.button_ok)
        button_gbox.setLayout(button_hbox)
        self.working_mode_disable()

        results_gbox = qtw.QGroupBox("Results")
        results_vbox = qtw.QVBoxLayout()
        results_vbox.addWidget(self.results)
        results_gbox.setLayout(results_vbox)

        main_grid = qtw.QGridLayout()
        main_grid.addWidget(message_gbox, 0, 0, 4, 1)
        main_grid.addWidget(dns_gbox, 0, 1)
        main_grid.addWidget(smtp_gbox, 1, 1)
        main_grid.addWidget(security_gbox, 2, 1)
        main_grid.addWidget(button_gbox, 3, 1)
        main_grid.addWidget(results_gbox, 4, 0, 1, 2)
        self.setLayout(main_grid)

    def check_state_map(self, obj):
        if isinstance(obj, int):
            return (
                qtc.Qt.CheckState.Unchecked,
                qtc.Qt.CheckState.PartiallyChecked,
                qtc.Qt.CheckState.Checked,
            )[obj]
        else:
            return int(obj)

    @qtc.Slot(log.LogRecord)
    def log_results(self, record):
        color = LOG_COLORS.get(record.levelname, LOG_DEFAULT_COLOR)
        self.results.setTextColor(qtg.QColor(color))
        self.results.append(record.message)

    @qtc.Slot()
    def toggle_dns_set_host(self):
        check_state = self.dns_set_host.checkState()
        enabled = True if check_state == qtc.Qt.CheckState.Checked else False
        widgets = [self.dns_host, self.dns_port, self.dns_use_tcp]
        for w in widgets:
            w.setEnabled(enabled)
        if not enabled:
            self.dns_host.clear()
            self.dns_port.setValue(dns.DNS_DEFAULT_PORT)
            self.dns_use_tcp.setCheckState(qtc.Qt.CheckState.Unchecked)

    @qtc.Slot()
    def toggle_smtp_set_host(self):
        check_state = self.smtp_set_host.checkState()
        enabled = True if check_state == qtc.Qt.CheckState.Checked else False
        widgets = [self.smtp_host, self.smtp_port]
        for w in widgets:
            w.setEnabled(enabled)
        if not enabled:
            self.smtp_host.clear()
            self.smtp_port.setValue(smtp.SMTP_DEFAULT_PORT)

    @qtc.Slot()
    def toggle_smtp_use_auth(self):
        check_state = self.smtp_use_auth.checkState()
        enabled = True if check_state == qtc.Qt.CheckState.Checked else False
        widgets = [self.smtp_auth_user, self.smtp_auth_pass]
        for w in widgets:
            w.setEnabled(enabled)
        if not enabled:
            for w in widgets:
                w.clear()

    @qtc.Slot()
    def working_mode_enable(self):
        log.debug(f"Worker thread started")
        self.button_cancel.setEnabled(True)
        self.button_ok.setEnabled(False)

    @qtc.Slot()
    def working_mode_disable(self):
        if self.worker.isFinished():
            log.debug(f"Worker thread finished")
        self.button_cancel.setEnabled(False)
        self.button_ok.setEnabled(True)

    @qtc.Slot()
    def start_worker(self):
        self.results.clear()

        dns_proto = "tcp" if self.dns_use_tcp.isChecked() else "udp"

        smtp_tls = {
            qtc.Qt.CheckState.Checked: "yes",
            qtc.Qt.CheckState.PartiallyChecked: "try",
            qtc.Qt.CheckState.Unchecked: "no",
        }[self.smtp_use_tls.checkState()]

        self.worker.task = meta.SMTPTester(
            recipient=self.recipient.text(),
            sender=self.sender.text(),
            message=self.message.toPlainText(),
            dns_host=self.dns_host.text(),
            dns_port=self.dns_port.value(),
            dns_timeout=self.dns_timeout.value(),
            dns_proto=dns_proto,
            smtp_host=self.smtp_host.text(),
            smtp_port=self.smtp_port.value(),
            smtp_timeout=self.smtp_timeout.value(),
            smtp_helo=self.smtp_helo.text(),
            smtp_tls=smtp_tls,
            smtp_auth_user=self.smtp_auth_user.text(),
            smtp_auth_pass=self.smtp_auth_pass.text(),
        )

        self.worker.start()

    @qtc.Slot()
    def terminate_worker(self):
        if self.worker.isRunning():
            log.debug(f"Terminating worker thread")
            self.worker.terminate()
            self.worker.wait()

    @qtc.Slot()
    def quit(self):
        self.settings.setValue("sender", self.sender.text())
        self.settings.setValue("recipient", self.recipient.text())
        self.settings.setValue("message", self.message.toPlainText())

        self.settings.setValue(
            "dns_set_host", self.check_state_map(self.dns_set_host.checkState())
        )
        self.settings.setValue("dns_host", self.dns_host.text())
        self.settings.setValue("dns_port", self.dns_port.value())
        self.settings.setValue("dns_timeout", self.dns_timeout.value())
        self.settings.setValue(
            "dns_use_tcp", self.check_state_map(self.dns_use_tcp.checkState())
        )

        self.settings.setValue(
            "smtp_set_host", self.check_state_map(self.smtp_set_host.checkState())
        )
        self.settings.setValue("smtp_host", self.smtp_host.text())
        self.settings.setValue("smtp_port", self.smtp_port.value())
        self.settings.setValue("smtp_timeout", self.smtp_timeout.value())
        self.settings.setValue("smtp_helo", self.smtp_helo.text())

        self.settings.setValue(
            "smtp_use_auth", self.check_state_map(self.smtp_use_auth.checkState())
        )
        self.settings.setValue(
            "smtp_use_tls", self.check_state_map(self.smtp_use_tls.checkState())
        )
        self.settings.setValue("smtp_auth_user", self.smtp_auth_user.text())
        self.settings.setValue("smtp_auth_pass", self.smtp_auth_pass.text())

        self.terminate_worker()


class MainWindow(qtw.QMainWindow):
    def __init__(self, app, options):
        super().__init__()

        self.setWindowTitle(meta.NAME)
        self.setWindowIcon(qtg.QIcon(ICON_PATH))

        self.settings = qtc.QSettings()
        if options.defaults:
            self.settings.clear()
        else:
            self.restoreGeometry(self.settings.value("window_geometry"))
            self.restoreState(self.settings.value("window_state"))

        self.menu_bar = self.menuBar()
        self._file_menu()
        self._help_menu()

        self.setCentralWidget(CentralWidget(app, options))

    def _file_menu(self):
        menu = self.menu_bar.addMenu("&File")

        exit = qtw.QAction("E&xit", self)
        exit.triggered.connect(self.close)
        menu.addAction(exit)

    def _help_menu(self):
        menu = self.menu_bar.addMenu("&Help")

        about = qtw.QAction("&About", self)
        about.triggered.connect(self.about)
        menu.addAction(about)

        about_qt = qtw.QAction("About Qt", self)
        about_qt.triggered.connect(self.about_qt)
        menu.addAction(about_qt)

    @qtc.Slot()
    def about(self):
        qtw.QMessageBox.about(
            self,
            meta.NAME,
            f"{meta.NAME} {meta.VERSION}{os.linesep}{meta.COPYRIGHT}{os.linesep}http://{meta.DOMAIN}",
        )

    @qtc.Slot()
    def about_qt(self):
        qtw.QMessageBox.aboutQt(self)

    def closeEvent(self, event):
        self.settings.setValue("window_geometry", self.saveGeometry())
        self.settings.setValue("window_state", self.saveState())


def run(options):
    app = qtw.QApplication()
    app.setOrganizationName(meta.AUTHOR)
    app.setOrganizationDomain(meta.DOMAIN)
    app.setApplicationName(meta.NAME)

    window = MainWindow(app, options)
    window.show()

    sig.signal(sig.SIGINT, sig.SIG_DFL)  # Handle Ctrl+C
    sys.exit(app.exec_())
