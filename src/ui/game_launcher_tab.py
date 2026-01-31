"""
游戏启动选项配置 Tab
"""

import tkinter as tk
from tkinter import ttk, messagebox
from src.core import get_zh_locale_preset, copy_zh_command_to_clipboard


class GameLauncherTab(ttk.Frame):
    """游戏启动选项配置标签页"""
    
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self._setup_ui()
    
    def _setup_ui(self):
        """构建界面"""
        # 标题
        title_label = ttk.Label(self, text='功能 3：非 Steam 游戏启动选项配置', 
                               font=('Arial', 12, 'bold'))
        title_label.pack(anchor=tk.W, padx=10, pady=10)
        
        # 分割线
        ttk.Separator(self, orient=tk.HORIZONTAL).pack(fill=tk.X, padx=10, pady=5)
        
        # 内容框架
        content_frame = ttk.Frame(self)
        content_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 说明文本
        info_text = """
功能说明：
为非 Steam 游戏配置中文启动选项。这样可以使游戏在启动时使用中文环境。

使用方法：
1. 在 Steam 中添加非 Steam 游戏
2. 进入游戏属性 → 启动选项
3. 复制下面的命令并粘贴到启动选项中

中文启动命令：
"""
        
        info_label = ttk.Label(content_frame, text=info_text, justify=tk.LEFT)
        info_label.pack(anchor=tk.W, pady=(0, 10))
        
        # 命令显示框
        command_frame = ttk.LabelFrame(content_frame, text='启动选项命令', padding=10)
        command_frame.pack(fill=tk.X, pady=10)
        
        # 创建只读的文本框显示命令
        self.command_text = tk.Text(command_frame, height=3, width=60, 
                                   font=('Courier', 10), wrap=tk.WORD)
        self.command_text.pack(fill=tk.X)
        
        # 设置为只读
        self.command_text.insert('1.0', get_zh_locale_preset())
        self.command_text.config(state=tk.DISABLED)
        
        # 按钮框架
        button_frame = ttk.Frame(content_frame)
        button_frame.pack(fill=tk.X, pady=10)
        
        # 复制按钮
        copy_button = ttk.Button(button_frame, text='📋 复制命令', command=self._copy_command)
        copy_button.pack(side=tk.LEFT, padx=5)
        
        # 提示文本
        tip_label = ttk.Label(content_frame, text="""
提示：
• 每次添加新的非 Steam 游戏时，可以使用这个命令
• 命令会设置游戏的环境变量以使用中文
• %command% 会被替换为实际的游戏启动命令
        """, foreground='gray', justify=tk.LEFT)
        tip_label.pack(anchor=tk.W, pady=10)
    
    def _copy_command(self):
        """复制命令到剪贴板"""
        if copy_zh_command_to_clipboard():
            messagebox.showinfo('成功', '命令已复制到剪贴板！')
        else:
            # 如果剪贴板操作失败，提供另一种方式
            command = get_zh_locale_preset()
            messagebox.showinfo('信息', f'请手动复制以下命令：\n\n{command}')
