"""
Game launcher module
"""

import os
import json
import subprocess
from typing import Tuple, List, Dict
from src.utils import get_home_dir
from src.config import Config

# Locale launch command constants
ZH_LOCALE_COMMAND = "LANG=zh_CN.UTF-8 LC_ALL=zh_CN.UTF-8 LC_CTYPE=zh_CN.UTF-8 LC_MESSAGES=zh_CN.UTF-8 LANGUAGE=zh_CN %command%"
JA_LOCALE_COMMAND = "LANG=ja_JP.UTF-8 LC_ALL=ja_JP.UTF-8 LC_CTYPE=ja_JP.UTF-8 LC_MESSAGES=ja_JP.UTF-8 LANGUAGE=ja_JP %command%"


class GameLauncher:
    """Game launcher utility class - all methods are static"""
    
    @staticmethod
    def find_steam_apps() -> List[Dict]:
        """
        Find installed Steam games
        
        Returns:
            List of games [{"app_id": xxx, "name": xxx}, ...]
        """
        games = []
        steam_user_dir = Config.get_steam_dir()
        
        try:
            # Traverse userdata directory
            if not os.path.isdir(steam_user_dir):
                return games
            
            # Find all user directories
            for user_id in os.listdir(steam_user_dir):
                user_path = os.path.join(steam_user_dir, user_id)
                config_file = os.path.join(user_path, "config/shortcuts.vdf")
                
                # Check shortcuts.vdf file
                if os.path.isfile(config_file):
                    # Parse VDF file here
                    # For now, query via command line
                    pass
        
        except Exception as e:
            print(f"Error finding games: {str(e)}")
        
        return games

    @staticmethod
    def apply_zh_locale_to_game(game_id: str, game_path: str) -> Tuple[bool, str]:
        """
        Apply Chinese locale settings to game
        
        Args:
            game_id: Game ID or name
            game_path: Game path
            
        Returns:
            (success_flag, detailed_message)
        """
        try:
            zh_command = get_zh_locale_command()
            
            info = f"""
Game Launch Options Configuration

Game: {game_id}
Path: {game_path}

Enter the following in Game Properties -> Launch Options:

{zh_command}

This will use Chinese locale when launching the game.
"""
            return True, info
        
        except Exception as e:
            return False, f"ERROR: Exception: {str(e)}"
    
    @staticmethod
    def copy_zh_command_to_clipboard() -> bool:
        """Copy Chinese locale command to clipboard"""
        try:
            command = get_zh_locale_command()
            
            # Try xclip first (most common on Linux)
            try:
                process = subprocess.Popen(['xclip', '-selection', 'clipboard'], 
                                         stdin=subprocess.PIPE)
                process.communicate(command.encode('utf-8'))
                return True
            except FileNotFoundError:
                pass
            
            # Fallback to xsel
            try:
                process = subprocess.Popen(['xsel', '-bi'], 
                                         stdin=subprocess.PIPE)
                process.communicate(command.encode('utf-8'))
                return True
            except FileNotFoundError:
                pass
            
            # If both fail
            print("Warning: Neither xclip nor xsel found. Clipboard copy failed.")
            return False
        
        except Exception as e:
            print(f"Failed to copy to clipboard: {str(e)}")
            return False


def get_zh_locale_preset() -> str:
    """Get Chinese locale preset command"""
    return get_zh_locale_command()


def apply_zh_locale_to_game(game_id: str, game_path: str) -> Tuple[bool, str]:
    """Convenience function to apply Chinese locale settings to game"""
    return GameLauncher.apply_zh_locale_to_game(game_id, game_path)


def copy_zh_command_to_clipboard() -> bool:
    """Convenience function to copy Chinese locale command to clipboard"""
    return GameLauncher.copy_zh_command_to_clipboard()


def get_zh_locale_command() -> str:
    """Get Chinese locale launch command"""
    return ZH_LOCALE_COMMAND


def get_ja_locale_command() -> str:
    """Get Japanese locale launch command"""
    return JA_LOCALE_COMMAND


def get_locale_command(target_lang: str = 'zh') -> str:
    """
    Get locale launch command based on target language
    
    Args:
        target_lang: 'zh' for Chinese, 'ja' for Japanese
        
    Returns:
        Locale launch command string
    """
    if target_lang == 'ja':
        return JA_LOCALE_COMMAND
    return ZH_LOCALE_COMMAND
