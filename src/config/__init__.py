"""
Configuration management module
"""

import os
from typing import Dict, Any
import json


class Config:
    """Configuration management class"""
    
    # System configuration
    FONTS_DIR = "/usr/share/fonts/galgame"
    TEMP_EXTRACT_DIR = "/tmp/galgame_fonts_extract"
    STEAM_USER_DIR = os.path.join(os.path.expanduser("~"), ".steam/root/userdata")
    
    # Application configuration
    APP_NAME = "SteamDeck Chinese Environment Config Tool"
    APP_VERSION = "1.0.0"
    
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
