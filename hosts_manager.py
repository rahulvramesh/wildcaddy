import os
import tempfile
import shutil

class HostsManager:
    def __init__(self):
        self.hosts_path = '/etc/hosts' if os.name != 'nt' else r'C:\Windows\System32\drivers\etc\hosts'
        self.temp_hosts_path = os.path.join(tempfile.gettempdir(), 'temp_hosts')
        self.original_content = None
        self.managed_domains = set()

    def backup_hosts(self):
        with open(self.hosts_path, 'r') as hosts_file:
            self.original_content = hosts_file.read()

    def restore_hosts(self):
        if self.original_content is not None:
            with open(self.hosts_path, 'w') as hosts_file:
                hosts_file.write(self.original_content)

    def add_domain(self, domain):
        self.managed_domains.add(domain)
        self.update_hosts()

    def remove_domain(self, domain):
        self.managed_domains.discard(domain)
        self.update_hosts()

    def update_hosts(self):
        with open(self.hosts_path, 'r') as hosts_file:
            content = hosts_file.readlines()

        with open(self.temp_hosts_path, 'w') as temp_file:
            for line in content:
                if not any(domain in line for domain in self.managed_domains):
                    temp_file.write(line)

            for domain in self.managed_domains:
                temp_file.write(f'127.0.0.1 {domain}\n')

        # Use elevated privileges to replace the hosts file
        if os.name == 'nt':  # Windows
            import ctypes
            import win32con
            MOVEFILE_DELAY_UNTIL_REBOOT = 0x4
            ctypes.windll.kernel32.MoveFileExW(self.temp_hosts_path, self.hosts_path, MOVEFILE_DELAY_UNTIL_REBOOT)
        else:  # macOS and Linux
            os.system(f'sudo cp {self.temp_hosts_path} {self.hosts_path}')

    def __enter__(self):
        self.backup_hosts()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.restore_hosts()