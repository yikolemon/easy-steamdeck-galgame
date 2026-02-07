"""
Chinese Fonts installer
"""

import os
import zipfile
import tarfile
import shutil
import subprocess
from typing import Tuple, Optional, Callable, Dict, List
from src.utils import (
    run_command,
    run_script_as_root,
    is_fonts_installed,
    is_steamos_system,
)
from src.config import Config
from .base import BaseInstaller
from src.core.downloader import FontReleaseDownloader, GitHubAsset

# Supported font file extensions
FONT_EXTENSIONS = (".ttf", ".otf", ".ttc", ".woff", ".woff2")

# Supported archive extensions
ARCHIVE_EXTENSIONS = (".zip", ".7z", ".tar", ".tar.gz", ".tgz", ".tar.bz2", ".tar.xz")


class FontInstaller(BaseInstaller):
    """Chinese fonts installer - supports zip, 7z, tar, and direct font files"""

    def __init__(
        self, font_path: Optional[str] = None, asset: Optional[GitHubAsset] = None
    ):
        self.font_path: Optional[str] = font_path  # Can be archive or font file
        self.asset: Optional[GitHubAsset] = asset
        self.fonts_dir = Config.get_fonts_dir()
        self.temp_dir = Config.get_temp_dir()
        self.downloader = FontReleaseDownloader()

    def _is_font_file(self, path: str) -> bool:
        """Check if path is a font file"""
        return path.lower().endswith(FONT_EXTENSIONS)

    def _is_archive_file(self, path: str) -> bool:
        """Check if path is a supported archive file"""
        lower_path = path.lower()
        return any(lower_path.endswith(ext) for ext in ARCHIVE_EXTENSIONS)

    def _is_7z_available(self) -> bool:
        """Check if 7z command is available"""
        return shutil.which("7z") is not None or shutil.which("7za") is not None

    def _extract_archive(self, archive_path: str, extract_dir: str) -> Tuple[bool, str]:
        """
        Extract archive to directory based on file type

        Returns:
            (success, error_message)
        """
        lower_path = archive_path.lower()

        try:
            if lower_path.endswith(".zip"):
                with zipfile.ZipFile(archive_path, "r") as zip_ref:
                    zip_ref.extractall(extract_dir)
                return True, ""

            elif lower_path.endswith(".7z"):
                if not self._is_7z_available():
                    return (
                        False,
                        "7z command not found. Please install p7zip: sudo pacman -S p7zip",
                    )
                # Try 7z first, then 7za
                cmd = "7z" if shutil.which("7z") else "7za"
                result = subprocess.run(
                    [cmd, "x", archive_path, f"-o{extract_dir}", "-y"],
                    capture_output=True,
                    text=True,
                )
                if result.returncode != 0:
                    return False, f"7z extraction failed: {result.stderr}"
                return True, ""

            elif lower_path.endswith(
                (".tar", ".tar.gz", ".tgz", ".tar.bz2", ".tar.xz")
            ):
                with tarfile.open(archive_path, "r:*") as tar_ref:
                    tar_ref.extractall(extract_dir)
                return True, ""

            else:
                return False, f"Unsupported archive format: {archive_path}"

        except Exception as e:
            return False, f"Extraction error: {str(e)}"

    def _collect_font_files(self, source_dir: str) -> List[Tuple[str, str]]:
        """
        Collect all font files from directory recursively

        Returns:
            List of (source_path, filename) tuples
        """
        font_files = []
        for root, dirs, files in os.walk(source_dir):
            for file in files:
                if self._is_font_file(file):
                    src_file = os.path.join(root, file)
                    font_files.append((src_file, file))
        return font_files

    def install(
        self,
        font_path: Optional[str] = None,
        progress_callback: Optional[Callable] = None,
    ) -> Tuple[bool, str]:
        """
        Install fonts from archive or font file

        Supports:
        - ZIP archives (.zip)
        - 7-Zip archives (.7z)
        - Tar archives (.tar, .tar.gz, .tgz, .tar.bz2, .tar.xz)
        - Direct font files (.ttf, .otf, .ttc, .woff, .woff2)
        """
        if font_path:
            self.font_path = font_path

        if not self.font_path:
            return False, "ERROR: Font file or archive path not specified"

        try:
            # Check if file exists
            if not os.path.isfile(self.font_path):
                return False, f"ERROR: File not found: {self.font_path}"

            font_files = []

            # Handle direct font file
            if self._is_font_file(self.font_path):
                print("[1/3] Processing font file...")
                font_files = [(self.font_path, os.path.basename(self.font_path))]
                use_temp_dir = False

            # Handle archive file
            elif self._is_archive_file(self.font_path):
                print("[1/4] Preparing font archive...")

                # Create temporary extraction directory
                if os.path.exists(self.temp_dir):
                    shutil.rmtree(self.temp_dir)
                os.makedirs(self.temp_dir, exist_ok=True)
                use_temp_dir = True

                # Extract archive
                print("[2/4] Extracting font archive...")
                success, error = self._extract_archive(self.font_path, self.temp_dir)
                if not success:
                    shutil.rmtree(self.temp_dir)
                    return False, f"ERROR: {error}"

                # Collect font files
                font_files = self._collect_font_files(self.temp_dir)

                if not font_files:
                    shutil.rmtree(self.temp_dir)
                    return False, "ERROR: No font files found in the archive"

            else:
                return False, f"ERROR: Unsupported file format: {self.font_path}"

            # Build installation script
            step = "[2/3]" if not use_temp_dir else "[3/4]"
            print(f"{step} Installing fonts (requires authentication)...")

            script_lines = []

            # Add SteamOS readonly disable if needed
            if is_steamos_system():
                script_lines.append("# Disable SteamOS readonly mode")
                script_lines.append("steamos-readonly disable || true")

            # Create fonts directory
            script_lines.append("# Create fonts directory")
            script_lines.append(f"mkdir -p '{self.fonts_dir}'")

            # Copy each font file
            script_lines.append("# Copy font files")
            font_count = 0
            for src_file, filename in font_files:
                dst_file = os.path.join(self.fonts_dir, filename)
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

            # Execute script
            script_content = "\n".join(script_lines)
            success, msg = run_script_as_root(script_content)

            # Clean up temp directory
            step = "[3/3]" if not use_temp_dir else "[4/4]"
            print(f"{step} Cleaning up...")
            if use_temp_dir and os.path.exists(self.temp_dir):
                shutil.rmtree(self.temp_dir)

            if not success:
                return False, f"ERROR: Font installation failed: {msg}"

            # Count installed fonts
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
                f"SUCCESS: Font installation completed!\nProcessed {font_count} font file(s)\nTotal installed fonts: {installed_count}",
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


def setup_fonts(font_path: str) -> Tuple[bool, str]:
    """
    Convenience function to install fonts

    Args:
        font_path: Path to font file or archive (zip, 7z, tar, ttf, otf, etc.)
    """
    installer = FontInstaller(font_path)
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
