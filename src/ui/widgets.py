"""
UI 组件模块
"""

import tkinter as tk
from tkinter import ttk
import threading
from typing import Callable, Optional


class StatusIndicator(tk.Canvas):
    """状态指示器 - 圆形指示灯"""
    
    def __init__(self, parent, size=20, **kwargs):
        super().__init__(parent, width=size, height=size, bg=kwargs.pop('bg', 'white'), 
                        highlightthickness=0, **kwargs)
        self.size = size
        self.set_status('pending')
    
    def set_status(self, status: str):
        """设置状态: pending(灰), done(绿), error(红), loading(黄)"""
        self.delete("all")
        
        status_colors = {
            'pending': '#cccccc',
            'done': '#00aa00',
            'error': '#ff0000',
            'loading': '#ffaa00'
        }
        
        color = status_colors.get(status, '#cccccc')
        self.create_oval(2, 2, self.size-2, self.size-2, fill=color, outline='')


class TaskTab(ttk.Frame):
    """单个任务标签页"""
    
    def __init__(self, parent, title: str, task_func: Callable, check_func: Optional[Callable] = None, 
                 need_zip: bool = False, **kwargs):
        super().__init__(parent, **kwargs)
        
        self.title = title
        self.task_func = task_func
        self.check_func = check_func
        self.need_zip = need_zip
        self.is_running = False
        self.zip_path = None
        
        self._setup_ui()
        self._check_status()
    
    def _setup_ui(self):
        """构建界面"""
        from tkinter import filedialog, messagebox
        
        # 标题框架
        title_frame = ttk.Frame(self)
        title_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # 状态指示灯
        self.status_indicator = StatusIndicator(title_frame, size=15)
        self.status_indicator.pack(side=tk.LEFT, padx=(0, 10))
        
        # 标题标签
        self.title_label = ttk.Label(title_frame, text=self.title, font=('Arial', 12, 'bold'))
        self.title_label.pack(side=tk.LEFT)
        
        # 状态文本
        self.status_text = ttk.Label(title_frame, text='待检查', foreground='gray')
        self.status_text.pack(side=tk.LEFT, padx=(10, 0))
        
        # 分割线
        ttk.Separator(self, orient=tk.HORIZONTAL).pack(fill=tk.X, padx=10, pady=5)
        
        # 内容框架
        content_frame = ttk.Frame(self)
        content_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 输出日志
        log_label = ttk.Label(content_frame, text='执行日志:', font=('Arial', 10))
        log_label.pack(anchor=tk.W)
        
        # 创建文本框用于显示日志
        self.log_text = tk.Text(content_frame, height=8, width=60, 
                               font=('Courier', 9), wrap=tk.WORD)
        self.log_text.pack(fill=tk.BOTH, expand=True, pady=(5, 10))
        
        # 添加滚动条
        scrollbar = ttk.Scrollbar(self.log_text)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.log_text.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.log_text.yview)
        
        # 按钮框架
        button_frame = ttk.Frame(content_frame)
        button_frame.pack(fill=tk.X, pady=10)
        
        # 如果需要选择 zip，添加文件选择按钮
        if self.need_zip:
            self.file_button = ttk.Button(button_frame, text='📁 选择字体包', 
                                         command=self._select_zip)
            self.file_button.pack(side=tk.LEFT, padx=5)
            
            self.file_label = ttk.Label(button_frame, text='未选择文件', foreground='gray')
            self.file_label.pack(side=tk.LEFT, padx=10)
        
        # 执行按钮
        self.execute_button = ttk.Button(button_frame, text='▶ 执行', command=self._execute)
        self.execute_button.pack(side=tk.LEFT, padx=5)
        
        # 清空日志按钮
        clear_button = ttk.Button(button_frame, text='🗑 清空日志', 
                                 command=lambda: self.log_text.delete('1.0', tk.END))
        clear_button.pack(side=tk.LEFT, padx=5)
    
    def _select_zip(self):
        """选择 zip 文件"""
        from tkinter import filedialog
        
        zip_file = filedialog.askopenfilename(
            title='选择字体包',
            filetypes=[('ZIP 文件', '*.zip'), ('所有文件', '*.*')]
        )
        if zip_file:
            self.zip_path = zip_file
            import os
            filename = os.path.basename(zip_file)
            self.file_label.config(text=f'✓ {filename}', foreground='green')
    
    def _execute(self):
        """执行任务"""
        from tkinter import messagebox
        
        if self.is_running:
            messagebox.showwarning('警告', '任务正在执行中，请稍候...')
            return
        
        # 需要 zip 但未选择
        if self.need_zip and not self.zip_path:
            messagebox.showerror('错误', '请先选择字体包文件')
            return
        
        # 在新线程中执行任务，避免冻结 UI
        self.is_running = True
        self.execute_button.config(state=tk.DISABLED)
        thread = threading.Thread(target=self._run_task)
        thread.daemon = True
        thread.start()
    
    def _run_task(self):
        """在后台线程执行任务"""
        try:
            self.log_text.delete('1.0', tk.END)
            self.status_indicator.set_status('loading')
            self.status_text.config(text='执行中...', foreground='orange')
            
            # 重定向 print 输出到 log_text
            import io
            import sys
            
            old_stdout = sys.stdout
            sys.stdout = io.StringIO()
            
            try:
                if self.need_zip:
                    success, msg = self.task_func(self.zip_path)
                else:
                    success, msg = self.task_func()
                
                output = sys.stdout.getvalue()
            finally:
                sys.stdout = old_stdout
            
            # 更新 UI
            self.log_text.insert(tk.END, output)
            self.log_text.insert(tk.END, f"\n{msg}\n")
            
            if success:
                self.status_indicator.set_status('done')
                self.status_text.config(text='✓ 完成', foreground='green')
            else:
                self.status_indicator.set_status('error')
                self.status_text.config(text='✗ 失败', foreground='red')
        
        except Exception as e:
            self.log_text.insert(tk.END, f"❌ 异常: {str(e)}\n")
            self.status_indicator.set_status('error')
            self.status_text.config(text='✗ 异常', foreground='red')
        
        finally:
            self.is_running = False
            self.execute_button.config(state=tk.NORMAL)
    
    def _check_status(self):
        """检查任务状态"""
        if self.check_func:
            is_done = self.check_func()
            if is_done:
                self.status_indicator.set_status('done')
                self.status_text.config(text='✓ 已完成', foreground='green')
                self.execute_button.config(state=tk.DISABLED)
            else:
                self.status_indicator.set_status('pending')
                self.status_text.config(text='待执行', foreground='gray')
