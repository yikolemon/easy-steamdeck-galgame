"""
SteamDeck 中文环境配置工具 - 应用入口
"""

import sys
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

from src.ui import MainWindow


if __name__ == '__main__':
    app = MainWindow()
    app.mainloop()
