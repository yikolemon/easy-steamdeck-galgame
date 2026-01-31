"""
Locale installer - supports multiple languages
"""

import subprocess
from typing import Tuple
from src.utils import run_command, disable_readonly_if_needed, enable_readonly, is_locale_enabled
from .base import BaseInstaller


class LocaleInstaller(BaseInstaller):
    """Locale installer for multiple languages"""
    
    def __init__(self, locale_code: str = 'zh_CN.UTF-8'):
        """
        Initialize locale installer
        
        Args:
            locale_code: Locale to install (e.g., 'zh_CN.UTF-8', 'ja_JP.UTF-8')
        """
        self.locale_code = locale_code
        # Extract locale identifier for sed command (e.g., 'zh_CN.UTF-8' or 'ja_JP.UTF-8')
        self.locale_identifier = locale_code
    
    def install(self) -> Tuple[bool, str]:
        """
        Install locale
        
        Returns:
            (success_flag, detailed_message)
        """
        try:
            # 1. Check if system needs readonly disable
            print(f"[1/5] Checking if readonly mode needs to be disabled...")
            target_path = "/etc/locale.gen"
            if not disable_readonly_if_needed(target_path):
                return False, "ERROR: Failed to disable readonly mode, please check permissions"
            
            # 2. Initialize pacman keys
            print("[2/5] Initializing pacman keys...")
            success, msg = run_command("pacman-key --init", use_sudo=True)
            if not success:
                enable_readonly()
                return False, f"ERROR: pacman-key --init failed: {msg}"
            
            success, msg = run_command("pacman-key --populate archlinux", use_sudo=True)
            if not success:
                enable_readonly()
                return False, f"ERROR: pacman-key --populate failed: {msg}"
            
            # 3. Check and enable locale
            print(f"[3/5] Enabling locale ({self.locale_code})...")
            # The locale.gen file format is: #en_US.UTF-8 UTF-8
            # We need to match and uncomment the exact locale
            locale_pattern = self.locale_identifier.replace('.', '\\.')  # Escape dots for regex
            check_result = subprocess.run(
                f"grep '^#{locale_pattern} UTF-8' /etc/locale.gen",
                shell=True,
                capture_output=True,
                check=False
            )
            
            if check_result.returncode == 0:
                # Found commented line, need to uncomment it
                success, msg = run_command(
                    f"sed -i 's/^#{locale_pattern} UTF-8/{locale_pattern} UTF-8/' /etc/locale.gen",
                    use_sudo=True
                )
                if not success:
                    enable_readonly()
                    return False, f"ERROR: Failed to modify locale.gen: {msg}"
            else:
                print(f"[WARN] {self.locale_code} already enabled or not found, skipping modification")
            
            # 4. Generate locale
            print("[4/5] Generating locale...")
            success, msg = run_command("locale-gen", use_sudo=True)
            if not success:
                enable_readonly()
                return False, f"ERROR: locale-gen failed: {msg}"
            
            # 5. Re-enable readonly mode
            print("[5/5] Re-enabling SteamOS readonly mode...")
            if not enable_readonly():
                return True, "WARNING: Failed to re-enable readonly mode, please manually run 'sudo steamos-readonly enable'"
            
            return True, f"SUCCESS: {self.locale_code} locale installation completed!"
        
        except Exception as e:
            try:
                enable_readonly()
            except:
                pass
            return False, f"ERROR: Exception occurred: {str(e)}"
    
    def check_status(self) -> bool:
        """Check if locale is installed"""
        return is_locale_enabled(self.locale_code)


def setup_locale(locale_code: str = 'zh_CN.UTF-8') -> Tuple[bool, str]:
    """
    Convenience function to install locale
    
    Args:
        locale_code: Locale to install (default: 'zh_CN.UTF-8')
    """
    installer = LocaleInstaller(locale_code)
    return installer.install()


def check_locale_status(locale_code: str = 'zh_CN.UTF-8') -> bool:
    """
    Convenience function to check locale status
    
    Args:
        locale_code: Locale to check (default: 'zh_CN.UTF-8')
    """
    installer = LocaleInstaller(locale_code)
    return installer.check_status()
