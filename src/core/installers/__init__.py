"""
安装器模块
"""

from .locale import (
    LocaleInstaller,
    setup_locale,
    check_locale_status,
)
from .font import (
    FontInstaller,
    setup_fonts,
    check_fonts_status,
    get_fonts_count,
    download_and_install_fonts,
    list_available_fonts,
    get_fonts_release_info,
)

__all__ = [
    "LocaleInstaller",
    "FontInstaller",
    "setup_locale",
    "check_locale_status",
    "setup_fonts",
    "check_fonts_status",
    "get_fonts_count",
    "download_and_install_fonts",
    "list_available_fonts",
    "get_fonts_release_info",
]
