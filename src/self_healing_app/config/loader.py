import os
import configparser

def load_config():
    """Loads and returns the global config."""
    base_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(base_dir, "config.ini")
    config = configparser.ConfigParser()
    config.read(config_path)
    print(f"Loaded config from {config_path}")
    return config
