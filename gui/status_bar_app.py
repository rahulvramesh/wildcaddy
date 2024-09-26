from PyQt6.QtWidgets import QApplication, QMenu, QSystemTrayIcon
from PyQt6.QtGui import QIcon, QAction
from PyQt6.QtCore import Qt, QObject, pyqtSignal

class StatusBarApp(QObject):
    open_main_window = pyqtSignal()
    restart_caddy = pyqtSignal()

    def __init__(self, icon):
        super().__init__()
        self.icon = icon
        self.tray_icon = None
        self.create_tray_icon()

    def create_tray_icon(self):
        self.tray_icon = QSystemTrayIcon(self.icon)

        # Create the tray menu
        tray_menu = QMenu()

        open_action = QAction("Open Wild Caddy", self)
        open_action.triggered.connect(self.open_main_window.emit)
        tray_menu.addAction(open_action)

        restart_action = QAction("Restart Caddy", self)
        restart_action.triggered.connect(self.restart_caddy.emit)
        tray_menu.addAction(restart_action)

        quit_action = QAction("Quit", self)
        quit_action.triggered.connect(QApplication.instance().quit)
        tray_menu.addAction(quit_action)

        # Set the tray's menu
        self.tray_icon.setContextMenu(tray_menu)

        # Make the tray icon visible
        self.tray_icon.setVisible(True)

    def show_message(self, title, message):
        self.tray_icon.showMessage(title, message, QSystemTrayIcon.MessageIcon.Information)