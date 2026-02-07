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
            "command -v steamos-readonly", shell=True, capture_output=True, check=False
        )
        return result.returncode == 0
    except Exception as e:
        logger.debug(f"Error checking steamos-readonly availability: {e}")
        return False


def is_path_writable(path: str) -> bool:
    """
    Check if a path (file or directory) is writable without needing readonly disable.

    For existing items:
    - If it's a directory: check the directory's writeability
    - If it's a file: check if we can write to it

    For non-existing items:
    - Check the first existing parent directory's writeability (since that's where it will be created)

    Returns True if writable, False if read-only.
    """
    check_path = path
    is_file_check = False

    if os.path.exists(path):
        # Path exists
        if os.path.isfile(path):
            # For files, we need to check if the file itself is writable
            is_file_check = True
            try:
                # Try to open the file in append mode (non-destructive test)
                with open(path, "a"):
                    pass
                return True
            except (OSError, IOError) as e:
                logger.debug(f"File is not writable: {path} - {str(e)}")
                return False
        elif os.path.isdir(path):
            # For directories, check the directory's writeability
            check_path = path
        else:
            # Other types (symlinks, devices, etc.)
            logger.warning(f"Path is not a file or directory: {path}")
            return False
    else:
        # Path doesn't exist - check the first existing parent directory
        logger.debug(f"Path does not exist: {path}, checking parent directories...")
        check_path = os.path.dirname(path)

        # Keep going up until we find an existing directory or reach root
        while check_path and not os.path.exists(check_path):
            check_path = os.path.dirname(check_path)

        # If we couldn't find any existing parent, we can't determine writeability
        if not check_path or not os.path.exists(check_path):
            logger.warning(f"Could not find any existing parent directory for: {path}")
            return False

        logger.debug(f"Checking parent directory instead: {check_path}")

    # Check if the directory is writable by trying to create a temporary file
    try:
        import tempfile

        with tempfile.NamedTemporaryFile(dir=check_path, delete=True):
            return True
    except (OSError, IOError) as e:
        logger.debug(f"Directory is not writable: {check_path} - {str(e)}")
        return False


def is_directory_writable(path: str) -> bool:
    """
    Check if a directory is writable without needing readonly disable.
    If the directory doesn't exist, check the first existing parent directory.
    Returns True if writable, False if read-only.

    NOTE: This function is for directories only. For files or mixed paths, use is_path_writable().
    """
    return is_path_writable(path)


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
        return True

    # Step 3: Try to disable readonly on SteamOS
    logger.info(
        f"SteamOS detected. Attempting to disable readonly mode for: {target_path}"
    )
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
        return True

    success, msg = run_command("steamos-readonly enable", use_sudo=True)
    return success


def is_locale_enabled(locale_code: str = "zh_CN.UTF-8") -> bool:
    """
    Check if a specific locale is enabled/installed on the system.
    Uses clean environment variables and precise parsing of locale -a output.

    Args:
        locale_code: Locale to check (e.g., 'zh_CN.UTF-8', 'ja_JP.UTF-8')

    Returns:
        True if locale is enabled, False otherwise
    """
    # 1. Prepare clean environment variables
    # Remove LD_LIBRARY_PATH to prevent loading wrong libc library in packaged environments
    clean_env = os.environ.copy()
    clean_env.pop("LD_LIBRARY_PATH", None)
    clean_env.pop("PYTHONHOME", None)
    clean_env.pop("PYTHONPATH", None)

    # 2. Define possible locale command paths (enhanced compatibility)
    cmd = "locale"
    if os.path.exists("/usr/bin/locale"):
        cmd = "/usr/bin/locale"

    try:
        # 3. Execute locale -a
        result = subprocess.run(
            [cmd, "-a"],
            env=clean_env,
            capture_output=True,
            text=True,
            timeout=5,
            check=False,
        )

        if result.returncode != 0:
            logger.error(
                f"locale -a command failed (exit code {result.returncode}): {result.stderr}"
            )
            return False

        # 4. Parse output
        # Split by lines, convert to lowercase and strip whitespace
        installed_locales = [
            line.strip().lower() for line in result.stdout.splitlines()
        ]

        # Extract the base locale identifier (e.g., 'zh_cn' from 'zh_CN.UTF-8')
        target = locale_code.split(".")[0].lower()

        for loc in installed_locales:
            # Match logic:
            # - loc == "zh_cn": exact match
            # - loc.startswith("zh_cn."): matches zh_cn.utf8, zh_cn.gbk, etc.
            # - loc.startswith("zh_cn@"): matches zh_cn.utf8@pinyin, etc.
            if (
                loc == target
                or loc.startswith(target + ".")
                or loc.startswith(target + "@")
            ):
                logger.debug(f"Detected valid locale: {loc} (target: {locale_code})")
                return True

        logger.debug(f"No {locale_code} locale found in system list.")
        return False

    except FileNotFoundError:
        logger.error("The 'locale' command was not found on this system.")
        return False
    except subprocess.TimeoutExpired:
        logger.error("Checking locale timed out.")
        return False
    except Exception as e:
        logger.error(f"Unexpected error checking locale: {str(e)}")
        return False


def is_zh_locale_enabled() -> bool:
    """
    Check if Chinese locale (zh_CN) is enabled on the system.
    This is a convenience function that calls is_locale_enabled with zh_CN.UTF-8.

    Deprecated: Use is_locale_enabled('zh_CN.UTF-8') instead.
    """
    return is_locale_enabled("zh_CN.UTF-8")


def is_fonts_installed() -> bool:
    """Check if fonts are already installed in user's ~/.fonts directory"""
    from src.config import Config

    font_dir = Config.get_fonts_dir()
    return os.path.isdir(font_dir) and len(os.listdir(font_dir)) > 0
