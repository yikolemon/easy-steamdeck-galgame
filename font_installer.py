"""
中文字体安装模块
"""

import os
import zipfile
import shutil
from pathlib import Path
from utils import run_command, disable_readonly, enable_readonly, is_fonts_installed


FONTS_DIR = "/usr/share/fonts/galgame"


def setup_fonts(zip_path: str) -> tuple[bool, str]:
    """
    安装中文字体
    
    Args:
        zip_path: GAL_Fonts_Minimal.zip 的路径
        
    Returns:
        (成功标志, 详细信息)
    """
    try:
        # 检查 zip 文件是否存在
        if not os.path.isfile(zip_path):
            return False, f"❌ 字体包不存在: {zip_path}"
        
        # 关闭只读模式
        print("👉 1. 关闭 SteamOS 只读模式...")
        if not disable_readonly():
            return False, "❌ 无法关闭只读模式，请检查权限"
        
        try:
            # 创建临时解压目录
            temp_extract_dir = "/tmp/galgame_fonts_extract"
            if os.path.exists(temp_extract_dir):
                shutil.rmtree(temp_extract_dir)
            os.makedirs(temp_extract_dir, exist_ok=True)
            
            # 解压字体包
            print("👉 2. 解压字体包...")
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(temp_extract_dir)
            
            # 创建目标目录
            print("👉 3. 创建字体目录...")
            os.makedirs(FONTS_DIR, exist_ok=True)
            
            # 复制字体文件，跳过已存在的
            print("👉 4. 复制字体文件...")
            font_count = 0
            skip_count = 0
            
            for root, dirs, files in os.walk(temp_extract_dir):
                for file in files:
                    src_file = os.path.join(root, file)
                    dst_file = os.path.join(FONTS_DIR, file)
                    
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
            shutil.rmtree(temp_extract_dir)
            
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


def check_fonts_status() -> bool:
    """检查字体是否已安装"""
    return is_fonts_installed()


def get_fonts_count() -> int:
    """获取已安装的字体数量"""
    if os.path.isdir(FONTS_DIR):
        return len(os.listdir(FONTS_DIR))
    return 0
