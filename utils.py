"""
工具函数模块 - SteamDeck 中文环境配置工具
"""

import subprocess
import os
import logging
from typing import Tuple, Optional

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def run_command(cmd: str, use_sudo: bool = False) -> Tuple[bool, str]:
    """
    执行 shell 命令
    
    Args:
        cmd: 要执行的命令
        use_sudo: 是否需要使用 sudo
        
    Returns:
        (成功标志, 输出/错误信息)
    """
    try:
        if use_sudo:
            cmd = f"sudo {cmd}"
        
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            check=False
        )
        
        output = result.stdout or result.stderr
        success = result.returncode == 0
        
        logger.info(f"命令: {cmd} | 返回码: {result.returncode}")
        if output:
            logger.info(f"输出: {output[:100]}")
            
        return success, output
    
    except Exception as e:
        error_msg = f"命令执行异常: {str(e)}"
        logger.error(error_msg)
        return False, error_msg


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


def get_home_dir() -> str:
    """获取用户主目录"""
    return os.path.expanduser("~")


def get_config_dir() -> str:
    """获取配置目录，如不存在则创建"""
    config_dir = os.path.join(get_home_dir(), ".config", "steamdeck-galgame")
    os.makedirs(config_dir, exist_ok=True)
    return config_dir


def get_zh_locale_command() -> str:
    """获取中文 locale 命令"""
    return "LANG=zh_CN.UTF-8 LC_ALL=zh_CN.UTF-8 LC_CTYPE=zh_CN.UTF-8 LC_MESSAGES=zh_CN.UTF-8 LANGUAGE=zh_CN %command%"
