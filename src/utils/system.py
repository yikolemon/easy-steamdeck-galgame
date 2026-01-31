"""
System operation utilities module
"""

import subprocess
import os
import logging
from typing import Optional
from .command import run_command

logger = logging.getLogger(__name__)


def is_steamos_system() -> bool:
    """
    Detect if this is a SteamOS system by checking for steamos-readonly command.
    Returns True if steamos-readonly is available, False otherwise.
    """
    try:
        result = subprocess.run(
            "command -v steamos-readonly",
            shell=True,
            capture_output=True,
            check=False
        )
        return result.returncode == 0
    except Exception as e:
        logger.debug(f"Error checking steamos-readonly availability: {e}")
        return False


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
    
    Behavior:
    1. If target directory is writable -> return True (no action needed)
    2. If SteamOS system available -> try to disable readonly
    3. If not SteamOS -> return False (read-only permission error, needs sudo)
    
    Args:
        target_path: The target directory to check
        
    Returns:
        True if already writable or successfully disabled, False otherwise
    """
    # Step 1: Check if directory is already writable
    if is_directory_writable(target_path):
        logger.info(f"Directory is already writable: {target_path}")
        return True
    
    # Step 2: Check if this is a SteamOS system
    if not is_steamos_system():
        logger.warning(
            f"Directory is read-only and steamos-readonly command not available. "
            f"This is likely Arch Linux or non-SteamOS system. "
            f"Try running with sudo: sudo {target_path}"
        )
        return False
    
    # Step 3: Try to disable readonly on SteamOS
    logger.info(f"SteamOS detected. Attempting to disable readonly mode for: {target_path}")
    success, msg = run_command("steamos-readonly disable", use_sudo=True)
    
    if success:
        logger.info("Successfully disabled readonly mode")
        # Verify that directory is now writable
        if is_directory_writable(target_path):
            return True
        else:
            logger.error("Directory still not writable after disabling readonly mode")
            return False
    else:
        logger.error(f"Failed to disable readonly mode: {msg}")
        return False


def disable_readonly() -> bool:
    """
    Disable SteamOS readonly mode
    Returns False if steamos-readonly command is not available
    """
    if not is_steamos_system():
        logger.warning("steamos-readonly command not available (not a SteamOS system)")
        return False
    
    success, msg = run_command("steamos-readonly disable", use_sudo=True)
    return success


def enable_readonly() -> bool:
    """
    Enable SteamOS readonly mode
    Returns False if steamos-readonly command is not available
    """
    if not is_steamos_system():
        logger.warning("steamos-readonly command not available (not a SteamOS system)")
        return False
    
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
