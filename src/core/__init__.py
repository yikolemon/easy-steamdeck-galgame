"""
Core module - Business logic for font installation, system locale setup, etc.
"""

from .game_launcher import (
    GameLauncher,
    get_zh_locale_preset,
    apply_zh_locale_to_game,
    copy_zh_command_to_clipboard,
)
from .downloader import (
    FontReleaseDownloader,
    GitHubReleaseManager,
    GitHubAsset,
)

__all__ = [
    "GameLauncher",
    "get_zh_locale_preset",
    "apply_zh_locale_to_game",
    "copy_zh_command_to_clipboard",
    "FontReleaseDownloader",
    "GitHubReleaseManager",
    "GitHubAsset",
]
