"""
System operation utilities module
"""

import subprocess
import os
import logging
from typing import Optional
from .command import run_command

logger = logging.getLogger(__name__)


def is_directory_writable(path: str) -> bool:
    """
    Check if a directory is writable without needing readonly disable.
    Returns True if writable, False if read-only.
    """
    if not os.path.exists(path):
        logger.warning(f"Path does not exist: {path}")
        return False
    
    try:
        # Try to create a temporary file in the directory
        import tempfile
        with tempfile.NamedTemporaryFile(dir=path, delete=True):
            return True
    except (OSError, IOError) as e:
        logger.debug(f"Directory is not writable: {path} - {str(e)}")
        return False


def disable_readonly_if_needed(target_path: str) -> bool:
    """
    Disable SteamOS readonly mode only if the target path is not writable.
    This improves compatibility with non-SteamDeck systems like Arch Linux.
    
    Args:
        target_path: The target directory to check
        
    Returns:
        True if already writable or successfully disabled, False otherwise
    """
    if is_directory_writable(target_path):
        logger.info(f"Directory is already writable: {target_path}")
        return True
    
    logger.info(f"Directory is read-only, attempting to disable readonly mode: {target_path}")
    success, msg = run_command("steamos-readonly disable", use_sudo=True)
    
    if success:
        logger.info("Successfully disabled readonly mode")
        return True
    else:
        logger.error(f"Failed to disable readonly mode: {msg}")
        return False


def disable_readonly() -> bool:
    """Disable SteamOS readonly mode"""
    success, msg = run_command("steamos-readonly disable", use_sudo=True)
    return success


def enable_readonly() -> bool:
    """Enable SteamOS readonly mode"""
    success, msg = run_command("steamos-readonly enable", use_sudo=True)
    return success


def is_zh_locale_enabled() -> bool:
    """Check if zh_CN.UTF-8 locale is enabled"""
    try:
        result = subprocess.run(
            "locale -a | grep -q zh_CN",
            shell=True,
            capture_output=True,
            check=False
        )
        return result.returncode == 0
    except Exception as e:
        logger.error(f"Error checking locale: {str(e)}")
        return False


def is_fonts_installed() -> bool:
    """Check if fonts are already installed"""
    font_dir = "/usr/share/fonts/galgame"
    return os.path.isdir(font_dir) and len(os.listdir(font_dir)) > 0
