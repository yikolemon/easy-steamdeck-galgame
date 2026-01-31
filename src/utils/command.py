"""
Command execution utilities module
"""

import subprocess
import logging
from typing import Tuple

logger = logging.getLogger(__name__)


def run_command(cmd: str, use_sudo: bool = False) -> Tuple[bool, str]:
    """
    Execute shell command
    
    Args:
        cmd: Command to execute
        use_sudo: Whether to use sudo
        
    Returns:
        (success_flag, output/error_message)
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
        
        logger.info(f"Command: {cmd} | Return code: {result.returncode}")
        if output:
            logger.info(f"Output: {output[:100]}")
            
        return success, output
    
    except Exception as e:
        error_msg = f"Command execution error: {str(e)}"
        logger.error(error_msg)
        return False, error_msg
