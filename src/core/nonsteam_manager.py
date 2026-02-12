"""
Non-Steam game management module
"""

import os
from typing import List, Dict, Any, Tuple, Optional
from src.config import Config


class NonSteamManager:
    """Manager for non-Steam games"""

    @staticmethod
    def get_compatibility_layers() -> List[str]:
        """Get list of available Steam compatibility layers"""
        steam_root = os.path.join(Config._get_home_dir(), ".steam", "root")
        compat_dir = os.path.join(steam_root, "compatibilitytools.d")

        layers = []
        if os.path.exists(compat_dir):
            try:
                for item in os.listdir(compat_dir):
                    item_path = os.path.join(compat_dir, item)
                    if os.path.isdir(item_path):
                        layers.append(item)
            except Exception:
                pass

        # Add built-in layers if not already present
        builtin_layers = ["Steam Linux Runtime", "Proton Experimental"]
        for layer in builtin_layers:
            if layer not in layers:
                layers.append(layer)

        return sorted(layers)

    @staticmethod
    def add_game(
        name: str,
        exe_path: str,
        compat_layer: str,
        properties: Optional[Dict[str, Any]] = None,
    ) -> Tuple[bool, str]:
        """Add a non-Steam game"""
        if not os.path.exists(exe_path):
            return False, f"Executable not found: {exe_path}"

        game = {
            "name": name,
            "exe_path": exe_path,
            "compat_layer": compat_layer,
            "properties": properties or {},
        }

        try:
            Config.add_managed_game(game)
            return True, "Game added successfully"
        except Exception as e:
            return False, f"Failed to add game: {str(e)}"

    @staticmethod
    def get_games() -> List[Dict[str, Any]]:
        """Get list of managed non-Steam games"""
        return Config.get_managed_games()

    @staticmethod
    def update_game(name: str, updates: Dict[str, Any]) -> Tuple[bool, str]:
        """Update a managed game"""
        games = Config.get_managed_games()
        for game in games:
            if game.get("name") == name:
                game.update(updates)
                Config.set_managed_games(games)
                return True, "Game updated successfully"
        return False, f"Game not found: {name}"

    @staticmethod
    def get_steam_shortcut_command(game: Dict[str, Any]) -> str:
        """Generate Steam shortcut command for the game"""
        name = game.get("name", "")
        exe_path = game.get("exe_path", "")
        compat_layer = game.get("compat_layer", "")
        launch_options = game.get("properties", {}).get("launch_options", "")

        # Basic Proton command
        if "Proton" in compat_layer:
            proton_path = f"~/.steam/root/compatibilitytools.d/{compat_layer}/proton"
            cmd = f'"{proton_path}" run "{exe_path}"'
        else:
            cmd = f'"{exe_path}"'

        if launch_options:
            cmd += f" {launch_options}"

        return cmd
