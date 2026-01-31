"""
Path utilities module
"""

import os


def get_home_dir() -> str:
    """Get user home directory"""
    return os.path.expanduser("~")


def get_config_dir() -> str:
    """Get config directory, create if not exists"""
    config_dir = os.path.join(get_home_dir(), ".config", "steamdeck-galgame")
    os.makedirs(config_dir, exist_ok=True)
    return config_dir
