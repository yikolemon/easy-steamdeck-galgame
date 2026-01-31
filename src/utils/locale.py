"""
Locale 检测和语言切换模块
根据系统 locale 自动选择 TUI 显示的语言
"""

import os
from typing import Dict


class LocaleDetector:
    """检测系统 locale，选择合适的语言"""
    
    # 支持的语言
    LANGUAGES = {
        'zh': 'Chinese',
        'en': 'English',
    }
    
    # 中文 locale 标识
    CHINESE_LOCALES = ['zh_CN', 'zh_TW', 'zh_HK', 'Chinese']
    
    def __init__(self):
        """初始化检测器"""
        self.lang = self._detect_language()
    
    def _detect_language(self) -> str:
        """
        检测系统语言
        
        Returns:
            'zh' for Chinese, 'en' for English
        """
        try:
            # 从环境变量获取
            lang = os.environ.get('LANG', '').lower()
            language = os.environ.get('LANGUAGE', '').lower()
            lc_all = os.environ.get('LC_ALL', '').lower()
            
            # 检查中文
            combined = f"{lang} {language} {lc_all}"
            for locale_variant in self.CHINESE_LOCALES:
                if locale_variant.lower() in combined:
                    return 'zh'
            
            # 默认英文
            return 'en'
        except Exception:
            return 'en'
    
    def is_chinese(self) -> bool:
        """是否为中文环境"""
        return self.lang == 'zh'
    
    def get_text(self, key: str, zh: str, en: str) -> str:
        """
        获取对应语言的文本
        
        Args:
            key: 文本键（用于调试）
            zh: 中文文本
            en: 英文文本
            
        Returns:
            对应语言的文本
        """
        return zh if self.lang == 'zh' else en


# 全局检测器实例
_detector = None


def get_detector() -> LocaleDetector:
    """获取全局 locale 检测器"""
    global _detector
    if _detector is None:
        _detector = LocaleDetector()
    return _detector


def t(key: str, zh: str, en: str) -> str:
    """
    便捷函数：翻译文本
    
    使用方式:
        text = t('menu_title', '主菜单', 'Main Menu')
    """
    return get_detector().get_text(key, zh, en)


def is_chinese() -> bool:
    """便捷函数：检查是否为中文环境"""
    return get_detector().is_chinese()
