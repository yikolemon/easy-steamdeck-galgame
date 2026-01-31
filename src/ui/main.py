"""
UI 主窗口
"""

import tkinter as tk
from tkinter import ttk
from src.core.installers import (
    setup_locale,
    check_locale_status,
)
from .widgets import TaskTab
from .font_installer_tab import FontInstallerTab
from .game_launcher_tab import GameLauncherTab


class MainWindow(tk.Tk):
    """主窗口"""
    
    def __init__(self):
        super().__init__()
        
        self.title('SteamDeck 中文环境配置工具')
        self.geometry('700x500')
        
        # 设置窗口图标和样式
        self.resizable(True, True)
        
        # 设置样式
        style = ttk.Style()
        style.theme_use('clam')
        
        self._setup_ui()
    
    def _setup_ui(self):
        """构建主界面"""
        # 创建 notebook（标签页容器）
        notebook = ttk.Notebook(self)
        notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 功能 1: 中文 locale 安装
        tab1 = TaskTab(
            notebook,
            title='功能 1：中文 Locale 安装',
            task_func=setup_locale,
            check_func=check_locale_status
        )
        notebook.add(tab1, text='📝 中文 Locale')
        
        # 功能 2: 中文字体安装（新的可下载版本）
        tab2 = FontInstallerTab(notebook)
        notebook.add(tab2, text='🔤 中文字体')
        
        # 功能 3: 游戏启动选项配置
        tab3 = GameLauncherTab(notebook)
        notebook.add(tab3, text='🎮 游戏启动选项')
        
        # 底部状态栏
        status_frame = ttk.Frame(self)
        status_frame.pack(fill=tk.X, side=tk.BOTTOM, padx=5, pady=5)
        
        status_label = ttk.Label(status_frame, text='✓ 准备就绪', foreground='green')
        status_label.pack(side=tk.LEFT)
        
        # 关于信息
        about_label = ttk.Label(status_frame, text='SteamDeck GAL 中文环境配置工具 v1.0', 
                               foreground='gray', font=('Arial', 8))
        about_label.pack(side=tk.RIGHT)


if __name__ == '__main__':
    app = MainWindow()
    app.mainloop()
