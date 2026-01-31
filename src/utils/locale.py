"""
Locale detection and language switching module
Automatically select TUI display language based on system locale
"""

import os
from typing import Dict


class LocaleDetector:
    """Detect system locale and select appropriate language"""
    
    # Supported languages
    LANGUAGES = {
        'zh': 'Chinese',
        'en': 'English',
    }
    
    # Chinese locale identifiers
    CHINESE_LOCALES = ['zh_CN', 'zh_TW', 'zh_HK', 'Chinese']
    
    def __init__(self):
        """Initialize detector"""
        self.lang = self._detect_language()
    
    def _detect_language(self) -> str:
        """
        Detect system language
        
        Returns:
            'zh' for Chinese, 'en' for English
        """
        try:
            # Get from environment variables
            lang = os.environ.get('LANG', '').lower()
            language = os.environ.get('LANGUAGE', '').lower()
            lc_all = os.environ.get('LC_ALL', '').lower()
            
            # Check for Chinese
            combined = f"{lang} {language} {lc_all}"
            for locale_variant in self.CHINESE_LOCALES:
                if locale_variant.lower() in combined:
                    return 'zh'
            
            # Default to English
            return 'en'
        except Exception:
            return 'en'
    
    def is_chinese(self) -> bool:
        """Check if system is in Chinese environment"""
        return self.lang == 'zh'
    
    def get_text(self, key: str, zh: str, en: str) -> str:
        """
        Get text in appropriate language
        
        Args:
            key: Text key (for debugging)
            zh: Chinese text
            en: English text
            
        Returns:
            Text in appropriate language
        """
        return zh if self.lang == 'zh' else en


# Global detector instance
_detector = None


def get_detector() -> LocaleDetector:
    """Get global locale detector"""
    global _detector
    if _detector is None:
        _detector = LocaleDetector()
    return _detector


def t(key: str, zh: str, en: str) -> str:
    """
    Convenience function: Translate text
    
    Usage:
        text = t('menu_title', '主菜单', 'Main Menu')
    """
    return get_detector().get_text(key, zh, en)


def is_chinese() -> bool:
    """Convenience function: Check if system is in Chinese environment"""
    return get_detector().is_chinese()
