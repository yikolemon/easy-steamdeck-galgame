"""
SteamDeck 中文环境配置工具 - 应用入口
TUI（终端界面）模式
"""

import sys
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)


def main():
    """主函数"""
    try:
        from src.tui.main import TUIApplication
        app = TUIApplication()
        app.run()
    except ImportError as e:
        print(f"错误: 无法导入 TUI 模块: {e}")
        print("请确保已安装所有依赖: pip install -r requirements.txt")
        sys.exit(1)
    except Exception as e:
        print(f"启动失败: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
