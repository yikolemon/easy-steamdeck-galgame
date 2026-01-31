"""
GitHub Release 下载管理器
"""

import requests
import os
import json
from typing import List, Dict, Optional, Tuple
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class GitHubAsset:
    """GitHub Release 资源对象"""
    
    def __init__(self, name: str, size: int, download_url: str):
        self.name = name
        self.size = size
        self.download_url = download_url
    
    def get_size_mb(self) -> float:
        """获取文件大小（MB）"""
        return self.size / (1024 * 1024)
    
    def __repr__(self) -> str:
        return f"{self.name} ({self.get_size_mb():.1f} MB)"


class GitHubReleaseManager:
    """GitHub Release 下载管理器"""
    
    def __init__(self, owner: str, repo: str, timeout: int = 10):
        """
        初始化
        
        Args:
            owner: GitHub 用户名
            repo: 仓库名
            timeout: 请求超时时间（秒）
        """
        self.owner = owner
        self.repo = repo
        self.timeout = timeout
        self.api_url = f"https://api.github.com/repos/{owner}/{repo}"
    
    def get_latest_release(self) -> Optional[Dict]:
        """
        获取最新 release 信息
        
        Returns:
            Release 信息字典，失败返回 None
        """
        try:
            url = f"{self.api_url}/releases/latest"
            response = requests.get(url, timeout=self.timeout)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            logger.error(f"获取 release 信息失败: {e}")
            return None
    
    def get_release_assets(self) -> List[GitHubAsset]:
        """
        获取最新 release 的所有资源
        
        Returns:
            资源列表
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
        获取 release 信息
        
        Returns:
            包含版本、描述等的字典
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
        下载资源
        
        Args:
            asset: 要下载的资源
            dest_path: 目标路径
            progress_callback: 进度回调函数 (downloaded, total)
            
        Returns:
            (成功标志, 消息)
        """
        try:
            # 创建目标目录
            os.makedirs(os.path.dirname(dest_path), exist_ok=True)
            
            logger.info(f"开始下载: {asset.name}")
            print(f"👉 下载: {asset.name} ({asset.get_size_mb():.1f} MB)")
            
            # 发送请求
            response = requests.get(
                asset.download_url,
                timeout=self.timeout,
                stream=True
            )
            response.raise_for_status()
            
            # 获取文件大小
            total_size = int(response.headers.get('content-length', 0))
            
            # 下载文件
            downloaded = 0
            chunk_size = 1024 * 1024  # 1MB chunks
            
            with open(dest_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=chunk_size):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        
                        # 调用进度回调
                        if progress_callback:
                            progress_callback(downloaded, total_size)
                        
                        # 打印进度
                        if total_size > 0:
                            percent = (downloaded / total_size) * 100
                            print(f"  进度: {percent:.1f}% ({downloaded / (1024*1024):.1f}/{total_size / (1024*1024):.1f} MB)")
            
            logger.info(f"下载完成: {dest_path}")
            return True, f"✅ 下载完成: {asset.name}"
        
        except requests.RequestException as e:
            error_msg = f"❌ 下载失败: {str(e)}"
            logger.error(error_msg)
            return False, error_msg
        except IOError as e:
            error_msg = f"❌ 保存文件失败: {str(e)}"
            logger.error(error_msg)
            return False, error_msg
        except Exception as e:
            error_msg = f"❌ 异常: {str(e)}"
            logger.error(error_msg)
            return False, error_msg


class FontReleaseDownloader:
    """字体 Release 下载器（easy-galgame-fonts）"""
    
    OWNER = "yikolemon"
    REPO = "easy-galgame-fonts"
    DOWNLOAD_DIR = "/tmp/steamdeck_fonts"
    
    def __init__(self):
        self.manager = GitHubReleaseManager(self.OWNER, self.REPO)
    
    def list_available_fonts(self) -> List[GitHubAsset]:
        """列出可用的字体包"""
        return self.manager.get_release_assets()
    
    def get_release_info(self) -> Dict:
        """获取 release 信息"""
        return self.manager.get_release_info()
    
    def download_font(
        self,
        asset: GitHubAsset,
        progress_callback=None
    ) -> Tuple[bool, str, Optional[str]]:
        """
        下载字体包
        
        Args:
            asset: 要下载的字体资源
            progress_callback: 进度回调
            
        Returns:
            (成功标志, 消息, 本地路径)
        """
        # 创建下载目录
        os.makedirs(self.DOWNLOAD_DIR, exist_ok=True)
        
        # 目标路径
        dest_path = os.path.join(self.DOWNLOAD_DIR, asset.name)
        
        # 下载
        success, msg = self.manager.download_asset(
            asset,
            dest_path,
            progress_callback
        )
        
        if success:
            return True, msg, dest_path
        else:
            return False, msg, None
