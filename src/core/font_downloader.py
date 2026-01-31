"""
GitHub Release download manager
"""

import requests
import os
import json
import sys
from typing import List, Dict, Optional, Tuple, BinaryIO
from pathlib import Path
import logging
import io

logger = logging.getLogger(__name__)


class GitHubAsset:
    """GitHub Release asset object"""
    
    def __init__(self, name: str, size: int, download_url: str):
        self.name = name
        self.size = size
        self.download_url = download_url
    
    def get_size_mb(self) -> float:
        """Get file size in MB"""
        return self.size / (1024 * 1024)
    
    def __repr__(self) -> str:
        return f"{self.name} ({self.get_size_mb():.1f} MB)"


class ProgressWriter:
    """Real-time progress writer that bypasses buffering"""
    
    def __init__(self):
        self.last_output = ""
    
    def update(self, downloaded: int, total: int, filename: str = ""):
        """Update progress display with unbuffered output"""
        if total <= 0:
            return
        
        percent = (downloaded / total) * 100
        mb_downloaded = downloaded / (1024 * 1024)
        mb_total = total / (1024 * 1024)
        
        # Format: [████████░░░░░░░░░░] 45.2% 23.5/52.1 MB
        bar_length = 30
        filled = int(bar_length * downloaded / total)
        bar = "█" * filled + "░" * (bar_length - filled)
        
        progress_line = f"\r[{bar}] {percent:5.1f}% {mb_downloaded:6.1f}/{mb_total:6.1f} MB"
        
        # Write directly to raw stdout/stderr to bypass buffering
        try:
            # Try using os.write for maximum unbuffered output
            os.write(2, (progress_line).encode('utf-8', errors='ignore'))
        except:
            # Fallback to sys.stderr
            sys.stderr.write(progress_line)
            sys.stderr.flush()
    
    def finish(self):
        """Clear progress line"""
        try:
            os.write(2, b"\n")
        except:
            sys.stderr.write("\n")
            sys.stderr.flush()


class GitHubReleaseManager:
    """GitHub Release download manager"""
    
    def __init__(self, owner: str, repo: str, timeout: int = 10):
        """
        Initialize
        
        Args:
            owner: GitHub username
            repo: Repository name
            timeout: Request timeout in seconds
        """
        self.owner = owner
        self.repo = repo
        self.timeout = timeout
        self.api_url = f"https://api.github.com/repos/{owner}/{repo}"
    
    def get_latest_release(self) -> Optional[Dict]:
        """
        Get latest release information
        
        Returns:
            Release information dictionary, None on failure
        """
        try:
            url = f"{self.api_url}/releases/latest"
            response = requests.get(url, timeout=self.timeout)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            logger.error(f"Failed to get release info: {e}")
            return None
    
    def get_release_assets(self) -> List[GitHubAsset]:
        """
        Get all assets from latest release
        
        Returns:
            List of assets
        """
        release = self.get_latest_release()
        if not release:
            return []
        
        assets = []
        for asset in release.get("assets", []):
            ga = GitHubAsset(
                name=asset["name"],
                size=asset["size"],
                download_url=asset["browser_download_url"]
            )
            assets.append(ga)
        
        return assets
    
    def get_release_info(self) -> Dict:
        """
        Get release information
        
        Returns:
            Dictionary with version, description, etc.
        """
        release = self.get_latest_release()
        if not release:
            return {}
        
        return {
            "version": release.get("tag_name", "unknown"),
            "name": release.get("name", ""),
            "description": release.get("body", ""),
            "published_at": release.get("published_at", ""),
            "assets_count": len(release.get("assets", []))
        }
    
    def download_asset(
        self,
        asset: GitHubAsset,
        dest_path: str,
        progress_callback=None
    ) -> Tuple[bool, str]:
        """
        Download asset with real-time unbuffered progress display
        
        Args:
            asset: Asset to download
            dest_path: Destination path
            progress_callback: Legacy progress callback function (downloaded, total)
            
        Returns:
            (success_flag, message)
        """
        try:
            # Create target directory
            os.makedirs(os.path.dirname(dest_path), exist_ok=True)
            
            logger.info(f"Starting download: {asset.name}")
            
            # Send request with streaming enabled
            response = requests.get(
                asset.download_url,
                timeout=self.timeout,
                stream=True
            )
            response.raise_for_status()
            
            # Get file size
            total_size = int(response.headers.get('content-length', 0))
            
            if total_size == 0:
                logger.warning("Content-Length header not provided, downloading without progress")
            
            # Create progress writer
            progress_writer = ProgressWriter()
            
            # Download file with very small chunks for real-time updates
            downloaded = 0
            chunk_size = 64 * 1024  # 64KB chunks for more frequent updates
            
            with open(dest_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=chunk_size):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        
                        # Update progress display in real-time
                        if total_size > 0:
                            progress_writer.update(downloaded, total_size, asset.name)
                        
                        # Call legacy progress callback if provided
                        if progress_callback:
                            progress_callback(downloaded, total_size)
            
            # Clear progress line
            progress_writer.finish()
            
            logger.info(f"Download complete: {dest_path}")
            return True, f"Download complete: {asset.name}"
        
        except requests.RequestException as e:
            error_msg = f"Download failed: {str(e)}"
            logger.error(error_msg)
            return False, error_msg
        except IOError as e:
            error_msg = f"Failed to save file: {str(e)}"
            logger.error(error_msg)
            return False, error_msg
        except Exception as e:
            error_msg = f"Exception: {str(e)}"
            logger.error(error_msg)
            return False, error_msg


class FontReleaseDownloader:
    """Font Release downloader (easy-galgame-fonts)"""
    
    OWNER = "yikolemon"
    REPO = "easy-galgame-fonts"
    DOWNLOAD_DIR = "/tmp/steamdeck_fonts"
    
    def __init__(self):
        self.manager = GitHubReleaseManager(self.OWNER, self.REPO)
    
    def list_available_fonts(self) -> List[GitHubAsset]:
        """List available font packages"""
        return self.manager.get_release_assets()
    
    def get_release_info(self) -> Dict:
        """Get release information"""
        return self.manager.get_release_info()
    
    def download_font(
        self,
        asset: GitHubAsset,
        progress_callback=None
    ) -> Tuple[bool, str, Optional[str]]:
        """
        Download font package
        
        Args:
            asset: Font resource to download
            progress_callback: Progress callback
            
        Returns:
            (success_flag, message, local_path)
        """
        # Create download directory
        os.makedirs(self.DOWNLOAD_DIR, exist_ok=True)
        
        # Target path
        dest_path = os.path.join(self.DOWNLOAD_DIR, asset.name)
        
        # Download
        success, msg = self.manager.download_asset(
            asset,
            dest_path,
            progress_callback
        )
        
        if success:
            return True, msg, dest_path
        else:
            return False, msg, None
