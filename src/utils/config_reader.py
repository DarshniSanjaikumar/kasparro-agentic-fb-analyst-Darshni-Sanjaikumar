import yaml
import os

class ConfigReader:
    def __init__(self, config_path: str = "../../config/config.yaml"):
        self.config_path = config_path
        self.config = self._load_config()

    def _load_config(self):
        if not os.path.exists(self.config_path):
            raise FileNotFoundError(f"Config file not found at {self.config_path}")

        with open(self.config_path, "r", encoding="utf-8") as f:
            config = yaml.safe_load(f)

        self._validate_config(config)
        return config

    def _validate_config(self, config):
        required_sections = ["data", "thresholds", "random"]
        for section in required_sections:
            if section not in config:
                raise ValueError(f"Missing required config section: {section}")

    def get(self, key: str, default=None):
        return self.config.get(key, default)

    def get_threshold(self, key: str):
        return self.config["thresholds"].get(key)

    def get_data_path(self):
        return self.config["data"]["path"]
