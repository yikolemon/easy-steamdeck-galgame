"""
Chinese Fonts installer
"""

import os
import zipfile
import shutil
from typing import Tuple, Optional, Callable, Dict
from src.utils import (
    run_command,
    run_script_as_root,
    is_fonts_installed,
    is_steamos_system,
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

            # Create temporary extraction directory (in user space, no sudo needed)
            print("[1/4] Preparing font package...")
            if os.path.exists(self.temp_dir):
                shutil.rmtree(self.temp_dir)
            os.makedirs(self.temp_dir, exist_ok=True)

            # Extract font package (to temp dir, no sudo needed)
            print("[2/4] Extracting font package...")
            with zipfile.ZipFile(self.zip_path, "r") as zip_ref:
                zip_ref.extractall(self.temp_dir)

            # Collect all font files to copy
            font_files = []
            for root, dirs, files in os.walk(self.temp_dir):
                for file in files:
                    src_file = os.path.join(root, file)
                    font_files.append((src_file, file))

            if not font_files:
                shutil.rmtree(self.temp_dir)
                return False, "ERROR: No font files found in the package"

            # Build a single script that does all privileged operations
            print("[3/4] Installing fonts (requires authentication)...")
            script_lines = []

            # Add SteamOS readonly disable if needed
            if is_steamos_system():
                script_lines.append("# Disable SteamOS readonly mode")
                script_lines.append("steamos-readonly disable || true")

            # Create fonts directory
            script_lines.append(f"# Create fonts directory")
            script_lines.append(f"mkdir -p '{self.fonts_dir}'")

            # Copy each font file (skip if exists)
            script_lines.append("# Copy font files")
            font_count = 0
            for src_file, filename in font_files:
                dst_file = os.path.join(self.fonts_dir, filename)
                # Use cp -n to skip existing files (no-clobber)
                script_lines.append(
                    f"cp -n '{src_file}' '{dst_file}' 2>/dev/null || true"
                )
                font_count += 1

            # Update font cache
            script_lines.append("# Update font cache")
            script_lines.append("fc-cache -fv >/dev/null 2>&1 || true")

            # Re-enable SteamOS readonly mode
            if is_steamos_system():
                script_lines.append("# Re-enable SteamOS readonly mode")
                script_lines.append("steamos-readonly enable || true")

            # Execute all commands with a single authentication prompt
            script_content = "\n".join(script_lines)
            success, msg = run_script_as_root(script_content)

            # Clean temporary directory (user space, no sudo needed)
            print("[4/4] Cleaning up...")
            shutil.rmtree(self.temp_dir)

            if not success:
                return False, f"ERROR: Font installation failed: {msg}"

            # Count actually installed fonts
            installed_count = 0
            if os.path.isdir(self.fonts_dir):
                installed_count = len(
                    [
                        f
                        for f in os.listdir(self.fonts_dir)
                        if os.path.isfile(os.path.join(self.fonts_dir, f))
                    ]
                )

            return (
                True,
                f"SUCCESS: Font installation completed!\nProcessed {font_count} files\nTotal installed fonts: {installed_count}",
            )

        except Exception as e:
            # Clean up on error
            try:
                if os.path.exists(self.temp_dir):
                    shutil.rmtree(self.temp_dir)
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
