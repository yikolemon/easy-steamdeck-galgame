"""
SteamDeck 中文环境配置工具 - 应用入口
支持 TUI（终端界面）和 GUI（图形界面）两种模式
"""

import sys
import logging
import argparse
import os

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description='SteamDeck 中文环境配置工具',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python3 run.py              # 默认启动 TUI 模式
  python3 run.py --gui        # 启动 GUI 模式（需要 X11/Wayland）
  python3 run.py --tui        # 显式启动 TUI 模式
        """
    )
    
    # 界面模式参数
    mode_group = parser.add_mutually_exclusive_group()
    mode_group.add_argument(
        '--gui',
        action='store_true',
        help='使用 GUI 模式（图形界面）'
    )
    mode_group.add_argument(
        '--tui',
        action='store_true',
        help='使用 TUI 模式（终端界面）'
    )
    
    args = parser.parse_args()
    
    # 决定使用哪种模式
    use_gui = args.gui
    use_tui = args.tui
    
    # 如果没有指定，尝试自动检测（优先使用 TUI）
    if not use_gui and not use_tui:
        # 默认使用 TUI（更适合 SteamDeck）
        use_tui = True
    
    # 启动应用
    if use_tui:
        try:
            from src.tui.main import TUIApplication
            app = TUIApplication()
            app.run()
        except ImportError as e:
            print(f"错误: 无法导入 TUI 模块: {e}")
            print("请确保已安装所有依赖: pip install -r requirements.txt")
            sys.exit(1)
        except Exception as e:
            print(f"TUI 启动失败: {e}")
            sys.exit(1)
    else:
        # 启动 GUI 模式
        try:
            from src.ui import MainWindow
            app = MainWindow()
            app.mainloop()
        except ImportError as e:
            print(f"错误: 无法导入 GUI 模块: {e}")
            print("请确保已安装 tkinter: apt-get install python3-tk")
            sys.exit(1)
        except Exception as e:
            print(f"GUI 启动失败: {e}")
            sys.exit(1)


if __name__ == '__main__':
    main()
