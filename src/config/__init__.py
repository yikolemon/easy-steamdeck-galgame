"""
Configuration management module
"""

import os
from typing import Dict, Any, Optional, List
import json


class TargetLanguage:
    """Target language configuration"""

    CHINESE = "zh"
    JAPANESE = "ja"

    # Locale codes for each language
    LOCALES = {
        CHINESE: "zh_CN.UTF-8",
        JAPANESE: "ja_JP.UTF-8",
    }

    # Display names for each language
    NAMES = {
        CHINESE: {"zh": "简体中文", "en": "Simplified Chinese"},
        JAPANESE: {"zh": "日本語", "en": "Japanese"},
    }

    @classmethod
    def get_locale(cls, lang: str) -> str:
        """Get locale code for target language"""
        return cls.LOCALES.get(lang, cls.LOCALES[cls.CHINESE])

    @classmethod
    def get_name(cls, lang: str, display_lang: str = "en") -> str:
        """Get display name for target language"""
        return cls.NAMES.get(lang, cls.NAMES[cls.CHINESE]).get(display_lang, "Unknown")


class Config:
    """Configuration management class"""

    # System configuration
    FONTS_DIR = "/usr/share/fonts/galgame"
    TEMP_EXTRACT_DIR = "/tmp/galgame_fonts_extract"
    CONFIG_FILE_NAME = ".steamdeck_galgame_config.json"

    # Application configuration
    APP_NAME = "SteamDeck Chinese Environment Config Tool"
    APP_VERSION = "1.0.0"

    # Runtime configuration (set by user)
    _target_language: Optional[str] = None
    _default_font_path: Optional[str] = None
    _config_file: Optional[str] = None
    _steam_dir: Optional[str] = None

    @classmethod
    def _get_home_dir(cls) -> str:
        """Get user home directory with fallbacks"""
        # Try multiple methods to get home directory
        home = os.environ.get("HOME")
        if home and os.path.isdir(home):
            return home

        home = os.path.expanduser("~")
        if home and home != "~" and os.path.isdir(home):
            return home

        # Fallback for edge cases
        import pwd

        try:
            home = pwd.getpwuid(os.getuid()).pw_dir
            if home and os.path.isdir(home):
                return home
        except Exception:
            pass

        return "/home"

    @classmethod
    def _get_config_file(cls) -> str:
        """Get config file path"""
        if cls._config_file is None:
            cls._config_file = os.path.join(cls._get_home_dir(), cls.CONFIG_FILE_NAME)
        return cls._config_file

    @classmethod
    def get_fonts_dir(cls) -> str:
        """Get fonts directory"""
        return cls.FONTS_DIR

    @classmethod
    def get_temp_dir(cls) -> str:
        """Get temporary directory"""
        return cls.TEMP_EXTRACT_DIR

    @classmethod
    def get_steam_dir(cls) -> str:
        """Get Steam user data directory"""
        if cls._steam_dir is None:
            cls._steam_dir = os.path.join(cls._get_home_dir(), ".steam/root/userdata")
        return cls._steam_dir

    @classmethod
    def get_app_info(cls) -> Dict[str, str]:
        """Get application information"""
        return {
            "name": cls.APP_NAME,
            "version": cls.APP_VERSION,
        }

    @classmethod
    def get_target_language(cls) -> str:
        """Get current target language (default: Chinese)"""
        if cls._target_language is None:
            # Load from config file
            config = cls.load_config()
            cls._target_language = config.get("target_language", TargetLanguage.CHINESE)
        return cls._target_language

    @classmethod
    def set_target_language(cls, lang: str):
        """Set target language and save to config"""
        cls._target_language = lang
        cls.save_config({"target_language": lang})

    @classmethod
    def get_default_font_path(cls) -> Optional[str]:
        """Get default font zip package search path"""
        if cls._default_font_path is None:
            # Load from config file
            config = cls.load_config()
            cls._default_font_path = config.get("default_font_path")
        return cls._default_font_path

    @classmethod
    def set_default_font_path(cls, path: str):
        """Set default font zip package search path and save to config"""
        cls._default_font_path = path
        cls.save_config({"default_font_path": path})

    @classmethod
    def get_managed_games(cls) -> List[Dict[str, Any]]:
        """Get list of games managed by this program"""
        config = cls.load_config()
        return config.get("managed_games", [])

    @classmethod
    def set_managed_games(cls, games: List[Dict[str, Any]]):
        """Set managed games list and save to config"""
        cls.save_config({"managed_games": games})

    @classmethod
    def add_managed_game(cls, game: Dict[str, Any]):
        """Add a game to the managed games list"""
        games = cls.get_managed_games()
        # Check if game already exists (by name or path)
        for existing_game in games:
            if existing_game.get("name") == game.get("name") or existing_game.get(
                "exe_path"
            ) == game.get("exe_path"):
                # Update existing game
                existing_game.update(game)
                cls.set_managed_games(games)
                return
        # Add new game
        games.append(game)
        cls.set_managed_games(games)

    @classmethod
    def load_config(cls) -> Dict[str, Any]:
        """Load configuration from file"""
        try:
            config_file = cls._get_config_file()
            if os.path.exists(config_file):
                with open(config_file, "r") as f:
                    return json.load(f)
        except Exception:
            pass
        return {}

    @classmethod
    def save_config(cls, config: Dict[str, Any]):
        """Save configuration to file"""
        try:
            config_file = cls._get_config_file()
            existing = cls.load_config()
            existing.update(config)
            with open(config_file, "w") as f:
                json.dump(existing, f, indent=2)
        except Exception as e:
            print(f"Warning: Failed to save config: {e}")
