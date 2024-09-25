import json

class ConfigManager:
    def __init__(self, config_file='proxy_config.json'):
        self.config_file = config_file
        self.load_config()

    def load_config(self):
        try:
            with open(self.config_file, 'r') as f:
                self.config = json.load(f)
        except FileNotFoundError:
            self.config = {}

    def save_config(self):
        with open(self.config_file, 'w') as f:
            json.dump(self.config, f, indent=2)

    def add_domain(self, domain, target):
        self.config[domain] = target
        self.save_config()

    def remove_domain(self, domain):
        if domain in self.config:
            del self.config[domain]
            self.save_config()

    def get_domains(self):
        return self.config