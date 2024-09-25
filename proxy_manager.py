import sys
import os
from PyQt6.QtWidgets import QApplication, QMessageBox
from gui.main_window import MainWindow
from config_manager import ConfigManager
from proxy_server import ProxyServer
from hosts_manager import HostsManager

def is_admin():
    try:
        return os.getuid() == 0
    except AttributeError:
        import ctypes
        return ctypes.windll.shell32.IsUserAnAdmin() != 0

def main():
    if not is_admin():
        QMessageBox.critical(None, "Error", "This application needs to be run with administrator privileges.")
        return

    app = QApplication(sys.argv)
    config_manager = ConfigManager()
    proxy_server = ProxyServer()
    hosts_manager = HostsManager()

    # Load existing configurations
    for domain, target in config_manager.get_domains().items():
        proxy_server.add_route(domain, target)
        hosts_manager.add_domain(domain)

    window = MainWindow(config_manager, proxy_server, hosts_manager)
    window.show()

    with hosts_manager:
        exit_code = app.exec()

    sys.exit(exit_code)

if __name__ == "__main__":
    main()