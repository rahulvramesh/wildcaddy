from PyQt6.QtWidgets import QMainWindow, QVBoxLayout, QHBoxLayout, QPushButton, QListWidget, QWidget
from PyQt6.QtCore import pyqtSlot
from .add_domain_dialog import AddDomainDialog

class MainWindow(QMainWindow):
    def __init__(self, config_manager, proxy_server, hosts_manager):
        super().__init__()
        self.config_manager = config_manager
        self.proxy_server = proxy_server
        self.hosts_manager = hosts_manager
        self.setWindowTitle("Proxy Manager")
        self.setGeometry(100, 100, 400, 300)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        self.domain_list = QListWidget()
        layout.addWidget(self.domain_list)

        button_layout = QHBoxLayout()
        add_button = QPushButton("Add Domain")
        add_button.clicked.connect(self.add_domain)
        button_layout.addWidget(add_button)

        remove_button = QPushButton("Remove Domain")
        remove_button.clicked.connect(self.remove_domain)
        button_layout.addWidget(remove_button)

        layout.addLayout(button_layout)

        self.update_domain_list()

        self.proxy_server.server_started.connect(self.on_server_started)
        self.proxy_server.start()

    @pyqtSlot()
    def add_domain(self):
        dialog = AddDomainDialog(self)
        if dialog.exec():
            domain, target = dialog.get_input()
            self.config_manager.add_domain(domain, target)
            self.proxy_server.add_route(domain, target)
            self.hosts_manager.add_domain(domain)
            self.update_domain_list()

    @pyqtSlot()
    def remove_domain(self):
        selected_items = self.domain_list.selectedItems()
        if selected_items:
            domain = selected_items[0].text().split(' -> ')[0]
            self.config_manager.remove_domain(domain)
            self.proxy_server.remove_route(domain)
            self.hosts_manager.remove_domain(domain)
            self.update_domain_list()

    def update_domain_list(self):
        self.domain_list.clear()
        domains = self.config_manager.get_domains()
        for domain, target in domains.items():
            self.domain_list.addItem(f"{domain} -> {target}")

    def closeEvent(self, event):
        self.proxy_server.stop()
        self.proxy_server.wait()
        super().closeEvent(event)

    @pyqtSlot()
    def on_server_started(self):
        print("GUI notified: Server has started")