"""
非 Steam 游戏启动选项配置模块
"""

import os
import json
from pathlib import Path
from utils import get_home_dir, get_zh_locale_command


# SteamDeck 用户数据目录
STEAM_USER_DIR = os.path.join(get_home_dir(), ".steam/root/userdata")


def find_steam_apps() -> list[dict]:
    """
    查找已安装的 Steam 游戏
    
    Returns:
        游戏列表 [{"app_id": xxx, "name": xxx}, ...]
    """
    games = []
    
    try:
        # 遍历 userdata 目录
        if not os.path.isdir(STEAM_USER_DIR):
            return games
        
        # 查找所有用户目录
        for user_id in os.listdir(STEAM_USER_DIR):
            user_path = os.path.join(STEAM_USER_DIR, user_id)
            config_file = os.path.join(user_path, "config/shortcuts.vdf")
            
            # 检查 shortcuts.vdf 文件
            if os.path.isfile(config_file):
                # 这里需要解析 VDF 文件
                # 为了简化，可以通过命令行查询
                pass
    
    except Exception as e:
        print(f"查找游戏异常: {str(e)}")
    
    return games


def get_zh_locale_preset() -> str:
    """获取中文 locale 预设命令"""
    return get_zh_locale_command()


def apply_zh_locale_to_game(game_id: str, game_path: str) -> tuple[bool, str]:
    """
    为游戏应用中文 locale 设置
    
    Args:
        game_id: 游戏 ID 或名称
        game_path: 游戏路径
        
    Returns:
        (成功标志, 详细信息)
    """
    try:
        zh_command = get_zh_locale_command()
        
        # 根据实际的游戏启动器进行配置
        # 这里提供命令供用户手动配置
        
        info = f"""
🎮 中文启动选项配置

游戏: {game_id}
路径: {game_path}

请在游戏属性 → 启动选项中填入以下内容:

{zh_command}

这样在启动游戏时就会使用中文 locale。
"""
        return True, info
    
    except Exception as e:
        return False, f"❌ 异常: {str(e)}"


def copy_zh_command_to_clipboard() -> bool:
    """复制中文 locale 命令到剪贴板"""
    try:
        import subprocess
        command = get_zh_locale_command()
        
        # 尝试使用不同的剪贴板工具
        try:
            process = subprocess.Popen(['xclip', '-selection', 'clipboard'], 
                                     stdin=subprocess.PIPE)
            process.communicate(command.encode('utf-8'))
            return True
        except:
            try:
                process = subprocess.Popen(['xsel', '-bi'], 
                                         stdin=subprocess.PIPE)
                process.communicate(command.encode('utf-8'))
                return True
            except:
                return False
    
    except Exception as e:
        print(f"复制到剪贴板失败: {str(e)}")
        return False
