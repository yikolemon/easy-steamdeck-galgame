"""
Chinese Fonts installer
"""

import os
import zipfile
import shutil
from typing import Tuple, Optional, Callable, Dict
from src.utils import (
    run_command,
    disable_readonly_if_needed,
    enable_readonly,
    is_fonts_installed,
)
from src.config import Config
from .base import BaseInstaller
from src.core.downloader import FontReleaseDownloader, GitHubAsset


class FontInstaller(BaseInstaller):
    """Chinese fonts installer"""

    def __init__(
        self, zip_path: Optional[str] = None, asset: Optional[GitHubAsset] = None
    ):
        self.zip_path: Optional[str] = zip_path
        self.asset: Optional[GitHubAsset] = asset
        self.fonts_dir = Config.get_fonts_dir()
        self.temp_dir = Config.get_temp_dir()
        self.downloader = FontReleaseDownloader()

    def install(
        self,
        zip_path: Optional[str] = None,
        progress_callback: Optional[Callable] = None,
    ) -> Tuple[bool, str]:
        if zip_path:
            self.zip_path = zip_path

        if not self.zip_path:
            return False, "ERROR: Font package path not specified"

        try:
            # Check if zip file exists
            if not os.path.isfile(self.zip_path):
                return False, f"ERROR: Font package not found: {self.zip_path}"

            # Check if readonly mode needs to be disabled
            print("[1/6] Checking if readonly mode needs to be disabled...")
            if not disable_readonly_if_needed(self.fonts_dir):
                return (
                    False,
                    "ERROR: Failed to disable readonly mode, please check permissions",
                )

            try:
                # Create temporary extraction directory (in user space, no sudo needed)
                if os.path.exists(self.temp_dir):
                    shutil.rmtree(self.temp_dir)
                os.makedirs(self.temp_dir, exist_ok=True)

                # Extract font package (to temp dir, no sudo needed)
                print("[2/6] Extracting font package...")
                with zipfile.ZipFile(self.zip_path, "r") as zip_ref:
                    zip_ref.extractall(self.temp_dir)

                # Create target directory with sudo
                print("[3/6] Creating fonts directory...")
                success, msg = run_command(f"mkdir -p {self.fonts_dir}", use_sudo=True)
                if not success:
                    return False, f"ERROR: Failed to create fonts directory: {msg}"

                # Copy font files with sudo, skip existing ones
                print("[4/6] Copying font files...")
                font_count = 0
                skip_count = 0

                for root, dirs, files in os.walk(self.temp_dir):
                    for file in files:
                        src_file = os.path.join(root, file)
                        dst_file = os.path.join(self.fonts_dir, file)

                        # Check if file exists (need to check with sudo)
                        check_result, _ = run_command(
                            f"test -f '{dst_file}'", use_sudo=True
                        )
                        if check_result:
                            print(f"[SKIP] File already exists: {file}")
                            skip_count += 1
                        else:
                            # Copy with sudo
                            success, msg = run_command(
                                f"cp '{src_file}' '{dst_file}'", use_sudo=True
                            )
                            if success:
                                print(f"[OK] Copied: {file}")
                                font_count += 1
                            else:
                                print(f"[ERROR] Failed to copy {file}: {msg}")

                # Update font cache
                print("[5/6] Updating font cache...")
                success, msg = run_command("fc-cache -fv", use_sudo=True)
                if not success:
                    # Font cache update failure does not affect final result
                    print(f"[WARN] Font cache update may have failed: {msg}")

                # Clean temporary directory (user space, no sudo needed)
                shutil.rmtree(self.temp_dir)

                # Re-enable readonly mode
                print("[6/6] Re-enabling SteamOS readonly mode...")
                if not enable_readonly():
                    return (
                        False,
                        f"WARNING: Failed to re-enable readonly mode, please manually run 'sudo steamos-readonly enable'\nBUT: Fonts installed successfully! Copied {font_count} files, skipped {skip_count} existing files",
                    )

                return (
                    True,
                    f"SUCCESS: Font installation completed!\nCopied {font_count} files\nSkipped {skip_count} existing files",
                )

            except Exception as e:
                enable_readonly()
                return False, f"ERROR: Installation failed: {str(e)}"

        except Exception as e:
            try:
                enable_readonly()
            except:
                pass
            return False, f"ERROR: Exception occurred: {str(e)}"

    def check_status(self) -> bool:
        """Check if fonts are installed"""
        return is_fonts_installed()

    def get_fonts_count(self) -> int:
        """Get count of installed fonts"""
        if os.path.isdir(self.fonts_dir):
            return len(os.listdir(self.fonts_dir))
        return 0


def setup_fonts(zip_path: str) -> Tuple[bool, str]:
    """Convenience function to install Chinese fonts"""
    installer = FontInstaller(zip_path)
    return installer.install()


def download_and_install_fonts(
    asset: GitHubAsset, progress_callback: Optional[Callable] = None
) -> Tuple[bool, str]:
    """
    Download and install fonts from GitHub Release

    Args:
        asset: The font resource to download
        progress_callback: Progress callback function

    Returns:
        (success_flag, detailed_message)
    """
    downloader = FontReleaseDownloader()

    # Download fonts
    print(f"[1/2] Downloading font package: {asset.name}...")
    success, msg, zip_path = downloader.download_font(asset, progress_callback)

    if not success:
        return False, msg

    # Install fonts
    print("\n[2/2] Starting font installation...")
    installer = FontInstaller(zip_path)
    return installer.install(progress_callback=progress_callback)


def list_available_fonts() -> Tuple[bool, list]:
    """
    List available font packages

    Returns:
        (success_flag, resources_list)
    """
    try:
        downloader = FontReleaseDownloader()
        assets = downloader.list_available_fonts()
        if assets:
            return True, assets
        else:
            return False, []
    except Exception as e:
        print(f"ERROR: Failed to get font list: {e}")
        return False, []


def get_fonts_release_info() -> Dict:
    """Get font Release information"""
    try:
        downloader = FontReleaseDownloader()
        return downloader.get_release_info()
    except Exception as e:
        print(f"ERROR: Failed to get Release info: {e}")
        return {}


def check_fonts_status() -> bool:
    """Convenience function to check font status"""
    installer = FontInstaller()
    return installer.check_status()


def get_fonts_count() -> int:
    """Convenience function to get installed fonts count"""
    installer = FontInstaller()
    return installer.get_fonts_count()
