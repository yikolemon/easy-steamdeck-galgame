"""
Configuration management module
"""

import os
from typing import Dict, Any, Optional
import json


class TargetLanguage:
    """Target language configuration"""
    CHINESE = 'zh'
    JAPANESE = 'ja'
    
    # Locale codes for each language
    LOCALES = {
        CHINESE: 'zh_CN.UTF-8',
        JAPANESE: 'ja_JP.UTF-8',
    }
    
    # Display names for each language
    NAMES = {
        CHINESE: {'zh': '简体中文', 'en': 'Simplified Chinese'},
        JAPANESE: {'zh': '日本語', 'en': 'Japanese'},
    }
    
    @classmethod
    def get_locale(cls, lang: str) -> str:
        """Get locale code for target language"""
        return cls.LOCALES.get(lang, cls.LOCALES[cls.CHINESE])
    
    @classmethod
    def get_name(cls, lang: str, display_lang: str = 'en') -> str:
        """Get display name for target language"""
        return cls.NAMES.get(lang, cls.NAMES[cls.CHINESE]).get(display_lang, 'Unknown')


class Config:
    """Configuration management class"""
    
    # System configuration
    FONTS_DIR = "/usr/share/fonts/galgame"
    TEMP_EXTRACT_DIR = "/tmp/galgame_fonts_extract"
    STEAM_USER_DIR = os.path.join(os.path.expanduser("~"), ".steam/root/userdata")
    CONFIG_FILE = os.path.join(os.path.expanduser("~"), ".steamdeck_galgame_config.json")
    
    # Application configuration
    APP_NAME = "SteamDeck Chinese Environment Config Tool"
    APP_VERSION = "1.0.0"
    
    # Runtime configuration (set by user)
    _target_language: Optional[str] = None
    
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
        return cls.STEAM_USER_DIR
    
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
            cls._target_language = config.get('target_language', TargetLanguage.CHINESE)
        return cls._target_language
    
    @classmethod
    def set_target_language(cls, lang: str):
        """Set target language and save to config"""
        cls._target_language = lang
        cls.save_config({'target_language': lang})
    
    @classmethod
    def load_config(cls) -> Dict[str, Any]:
        """Load configuration from file"""
        try:
            if os.path.exists(cls.CONFIG_FILE):
                with open(cls.CONFIG_FILE, 'r') as f:
                    return json.load(f)
        except Exception:
            pass
        return {}
    
    @classmethod
    def save_config(cls, config: Dict[str, Any]):
        """Save configuration to file"""
        try:
            existing = cls.load_config()
            existing.update(config)
            with open(cls.CONFIG_FILE, 'w') as f:
                json.dump(existing, f, indent=2)
        except Exception as e:
            print(f"Warning: Failed to save config: {e}")
