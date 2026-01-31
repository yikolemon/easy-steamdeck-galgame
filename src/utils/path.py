"""
路径工具模块
"""

import os


def get_home_dir() -> str:
    """获取用户主目录"""
    return os.path.expanduser("~")


def get_config_dir() -> str:
    """获取配置目录，如不存在则创建"""
    config_dir = os.path.join(get_home_dir(), ".config", "steamdeck-galgame")
    os.makedirs(config_dir, exist_ok=True)
    return config_dir
