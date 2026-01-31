"""
SteamDeck 中文环境配置工具 - 应用入口
TUI（终端界面）模式
"""

import sys
import logging
import os  # 新增导入

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def ensure_root():
    """检测权限，如果不是 root 则尝试通过 sudo 重启"""
    # UID 0 代表 root 用户
    if os.geteuid() != 0:
        print("检测到当前权限不足，正在尝试通过 sudo 提升权限...")
        try:
            # sys.executable 是当前 python 解释器的路径
            # sys.argv 是传递给脚本的所有参数
            args = ['sudo', sys.executable] + sys.argv

            # os.execvp 会用新进程替换当前进程
            # 这样执行后，后续的代码将以 root 身份运行
            os.execvp('sudo', args)
        except Exception as e:
            print(f"无法获取 sudo 权限: {e}")
            sys.exit(1)

def main():
    """主函数"""
    # 在导入 TUI 模块前先检查并提升权限
    ensure_root()

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