from PyQt6.QtWidgets import QMainWindow, QVBoxLayout, QHBoxLayout, QPushButton, QListWidget, QWidget, QMessageBox, QProgressDialog, QTextEdit, QLabel
from PyQt6.QtCore import pyqtSlot, Qt

class MainWindow(QMainWindow):
    def __init__(self, config_manager, caddy_manager):
        super().__init__()
        self.config_manager = config_manager
        self.caddy_manager = caddy_manager
        self.setWindowTitle("Caddy Proxy Manager")
        self.setGeometry(100, 100, 600, 400)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        self.status_label = QLabel("Preparing...")
        layout.addWidget(self.status_label)

        self.domain_list = QListWidget()
        layout.addWidget(self.domain_list)

        button_layout = QHBoxLayout()
        self.add_button = QPushButton("Add Domain")
        self.add_button.clicked.connect(self.add_domain)
        self.add_button.setEnabled(False)
        button_layout.addWidget(self.add_button)

        self.remove_button = QPushButton("Remove Domain")
        self.remove_button.clicked.connect(self.remove_domain)
        self.remove_button.setEnabled(False)
        button_layout.addWidget(self.remove_button)

        self.check_status_button = QPushButton("Check Status")
        self.check_status_button.clicked.connect(self.check_status)
        self.check_status_button.setEnabled(False)
        button_layout.addWidget(self.check_status_button)

        layout.addLayout(button_layout)

        self.log_display = QTextEdit()
        self.log_display.setReadOnly(True)
        layout.addWidget(self.log_display)

        self.update_domain_list()

        self.caddy_manager.caddy_started.connect(self.on_caddy_started)
        self.caddy_manager.caddy_stopped.connect(self.on_caddy_stopped)
        self.caddy_manager.caddy_error.connect(self.on_caddy_error)
        self.caddy_manager.caddy_download_progress.connect(self.on_caddy_download_progress)
        self.caddy_manager.caddy_log.connect(self.on_caddy_log)
        self.caddy_manager.caddy_status.connect(self.on_caddy_status)

        self.download_progress_dialog = None

    @pyqtSlot()
    def add_domain(self):
        dialog = AddDomainDialog(self)
        if dialog.exec():
            domain, target = dialog.get_input()
            self.config_manager.add_domain(domain, target)
            self.caddy_manager.reload_caddy()
            self.update_domain_list()

    @pyqtSlot()
    def remove_domain(self):
        selected_items = self.domain_list.selectedItems()
        if selected_items:
            domain = selected_items[0].text().split(' -> ')[0]
            self.config_manager.remove_domain(domain)
            self.caddy_manager.reload_caddy()
            self.update_domain_list()

    def update_domain_list(self):
        self.domain_list.clear()
        domains = self.config_manager.get_domains()
        for domain, target in domains.items():
            self.domain_list.addItem(f"{domain} -> {target}")

    @pyqtSlot()
    def on_caddy_started(self):
        self.log_display.append("Caddy has started successfully.")
        self.status_label.setText("Caddy is running")
        self.add_button.setEnabled(True)
        self.remove_button.setEnabled(True)
        self.check_status_button.setEnabled(True)

    @pyqtSlot()
    def on_caddy_stopped(self):
        self.log_display.append("Caddy has stopped.")
        self.status_label.setText("Caddy is stopped")
        self.add_button.setEnabled(False)
        self.remove_button.setEnabled(False)
        self.check_status_button.setEnabled(False)

    @pyqtSlot(str)
    def on_caddy_error(self, error_message):
        self.log_display.append(f"Error: {error_message}")
        QMessageBox.critical(self, "Caddy Error", error_message)

    @pyqtSlot(int)
    def on_caddy_download_progress(self, progress):
        if self.download_progress_dialog is None and progress < 100:
            self.download_progress_dialog = QProgressDialog("Downloading Caddy...", "Cancel", 0, 100, self)
            self.download_progress_dialog.setWindowModality(Qt.WindowModality.WindowModal)
            self.download_progress_dialog.setAutoReset(False)
            self.download_progress_dialog.setAutoClose(False)
            self.download_progress_dialog.show()

        if self.download_progress_dialog:
            self.download_progress_dialog.setValue(progress)

        if progress == 100 and self.download_progress_dialog:
            self.download_progress_dialog.close()
            self.download_progress_dialog = None

    @pyqtSlot(str)
    def on_caddy_log(self, log_message):
        self.log_display.append(log_message)

    @pyqtSlot()
    def check_status(self):
        self.caddy_manager.check_status()

    @pyqtSlot(bool, str)
    def on_caddy_status(self, is_running, status_message):
        if is_running:
            QMessageBox.information(self, "Caddy Status", status_message)
        else:
            QMessageBox.warning(self, "Caddy Status", status_message)
        self.log_display.append(f"Status check: {status_message}")

    def closeEvent(self, event):
        self.caddy_manager.stop_caddy()
        super().closeEvent(event)