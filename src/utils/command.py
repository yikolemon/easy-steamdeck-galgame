"""
命令执行工具模块
"""

import subprocess
import logging
from typing import Tuple

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
