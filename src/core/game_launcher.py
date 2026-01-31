"""
Game launcher module
"""

import os
import json
import subprocess
from typing import Tuple, List, Dict
from src.utils import get_home_dir
from src.config import Config


class GameLauncher:
    """Game launch options configuration class"""
    
    def __init__(self):
        self.steam_user_dir = Config.get_steam_dir()
    
    def find_steam_apps(self) -> List[Dict]:
        """
        Find installed Steam games
        
        Returns:
            List of games [{"app_id": xxx, "name": xxx}, ...]
        """
        games = []
        
        try:
            # Traverse userdata directory
            if not os.path.isdir(self.steam_user_dir):
                return games
            
            # Find all user directories
            for user_id in os.listdir(self.steam_user_dir):
                user_path = os.path.join(self.steam_user_dir, user_id)
                config_file = os.path.join(user_path, "config/shortcuts.vdf")
                
                # Check shortcuts.vdf file
                if os.path.isfile(config_file):
                    # Parse VDF file here
                    # For now, query via command line
                    pass
        
        except Exception as e:
            print(f"Error finding games: {str(e)}")
        
        return games
    
    def get_zh_locale_command(self) -> str:
        """Get Chinese locale launch command"""
        return "LANG=zh_CN.UTF-8 LC_ALL=zh_CN.UTF-8 LC_CTYPE=zh_CN.UTF-8 LC_MESSAGES=zh_CN.UTF-8 LANGUAGE=zh_CN %command%"
    
    def apply_zh_locale_to_game(self, game_id: str, game_path: str) -> Tuple[bool, str]:
        """
        Apply Chinese locale settings to game
        
        Args:
            game_id: Game ID or name
            game_path: Game path
            
        Returns:
            (success_flag, detailed_message)
        """
        try:
            zh_command = self.get_zh_locale_command()
            
            # Configure based on actual game launcher
            # Provide command for manual user configuration
            
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
    
    def copy_zh_command_to_clipboard(self) -> bool:
        """Copy Chinese locale command to clipboard"""
        try:
            command = self.get_zh_locale_command()
            
            # Try different clipboard tools
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
            print(f"Failed to copy to clipboard: {str(e)}")
            return False


def get_zh_locale_preset() -> str:
    """Get Chinese locale preset command"""
    launcher = GameLauncher()
    return launcher.get_zh_locale_command()


def apply_zh_locale_to_game(game_id: str, game_path: str) -> Tuple[bool, str]:
    """Convenience function to apply Chinese locale settings to game"""
    launcher = GameLauncher()
    return launcher.apply_zh_locale_to_game(game_id, game_path)


def copy_zh_command_to_clipboard() -> bool:
    """Convenience function to copy Chinese locale command to clipboard"""
    launcher = GameLauncher()
    return launcher.copy_zh_command_to_clipboard()
