"""
配置管理模块
"""

import os
from typing import Dict, Any
import json


class Config:
    """配置管理类"""
    
    # 系统配置
    FONTS_DIR = "/usr/share/fonts/galgame"
    TEMP_EXTRACT_DIR = "/tmp/galgame_fonts_extract"
    STEAM_USER_DIR = os.path.join(os.path.expanduser("~"), ".steam/root/userdata")
    
    # 应用配置
    APP_NAME = "SteamDeck 中文环境配置工具"
    APP_VERSION = "1.0.0"
    
    @classmethod
    def get_fonts_dir(cls) -> str:
        """获取字体目录"""
        return cls.FONTS_DIR
    
    @classmethod
    def get_temp_dir(cls) -> str:
        """获取临时目录"""
        return cls.TEMP_EXTRACT_DIR
    
    @classmethod
    def get_steam_dir(cls) -> str:
        """获取 Steam 用户数据目录"""
        return cls.STEAM_USER_DIR
    
    @classmethod
    def get_app_info(cls) -> Dict[str, str]:
        """获取应用信息"""
        return {
            "name": cls.APP_NAME,
            "version": cls.APP_VERSION,
        }
