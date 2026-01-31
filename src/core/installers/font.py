"""
字体安装器
"""

import os
import zipfile
import shutil
from typing import Tuple, Optional, Callable, Dict
from src.utils import run_command, disable_readonly, enable_readonly, is_fonts_installed
from src.config import Config
from .base import BaseInstaller
from src.core.font_downloader import FontReleaseDownloader, GitHubAsset


class FontInstaller(BaseInstaller):
    """中文字体安装器"""
    
    def __init__(self, zip_path: Optional[str] = None, asset: Optional[GitHubAsset] = None):
        self.zip_path: Optional[str] = zip_path
        self.asset: Optional[GitHubAsset] = asset
        self.fonts_dir = Config.get_fonts_dir()
        self.temp_dir = Config.get_temp_dir()
        self.downloader = FontReleaseDownloader()
    
    def install(self, zip_path: Optional[str] = None, progress_callback: Optional[Callable] = None) -> Tuple[bool, str]:
        if zip_path:
            self.zip_path = zip_path
        
        if not self.zip_path:
            return False, "❌ 未指定字体包路径"
        
        try:
            # 检查 zip 文件是否存在
            if not os.path.isfile(self.zip_path):
                return False, f"❌ 字体包不存在: {self.zip_path}"
            
            # 关闭只读模式
            print("👉 1. 关闭 SteamOS 只读模式...")
            if not disable_readonly():
                return False, "❌ 无法关闭只读模式，请检查权限"
            
            try:
                # 创建临时解压目录
                if os.path.exists(self.temp_dir):
                    shutil.rmtree(self.temp_dir)
                os.makedirs(self.temp_dir, exist_ok=True)
                
                # 解压字体包
                print("👉 2. 解压字体包...")
                with zipfile.ZipFile(self.zip_path, 'r') as zip_ref:
                    zip_ref.extractall(self.temp_dir)
                
                # 创建目标目录
                print("👉 3. 创建字体目录...")
                os.makedirs(self.fonts_dir, exist_ok=True)
                
                # 复制字体文件，跳过已存在的
                print("👉 4. 复制字体文件...")
                font_count = 0
                skip_count = 0
                
                for root, dirs, files in os.walk(self.temp_dir):
                    for file in files:
                        src_file = os.path.join(root, file)
                        dst_file = os.path.join(self.fonts_dir, file)
                        
                        if os.path.exists(dst_file):
                            print(f"⏭️ 跳过已存在: {file}")
                            skip_count += 1
                        else:
                            shutil.copy2(src_file, dst_file)
                            print(f"✓ 已复制: {file}")
                            font_count += 1
                
                # 更新字体缓存
                print("👉 5. 更新字体缓存...")
                success, msg = run_command("fc-cache -fv", use_sudo=True)
                if not success:
                    # 字体缓存失败不影响最终结果
                    print(f"⚠️ 字体缓存更新可能失败: {msg}")
                
                # 清理临时目录
                shutil.rmtree(self.temp_dir)
                
                # 恢复只读模式
                print("👉 6. 恢复 SteamOS 只读模式...")
                if not enable_readonly():
                    return False, f"⚠️ 警告: 无法恢复只读模式，请手动执行 'sudo steamos-readonly enable'\n✅ 但字体已安装成功！复制了 {font_count} 个文件，跳过了 {skip_count} 个已存在的文件"
                
                return True, f"✅ 字体安装完成！\n复制了 {font_count} 个文件\n跳过了 {skip_count} 个已存在的文件"
            
            except Exception as e:
                enable_readonly()
                return False, f"❌ 安装过程异常: {str(e)}"
        
        except Exception as e:
            try:
                enable_readonly()
            except:
                pass
            return False, f"❌ 异常: {str(e)}"
    
    def check_status(self) -> bool:
        """检查字体是否已安装"""
        return is_fonts_installed()
    
    def get_fonts_count(self) -> int:
        """获取已安装的字体数量"""
        if os.path.isdir(self.fonts_dir):
            return len(os.listdir(self.fonts_dir))
        return 0


def setup_fonts(zip_path: str) -> Tuple[bool, str]:
    """安装中文字体的便捷函数"""
    installer = FontInstaller(zip_path)
    return installer.install()


def download_and_install_fonts(asset: GitHubAsset, progress_callback: Optional[Callable] = None) -> Tuple[bool, str]:
    """
    从 GitHub Release 下载并安装字体的便捷函数
    
    Args:
        asset: 要下载的字体资源
        progress_callback: 进度回调
        
    Returns:
        (成功标志, 详细信息)
    """
    downloader = FontReleaseDownloader()
    
    # 下载字体
    print(f"👉 正在下载字体包: {asset.name}...")
    success, msg, zip_path = downloader.download_font(asset, progress_callback)
    
    if not success:
        return False, msg
    
    # 安装字体
    print("\n👉 开始安装字体...")
    installer = FontInstaller(zip_path)
    return installer.install(progress_callback=progress_callback)


def list_available_fonts() -> Tuple[bool, list]:
    """
    列出可用的字体包
    
    Returns:
        (成功标志, 资源列表)
    """
    try:
        downloader = FontReleaseDownloader()
        assets = downloader.list_available_fonts()
        if assets:
            return True, assets
        else:
            return False, []
    except Exception as e:
        print(f"❌ 获取字体列表失败: {e}")
        return False, []


def get_fonts_release_info() -> Dict:
    """获取字体 Release 信息"""
    try:
        downloader = FontReleaseDownloader()
        return downloader.get_release_info()
    except Exception as e:
        print(f"❌ 获取 Release 信息失败: {e}")
        return {}


def check_fonts_status() -> bool:
    """检查字体状态的便捷函数"""
    installer = FontInstaller()
    return installer.check_status()


def get_fonts_count() -> int:
    """获取已安装字体数量的便捷函数"""
    installer = FontInstaller()
    return installer.get_fonts_count()
