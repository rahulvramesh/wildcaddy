import sys
import os
import subprocess
import platform
import requests
import threading
import time
from PyQt6.QtWidgets import QApplication, QMessageBox
from PyQt6.QtCore import QObject, pyqtSignal, QThread
from gui.main_window import MainWindow
from config_manager import ConfigManager
from hosts_manager import HostsManager
from utils import get_data_dir

class CaddyDownloader(QThread):
    progress = pyqtSignal(int)
    finished = pyqtSignal(str)
    error = pyqtSignal(str)

    def __init__(self, url, local_path):
        super().__init__()
        self.url = url
        self.local_path = local_path

    def run(self):
        try:
            response = requests.get(self.url, stream=True)
            response.raise_for_status()

            total_size = int(response.headers.get('content-length', 0))
            block_size = 1024  # 1 KB
            downloaded = 0

            self.progress.emit(0)  # Emit initial progress

            with open(self.local_path, 'wb') as f:
                for data in response.iter_content(block_size):
                    f.write(data)
                    downloaded += len(data)
                    progress = int((downloaded / total_size) * 100)
                    self.progress.emit(progress)

            os.chmod(self.local_path, 0o755)  # Make the file executable
            self.progress.emit(100)  # Emit final progress
            self.finished.emit(self.local_path)

        except requests.RequestException as e:
            self.error.emit(f"Failed to download Caddy: {str(e)}")

class CaddyManager(QObject):
    caddy_started = pyqtSignal()
    caddy_stopped = pyqtSignal()
    caddy_error = pyqtSignal(str)
    caddy_download_progress = pyqtSignal(int)
    caddy_log = pyqtSignal(str)
    caddy_status = pyqtSignal(bool, str)
    initialization_complete = pyqtSignal()  # New signal for initialization completion

    def __init__(self, config_manager):
        super().__init__()
        self.config_manager = config_manager
        self.caddy_process = None
        self.data_dir = get_data_dir()
        self.bins_folder = os.path.join(self.data_dir, 'bins')
        self.caddy_path = None
        self.log_thread = None
        self.stop_log_thread = False

    def initialize(self):
        if not os.path.exists(self.bins_folder):
            os.makedirs(self.bins_folder)

        caddy_filename = 'caddy.exe' if platform.system() == 'Windows' else 'caddy'
        self.caddy_path = os.path.join(self.bins_folder, caddy_filename)

        if not os.path.exists(self.caddy_path):
            self.download_caddy()
        else:
            self.caddy_download_progress.emit(100)
            self.start_caddy()

    def download_caddy(self):
        system = platform.system().lower()
        machine = platform.machine().lower()

        if system == 'darwin':
            url = f'https://caddyserver.com/api/download?os=darwin&arch={machine}'
        elif system == 'windows':
            url = f'https://caddyserver.com/api/download?os=windows&arch={machine}'
        elif system == 'linux':
            url = f'https://caddyserver.com/api/download?os=linux&arch={machine}'
        else:
            self.caddy_error.emit(f"Unsupported operating system: {system}")
            return

        self.downloader = CaddyDownloader(url, self.caddy_path)
        self.downloader.progress.connect(self.caddy_download_progress)
        self.downloader.finished.connect(self.on_download_finished)
        self.downloader.error.connect(self.caddy_error)
        self.downloader.start()

    def on_download_finished(self, path):
        self.caddy_path = path
        self.start_caddy()

    def generate_caddyfile(self):
        caddyfile_content = """
{
    admin off
    local_certs
}
"""
        for domain, target in self.config_manager.get_domains().items():
            caddyfile_content += f"""
{domain} {{
    tls internal
    reverse_proxy {target}
}}
"""
        caddyfile_path = os.path.join(self.data_dir, 'Caddyfile')
        with open(caddyfile_path, 'w') as f:
            f.write(caddyfile_content)
        return caddyfile_path

    def start_caddy(self):
        if self.caddy_path is None:
            self.caddy_error.emit("Cannot start Caddy: executable not found.")
            return

        caddyfile_path = self.generate_caddyfile()
        try:
            self.caddy_process = subprocess.Popen(
                [self.caddy_path, 'run', '--config', caddyfile_path],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines=True
            )
            # Wait a short time to check for immediate failures
            time.sleep(2)
            if self.caddy_process.poll() is not None:
                # Caddy stopped immediately, probably due to an error
                stdout, stderr = self.caddy_process.communicate()
                error_message = f"Caddy failed to start. Exit code: {self.caddy_process.returncode}\n"
                if stdout:
                    error_message += f"Stdout: {stdout}\n"
                if stderr:
                    error_message += f"Stderr: {stderr}"
                self.caddy_error.emit(error_message)
            else:
                self.caddy_started.emit()
                self.start_log_thread()
        except subprocess.SubprocessError as e:
            self.caddy_error.emit(f"Failed to start Caddy: {str(e)}")
        finally:
            self.initialization_complete.emit()  # Signal that initialization is complete

    def stop_caddy(self):
        if self.caddy_process:
            self.stop_log_thread = True
            if self.log_thread:
                self.log_thread.join()
            self.caddy_process.terminate()
            self.caddy_process.wait()
            self.caddy_process = None
            self.caddy_stopped.emit()

    def reload_caddy(self):
        self.stop_caddy()
        self.start_caddy()

    def start_log_thread(self):
        self.stop_log_thread = False
        self.log_thread = threading.Thread(target=self.log_output)
        self.log_thread.start()

    def log_output(self):
        while not self.stop_log_thread and self.caddy_process:
            output = self.caddy_process.stdout.readline()
            if output:
                self.caddy_log.emit(output.strip())
            error = self.caddy_process.stderr.readline()
            if error:
                self.caddy_log.emit(f"ERROR: {error.strip()}")

    def check_status(self):
        if not self.caddy_process:
            self.caddy_status.emit(False, "Caddy is not running")
            return

        if self.caddy_process.poll() is not None:
            self.caddy_status.emit(False, f"Caddy has stopped with return code {self.caddy_process.returncode}")
            return

        # Check if Caddy is responding to any of the configured domains
        domains = self.config_manager.get_domains().keys()
        if not domains:
            self.caddy_status.emit(False, "No domains configured")
            return

        for domain in domains:
            try:
                response = requests.get(f"https://{domain}", timeout=5, verify=False)
                if response.status_code == 200:
                    self.caddy_status.emit(True, f"Caddy is running and responding to HTTPS requests for {domain}")
                    return
                else:
                    self.caddy_status.emit(False, f"Caddy is running but returned status code {response.status_code} for {domain}")
                    return
            except requests.RequestException as e:
                continue  # Try the next domain if this one fails

        # If we've tried all domains and none worked
        self.caddy_status.emit(False, "Caddy is running but not responding to any configured domains")

def main():
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)  # Prevent app from quitting when main window is closed

    try:
        data_dir = get_data_dir()
        config_manager = ConfigManager()
        caddy_manager = CaddyManager(config_manager)
        hosts_manager = HostsManager()
    except OSError as e:
        QMessageBox.critical(None, "Error", f"Failed to create necessary directories: {str(e)}")
        return

    window = MainWindow(config_manager, caddy_manager, hosts_manager)

    def show_window():
        window.show()
        window.activateWindow()  # Bring the window to the front

    caddy_manager.initialization_complete.connect(show_window)

    try:
        caddy_manager.initialize()
    except Exception as e:
        QMessageBox.critical(None, "Error", f"Failed to initialize Caddy: {str(e)}")
        return

    exit_code = app.exec()

    caddy_manager.stop_caddy()
    sys.exit(exit_code)

if __name__ == "__main__":
    main()