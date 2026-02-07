"""
Locale installer - supports multiple languages
"""

from typing import Tuple, Optional, Callable
from src.utils import (
    run_script_as_root,
    is_locale_enabled,
    is_steamos_system,
)
from .base import BaseInstaller


class LocaleInstaller(BaseInstaller):
    """Locale installer for multiple languages"""

    def __init__(self, locale_code: str = "zh_CN.UTF-8"):
        """
        Initialize locale installer

        Args:
            locale_code: Locale to install (e.g., 'zh_CN.UTF-8', 'ja_JP.UTF-8')
        """
        self.locale_code = locale_code
        self.locale_identifier = locale_code

    def install(
        self, log_callback: Optional[Callable[[str], None]] = None
    ) -> Tuple[bool, str]:
        """
        Install locale

        Args:
            log_callback: Optional callback function to receive log messages

        Returns:
            (success_flag, detailed_message)
        """

        def log(message: str):
            """Log message to callback or print"""
            if log_callback:
                log_callback(message)
            else:
                print(message)

        try:
            log(f"[1/4] Preparing locale installation ({self.locale_code})...")

            # Build installation script
            script_lines = []

            # Add SteamOS readonly disable if needed
            if is_steamos_system():
                log("[2/4] Disabling SteamOS readonly mode...")
                script_lines.append("# Disable SteamOS readonly mode")
                script_lines.append("steamos-readonly disable || true")

            # Initialize pacman keys
            log("[2/4] Initializing pacman keys...")
            script_lines.append("# Initialize pacman keys")
            script_lines.append("pacman-key --init")
            script_lines.append("pacman-key --populate archlinux")

            # Enable locale in locale.gen
            log(f"[3/4] Enabling locale ({self.locale_code})...")
            locale_pattern = self.locale_identifier.replace(".", "\\.")
            script_lines.append(f"# Enable {self.locale_code} locale")
            script_lines.append(
                f"sed -i 's/^#{locale_pattern} UTF-8/{locale_pattern} UTF-8/' /etc/locale.gen || true"
            )

            # Generate locale
            log("[4/4] Generating locale...")
            script_lines.append("# Generate locale")
            script_lines.append("locale-gen")

            # Re-enable SteamOS readonly mode
            if is_steamos_system():
                script_lines.append("# Re-enable SteamOS readonly mode")
                script_lines.append("steamos-readonly enable || true")

            # Execute all commands with a single authentication prompt
            log("Executing installation script (requires authentication)...")
            script_content = "\n".join(script_lines)

            def script_output_callback(line: str):
                """Forward script output to log callback"""
                log(f"  {line}")

            success, msg = run_script_as_root(
                script_content, output_callback=script_output_callback
            )

            if not success:
                log(f"[ERROR] Installation failed: {msg}")
                return False, f"ERROR: Locale installation failed: {msg}"

            # Verify installation
            if is_locale_enabled(self.locale_code):
                log(f"[OK] {self.locale_code} locale installed successfully!")
                return (
                    True,
                    f"SUCCESS: {self.locale_code} locale installation completed!",
                )
            else:
                log(f"[WARN] Installation completed but locale verification failed")
                return (
                    True,
                    f"WARNING: Installation completed but {self.locale_code} locale verification failed. Please reboot and check.",
                )

        except Exception as e:
            log(f"[ERROR] Exception occurred: {str(e)}")
            return False, f"ERROR: Exception occurred: {str(e)}"

    def check_status(self) -> bool:
        """Check if locale is installed"""
        return is_locale_enabled(self.locale_code)


def setup_locale(
    locale_code: str = "zh_CN.UTF-8",
    log_callback: Optional[Callable[[str], None]] = None,
) -> Tuple[bool, str]:
    """
    Convenience function to install locale

    Args:
        locale_code: Locale to install (default: 'zh_CN.UTF-8')
        log_callback: Optional callback function to receive log messages
    """
    installer = LocaleInstaller(locale_code)
    return installer.install(log_callback=log_callback)


def check_locale_status(locale_code: str = "zh_CN.UTF-8") -> bool:
    """
    Convenience function to check locale status

    Args:
        locale_code: Locale to check (default: 'zh_CN.UTF-8')
    """
    installer = LocaleInstaller(locale_code)
    return installer.check_status()
