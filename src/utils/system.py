"""
系统操作工具模块
"""

import subprocess
import os
import logging
from typing import Optional
from .command import run_command

logger = logging.getLogger(__name__)


def disable_readonly() -> bool:
    """关闭 SteamOS 只读模式"""
    success, msg = run_command("steamos-readonly disable", use_sudo=True)
    return success


def enable_readonly() -> bool:
    """启用 SteamOS 只读模式"""
    success, msg = run_command("steamos-readonly enable", use_sudo=True)
    return success


def is_zh_locale_enabled() -> bool:
    """检查 zh_CN.UTF-8 locale 是否已启用"""
    try:
        result = subprocess.run(
            "locale -a | grep -q zh_CN",
            shell=True,
            capture_output=True,
            check=False
        )
        return result.returncode == 0
    except Exception as e:
        logger.error(f"检查 locale 异常: {str(e)}")
        return False


def is_fonts_installed() -> bool:
    """检查字体是否已安装"""
    font_dir = "/usr/share/fonts/galgame"
    return os.path.isdir(font_dir) and len(os.listdir(font_dir)) > 0
