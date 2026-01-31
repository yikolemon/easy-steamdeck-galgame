"""
Locale 安装器
"""

import subprocess
from typing import Tuple
from src.utils import run_command, disable_readonly, enable_readonly, is_zh_locale_enabled
from .base import BaseInstaller


class LocaleInstaller(BaseInstaller):
    """中文 locale 安装器"""
    
    def install(self) -> Tuple[bool, str]:
        """
        安装中文 locale
        
        Returns:
            (成功标志, 详细信息)
        """
        try:
            # 1. 关闭只读模式
            print("👉 1. 关闭 SteamOS 只读模式...")
            if not disable_readonly():
                return False, "❌ 无法关闭只读模式，请检查权限"
            
            # 2. 初始化 pacman key
            print("👉 2. 初始化 pacman key...")
            success, msg = run_command("pacman-key --init", use_sudo=True)
            if not success:
                enable_readonly()
                return False, f"❌ pacman-key --init 失败: {msg}"
            
            success, msg = run_command("pacman-key --populate archlinux", use_sudo=True)
            if not success:
                enable_readonly()
                return False, f"❌ pacman-key --populate 失败: {msg}"
            
            # 3. 检查并启用 zh_CN.UTF-8 locale
            print("👉 3. 启用简体中文 locale（zh_CN.UTF-8）...")
            check_result = subprocess.run(
                "grep '^#zh_CN.UTF-8 UTF-8' /etc/locale.gen",
                shell=True,
                capture_output=True,
                check=False
            )
            
            if check_result.returncode == 0:
                # 找到被注释的行，需要取消注释
                success, msg = run_command(
                    "sed -i 's/^#zh_CN.UTF-8 UTF-8/zh_CN.UTF-8 UTF-8/' /etc/locale.gen",
                    use_sudo=True
                )
                if not success:
                    enable_readonly()
                    return False, f"❌ 修改 locale.gen 失败: {msg}"
            else:
                print("⚠️ zh_CN.UTF-8 已启用或不存在，跳过修改")
            
            # 4. 生成 locale
            print("👉 4. 生成 locale...")
            success, msg = run_command("locale-gen", use_sudo=True)
            if not success:
                enable_readonly()
                return False, f"❌ locale-gen 失败: {msg}"
            
            # 5. 启用只读模式
            print("👉 5. 恢复 SteamOS 只读模式...")
            if not enable_readonly():
                return False, "⚠️ 警告: 无法恢复只读模式，请手动执行 'sudo steamos-readonly enable'"
            
            return True, "✅ 中文 locale 安装完成！"
        
        except Exception as e:
            try:
                enable_readonly()
            except:
                pass
            return False, f"❌ 异常: {str(e)}"
    
    def check_status(self) -> bool:
        """检查中文 locale 是否已安装"""
        return is_zh_locale_enabled()


def setup_locale() -> Tuple[bool, str]:
    """安装中文 locale 的便捷函数"""
    installer = LocaleInstaller()
    return installer.install()


def check_locale_status() -> bool:
    """检查中文 locale 状态的便捷函数"""
    installer = LocaleInstaller()
    return installer.check_status()
