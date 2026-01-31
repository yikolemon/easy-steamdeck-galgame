"""
Chinese Locale installer
"""

import subprocess
from typing import Tuple
from src.utils import run_command, disable_readonly_if_needed, enable_readonly, is_zh_locale_enabled
from .base import BaseInstaller


class LocaleInstaller(BaseInstaller):
    """Chinese locale installer"""
    
    def install(self) -> Tuple[bool, str]:
        """
        Install Chinese locale
        
        Returns:
            (success_flag, detailed_message)
        """
        try:
            # 1. Check if system needs readonly disable
            print("[1/5] Checking if readonly mode needs to be disabled...")
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
            
            # 3. Check and enable zh_CN.UTF-8 locale
            print("[3/5] Enabling Chinese locale (zh_CN.UTF-8)...")
            check_result = subprocess.run(
                "grep '^#zh_CN.UTF-8 UTF-8' /etc/locale.gen",
                shell=True,
                capture_output=True,
                check=False
            )
            
            if check_result.returncode == 0:
                # Found commented line, need to uncomment it
                success, msg = run_command(
                    "sed -i 's/^#zh_CN.UTF-8 UTF-8/zh_CN.UTF-8 UTF-8/' /etc/locale.gen",
                    use_sudo=True
                )
                if not success:
                    enable_readonly()
                    return False, f"ERROR: Failed to modify locale.gen: {msg}"
            else:
                print("[WARN] zh_CN.UTF-8 already enabled or not found, skipping modification")
            
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
            
            return True, "SUCCESS: Chinese locale installation completed!"
        
        except Exception as e:
            try:
                enable_readonly()
            except:
                pass
            return False, f"ERROR: Exception occurred: {str(e)}"
    
    def check_status(self) -> bool:
        """Check if Chinese locale is installed"""
        return is_zh_locale_enabled()


def setup_locale() -> Tuple[bool, str]:
    """Convenience function to install Chinese locale"""
    installer = LocaleInstaller()
    return installer.install()


def check_locale_status() -> bool:
    """Convenience function to check Chinese locale status"""
    installer = LocaleInstaller()
    return installer.check_status()
