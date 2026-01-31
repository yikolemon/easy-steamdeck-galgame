"""
Locale 检测和字符兼容性模块
检测系统 locale 设置，自动选择合适的字符显示方案
"""

import locale
import os
import sys
from typing import Dict, Tuple


class LocaleDetector:
    """检测系统 locale 和字符支持"""
    
    # 中文 locale 变体
    CHINESE_LOCALES = [
        'zh_CN.UTF-8',
        'zh_CN.utf8',
        'zh_CN',
        'Chinese_China.1252',
        'zh_TW.UTF-8',
        'zh_TW.utf8',
        'zh_TW',
    ]
    
    # 字符集定义：用于不同 locale 环境
    CHAR_SETS = {
        'utf8': {
            'check': '✓',
            'cross': '✗',
            'warning': '⚠️',
            'arrow': '👉',
            'bullet': '•',
            'box_h': '─',
            'box_v': '│',
            'box_tl': '┌',
            'box_tr': '┐',
            'box_bl': '└',
            'box_br': '┘',
        },
        'ascii': {
            'check': '[OK]',
            'cross': '[X]',
            'warning': '[!]',
            'arrow': '>>',
            'bullet': '*',
            'box_h': '-',
            'box_v': '|',
            'box_tl': '+',
            'box_tr': '+',
            'box_bl': '+',
            'box_br': '+',
        },
    }
    
    def __init__(self):
        """初始化检测器"""
        self.current_locale = self._get_current_locale()
        self.supports_chinese = self._check_chinese_support()
        self.supports_utf8 = self._check_utf8_support()
        self.char_set = self._select_char_set()
    
    def _get_current_locale(self) -> str:
        """获取当前系统 locale"""
        try:
            # 尝试从环境变量获取
            lang = os.environ.get('LANG', '')
            if lang:
                return lang
            
            # 尝试从 locale 模块获取
            current = locale.getlocale()
            if current and current[0]:
                return f"{current[0]}.{current[1] or 'UTF-8'}"
            
            # 默认值
            return 'C'
        except Exception:
            return 'C'
    
    def _check_chinese_support(self) -> bool:
        """检查系统是否支持中文 locale"""
        try:
            # 检查 LANG 环境变量
            lang = os.environ.get('LANG', '').lower()
            if any(cn_locale in lang for cn_locale in ['zh_cn', 'zh_tw', 'chinese']):
                return True
            
            # 检查 LANGUAGE 环境变量
            language = os.environ.get('LANGUAGE', '').lower()
            if 'zh' in language:
                return True
            
            # 检查 LC_ALL
            lc_all = os.environ.get('LC_ALL', '').lower()
            if 'zh' in lc_all:
                return True
            
            return False
        except Exception:
            return False
    
    def _check_utf8_support(self) -> bool:
        """检查系统是否支持 UTF-8"""
        try:
            # 检查 locale 中是否包含 UTF-8
            current = self.current_locale.lower()
            if 'utf' in current or 'utf-8' in current:
                return True
            
            # 尝试编码中文字符
            try:
                '中文'.encode(sys.stdout.encoding or 'utf-8')
                return True
            except (UnicodeEncodeError, AttributeError):
                return False
        except Exception:
            return False
    
    def _select_char_set(self) -> str:
        """根据系统能力选择字符集"""
        # 优先选择 UTF-8
        if self.supports_utf8:
            try:
                # 测试输出 UTF-8 字符
                '✓'.encode(sys.stdout.encoding or 'utf-8')
                return 'utf8'
            except (UnicodeEncodeError, AttributeError):
                pass
        
        # 回退到 ASCII
        return 'ascii'
    
    def get_char(self, char_name: str) -> str:
        """
        获取字符
        
        Args:
            char_name: 字符名称 (check, cross, warning, arrow, bullet, 等)
            
        Returns:
            对应的字符
        """
        return self.CHAR_SETS[self.char_set].get(char_name, '?')
    
    def get_all_chars(self) -> Dict[str, str]:
        """获取全部字符集"""
        return self.CHAR_SETS[self.char_set].copy()
    
    def get_status_info(self) -> Dict[str, str]:
        """获取 locale 状态信息"""
        return {
            'locale': self.current_locale,
            'supports_chinese': 'Yes' if self.supports_chinese else 'No',
            'supports_utf8': 'Yes' if self.supports_utf8 else 'No',
            'char_set': 'UTF-8' if self.char_set == 'utf8' else 'ASCII',
        }
    
    def print_status(self) -> str:
        """打印 locale 状态信息为字符串"""
        info = self.get_status_info()
        lines = [
            f"Current LANG: {info['locale']}",
            f"Chinese Support: {info['supports_chinese']}",
            f"UTF-8 Support: {info['supports_utf8']}",
            f"Display Mode: {info['char_set']}",
        ]
        
        if not self.supports_chinese:
            lines.append("\n[!] Warning: Chinese locale not detected!")
            lines.append("    To display Chinese properly, install locale:")
            lines.append("    sudo pacman -S glibc-locales")
            lines.append("    sudo locale-gen zh_CN.UTF-8")
        
        if self.char_set == 'ascii':
            lines.append("\n[!] Using ASCII mode (UTF-8 not available)")
            lines.append("    For better display, ensure UTF-8 support in your terminal")
        
        return '\n'.join(lines)


# 全局检测器实例
_detector = None


def get_detector() -> LocaleDetector:
    """获取全局 locale 检测器"""
    global _detector
    if _detector is None:
        _detector = LocaleDetector()
    return _detector


def get_char(char_name: str) -> str:
    """便捷函数：获取字符"""
    return get_detector().get_char(char_name)


def get_locale_info() -> Dict[str, str]:
    """便捷函数：获取 locale 信息"""
    return get_detector().get_status_info()


def is_chinese_supported() -> bool:
    """便捷函数：检查中文支持"""
    return get_detector().supports_chinese


def is_utf8_supported() -> bool:
    """便捷函数：检查 UTF-8 支持"""
    return get_detector().supports_utf8
