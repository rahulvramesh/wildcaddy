import os

from PyQt6.QtWidgets import (
    QMainWindow, QVBoxLayout, QHBoxLayout, QPushButton, QListWidget, QWidget,
    QMessageBox, QProgressDialog, QTextEdit, QLabel, QMenu, QMenuBar, QDialog,
    QVBoxLayout, QLabel, QTextBrowser
)
from PyQt6.QtCore import pyqtSlot, Qt
from PyQt6.QtGui import QAction, QIcon
from .add_domain_dialog import AddDomainDialog
from .status_bar_app import StatusBarApp

class AboutDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("About Wild Caddy")
        self.setFixedSize(400, 300)

        layout = QVBoxLayout()

        title = QLabel("Wild Caddy")
        title.setStyleSheet("font-size: 18px; font-weight: bold;")
        layout.addWidget(title)

        version = QLabel("Version 1.0")
        layout.addWidget(version)

        description = QTextBrowser()
        description.setHtml("""
        <p>Wild Caddy is a user-friendly GUI application for managing Caddy server as a reverse proxy.</p>
        <p>Features:</p>
        <ul>
            <li>Easy domain management</li>
            <li>Automatic HTTPS with Let's Encrypt</li>
            <li>Real-time log viewing</li>
            <li>Caddy server status monitoring</li>
            <li>macOS menu bar integration</li>
        </ul>
        <p>Created by Your Name</p>
        <p>Licensed under MIT License</p>
        """)
        layout.addWidget(description)

        self.setLayout(layout)

class MainWindow(QMainWindow):
    def __init__(self, config_manager, caddy_manager):
        super().__init__()
        self.config_manager = config_manager
        self.caddy_manager = caddy_manager
        self.setWindowTitle("Wild Caddy")
        self.setGeometry(100, 100, 600, 400)

        self.app_icon = self.load_app_icon()
        self.setWindowIcon(self.app_icon)


        self.create_menu_bar()
        self.create_status_bar_app()

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

    def load_app_icon(self):
        icon_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'resources', 'wild_caddy_icon.png'))
        return QIcon(icon_path)

    def create_menu_bar(self):
        """Create and set up the menu bar."""
        menu_bar = QMenuBar(self)
        self.setMenuBar(menu_bar)

        # File menu
        file_menu = QMenu("File", self)
        menu_bar.addMenu(file_menu)

        exit_action = QAction("Exit", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # Domain menu
        domain_menu = QMenu("Domain", self)
        menu_bar.addMenu(domain_menu)

        add_domain_action = QAction("Add Domain", self)
        add_domain_action.triggered.connect(self.add_domain)
        domain_menu.addAction(add_domain_action)

        remove_domain_action = QAction("Remove Domain", self)
        remove_domain_action.triggered.connect(self.remove_domain)
        domain_menu.addAction(remove_domain_action)

        # Caddy menu
        caddy_menu = QMenu("Caddy", self)
        menu_bar.addMenu(caddy_menu)

        check_status_action = QAction("Check Status", self)
        check_status_action.triggered.connect(self.check_status)
        caddy_menu.addAction(check_status_action)

        restart_caddy_action = QAction("Restart Caddy", self)
        restart_caddy_action.triggered.connect(self.restart_caddy)
        caddy_menu.addAction(restart_caddy_action)

        # Help menu
        help_menu = QMenu("Help", self)
        menu_bar.addMenu(help_menu)

        about_action = QAction("About", self)
        about_action.triggered.connect(self.show_about_dialog)
        help_menu.addAction(about_action)

    def create_status_bar_app(self):
        self.status_bar_app = StatusBarApp(self.app_icon)
        self.status_bar_app.open_main_window.connect(self.show)
        self.status_bar_app.restart_caddy.connect(self.restart_caddy)


        # Set the window icon
        icon_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'resources', 'wild_caddy_icon.png'))
        self.setWindowIcon(QIcon(icon_path))

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

    @pyqtSlot()
    def restart_caddy(self):
        """Restart the Caddy server."""
        self.caddy_manager.reload_caddy()
        self.log_display.append("Restarting Caddy...")
        self.status_bar_app.show_message("Wild Caddy", "Caddy server restarted")

    @pyqtSlot()
    def show_about_dialog(self):
        """Show the About dialog."""
        about_dialog = AboutDialog(self)
        about_dialog.exec()

    def closeEvent(self, event):
        event.ignore()
        self.hide()
        self.status_bar_app.show_message("Wild Caddy", "Application minimized to menu bar")