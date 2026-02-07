"""
Command execution utilities module
"""

import os
import shutil
import subprocess
import logging
from typing import Tuple

logger = logging.getLogger(__name__)


def is_pkexec_available() -> bool:
    """
    Check if pkexec is available on the system.
    pkexec provides a graphical authentication dialog via polkit.
    """
    return shutil.which("pkexec") is not None


def get_clean_env() -> dict:
    """
    Get a clean environment for subprocess execution.
    Removes PyInstaller-specific environment variables that may cause
    library conflicts with system commands.
    """
    env = os.environ.copy()

    # Remove PyInstaller-specific variables that can cause library conflicts
    vars_to_remove = [
        "LD_LIBRARY_PATH",  # Can cause symbol lookup errors
        "LD_PRELOAD",  # Can interfere with system libraries
        "_MEIPASS2",  # PyInstaller internal
        "PYTHONPATH",  # May point to bundled packages
    ]

    for var in vars_to_remove:
        env.pop(var, None)

    return env


def run_command(cmd: str, use_sudo: bool = False) -> Tuple[bool, str]:
    """
    Execute shell command

    Args:
        cmd: Command to execute
        use_sudo: Whether to use elevated privileges (uses pkexec for GUI dialog, falls back to sudo)

    Returns:
        (success_flag, output/error_message)
    """
    try:
        if use_sudo:
            # Use pkexec for graphical authentication dialog if available
            # pkexec provides a polkit-based GUI password prompt
            if is_pkexec_available():
                # pkexec doesn't support shell syntax directly, so we use sh -c
                # Escape single quotes in the command for safe shell execution
                escaped_cmd = cmd.replace("'", "'\"'\"'")
                cmd = f"pkexec sh -c '{escaped_cmd}'"
                logger.info("Using pkexec for privilege escalation (graphical dialog)")
            else:
                # Fallback to sudo for terminal-based authentication
                cmd = f"sudo {cmd}"
                logger.info("pkexec not available, falling back to sudo")

        # Use clean environment to avoid PyInstaller library conflicts
        clean_env = get_clean_env()

        result = subprocess.run(
            cmd, shell=True, capture_output=True, text=True, check=False, env=clean_env
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
