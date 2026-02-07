"""
SteamDeck 中文环境配置工具 - 应用入口
GUI（图形界面）模式

Note: This application runs as a normal user.
Sudo is only used when needed for specific operations like:
- Installing locales (requires system file modification)
- Installing fonts (requires writing to /usr/share/fonts)
"""

import sys
import logging
import os

# 根据 BUILD_TYPE 环境变量设置日志级别
# 支持: debug, release (默认)
build_type = os.environ.get("BUILD_TYPE", "release").lower()
log_level = logging.DEBUG if build_type == "debug" else logging.INFO

# 配置日志
logging.basicConfig(level=log_level, format="%(asctime)s - %(levelname)s - %(message)s")

# 记录构建类型
logger = logging.getLogger(__name__)
logger.debug(f"Application running in {build_type.upper()} mode")


def main():
    """主函数"""
    try:
        from src.gui.main import GUIApplication

        app = GUIApplication()
        app.mainloop()
    except ImportError as e:
        print(f"错误: 无法导入 GUI 模块: {e}")
        print("请确保已安装所有依赖: pip install -r requirements.txt")
        sys.exit(1)
    except Exception as e:
        print(f"启动失败: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
