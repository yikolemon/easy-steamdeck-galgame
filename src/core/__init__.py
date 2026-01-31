"""
核心模块
"""

from .game_launcher import (
    GameLauncher,
    get_zh_locale_preset,
    apply_zh_locale_to_game,
    copy_zh_command_to_clipboard,
)

__all__ = [
    "GameLauncher",
    "get_zh_locale_preset",
    "apply_zh_locale_to_game",
    "copy_zh_command_to_clipboard",
]
