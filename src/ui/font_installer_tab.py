"""
字体安装 Tab - 支持本地和远程下载
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import threading
from typing import Optional
import io
import sys
import os

from src.core.installers import (
    setup_fonts,
    download_and_install_fonts,
    list_available_fonts,
    get_fonts_release_info,
)


class FontInstallerTab(ttk.Frame):
    """字体安装标签页 - 支持本地和远程下载"""
    
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        
        self.is_running = False
        self.zip_path: Optional[str] = None
        self.selected_asset = None
        self.available_fonts = []
        
        self._setup_ui()
        self._load_fonts_list()
    
    def _setup_ui(self):
        """构建界面"""
        # 标题
        title_label = ttk.Label(self, text='功能 2：中文字体安装', 
                               font=('Arial', 12, 'bold'))
        title_label.pack(anchor=tk.W, padx=10, pady=10)
        
        # 分割线
        ttk.Separator(self, orient=tk.HORIZONTAL).pack(fill=tk.X, padx=10, pady=5)
        
        # 内容框架
        content_frame = ttk.Frame(self)
        content_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 选择模式框架
        mode_frame = ttk.LabelFrame(content_frame, text='选择安装方式', padding=10)
        mode_frame.pack(fill=tk.X, pady=(0, 10))
        
        # 两种模式
        self.mode_var = tk.StringVar(value="remote")
        
        ttk.Radiobutton(mode_frame, text='📡 从 GitHub 下载', value='remote',
                       variable=self.mode_var, command=self._on_mode_changed).pack(anchor=tk.W, pady=5)
        ttk.Radiobutton(mode_frame, text='📂 使用本地文件', value='local',
                       variable=self.mode_var, command=self._on_mode_changed).pack(anchor=tk.W, pady=5)
        
        # 远程下载框架
        self.remote_frame = ttk.LabelFrame(content_frame, text='可用的字体包', padding=10)
        self.remote_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # 刷新按钮
        refresh_btn = ttk.Button(self.remote_frame, text='🔄 刷新列表',
                                command=self._load_fonts_list)
        refresh_btn.pack(side=tk.LEFT, padx=5, pady=5)
        
        # Release 信息标签
        self.release_info_label = ttk.Label(self.remote_frame, text='', foreground='gray')
        self.release_info_label.pack(anchor=tk.W, padx=5)
        
        # 字体列表 Frame
        list_frame = ttk.Frame(self.remote_frame)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Listbox 用于显示字体包
        scrollbar = ttk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.fonts_listbox = tk.Listbox(list_frame, yscrollcommand=scrollbar.set,
                                        height=6, font=('Courier', 9))
        self.fonts_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.fonts_listbox.yview)
        
        self.fonts_listbox.bind('<<ListboxSelect>>', self._on_font_selected)
        
        # 本地文件框架
        self.local_frame = ttk.LabelFrame(content_frame, text='本地文件', padding=10)
        self.local_frame.pack(fill=tk.X, pady=(0, 10))
        
        # 文件选择按钮和标签
        btn_frame = ttk.Frame(self.local_frame)
        btn_frame.pack(fill=tk.X, pady=5)
        
        self.file_button = ttk.Button(btn_frame, text='📁 选择字体包',
                                     command=self._select_zip)
        self.file_button.pack(side=tk.LEFT, padx=5)
        
        self.file_label = ttk.Label(btn_frame, text='未选择文件', foreground='gray')
        self.file_label.pack(side=tk.LEFT, padx=10)
        
        # 默认隐藏本地框架
        self.local_frame.pack_forget()
        
        # 日志框架
        log_label = ttk.Label(content_frame, text='执行日志:', font=('Arial', 10))
        log_label.pack(anchor=tk.W)
        
        self.log_text = tk.Text(content_frame, height=8, width=60,
                               font=('Courier', 9), wrap=tk.WORD)
        self.log_text.pack(fill=tk.BOTH, expand=True, pady=(5, 10))
        
        # 添加滚动条
        log_scrollbar = ttk.Scrollbar(self.log_text)
        log_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.log_text.config(yscrollcommand=log_scrollbar.set)
        log_scrollbar.config(command=self.log_text.yview)
        
        # 按钮框架
        button_frame = ttk.Frame(content_frame)
        button_frame.pack(fill=tk.X, pady=10)
        
        self.execute_button = ttk.Button(button_frame, text='▶ 执行',
                                        command=self._execute)
        self.execute_button.pack(side=tk.LEFT, padx=5)
        
        clear_button = ttk.Button(button_frame, text='🗑 清空日志',
                                 command=lambda: self.log_text.delete('1.0', tk.END))
        clear_button.pack(side=tk.LEFT, padx=5)
    
    def _on_mode_changed(self):
        """模式切换回调"""
        if self.mode_var.get() == "remote":
            self.local_frame.pack_forget()
            self.remote_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        else:
            self.remote_frame.pack_forget()
            self.local_frame.pack(fill=tk.X, pady=(0, 10))
    
    def _load_fonts_list(self):
        """加载字体列表"""
        try:
            self.fonts_listbox.delete(0, tk.END)
            self.fonts_listbox.insert(tk.END, "正在加载...")
            self.update()
            
            # 获取 Release 信息
            info = get_fonts_release_info()
            if info:
                self.release_info_label.config(
                    text=f"最新版本: {info.get('version', 'unknown')} | "
                         f"资源数: {info.get('assets_count', 0)}"
                )
            
            # 获取可用字体
            success, assets = list_available_fonts()
            if success and assets:
                self.fonts_listbox.delete(0, tk.END)
                self.available_fonts = assets
                for i, asset in enumerate(assets):
                    size_mb = asset.get_size_mb()
                    self.fonts_listbox.insert(tk.END, f"{asset.name} ({size_mb:.1f} MB)")
                self.fonts_listbox.selection_set(0)
                self._on_font_selected(None)
            else:
                self.fonts_listbox.delete(0, tk.END)
                self.fonts_listbox.insert(tk.END, "❌ 无法获取字体列表，请检查网络连接")
                self.available_fonts = []
        
        except Exception as e:
            messagebox.showerror('错误', f'加载字体列表失败: {str(e)}')
    
    def _on_font_selected(self, event):
        """字体选择回调"""
        try:
            selection = self.fonts_listbox.curselection()
            if selection:
                idx = selection[0]
                if idx < len(self.available_fonts):
                    self.selected_asset = self.available_fonts[idx]
        except Exception as e:
            print(f"选择字体失败: {e}")
    
    def _select_zip(self):
        """选择本地 zip 文件"""
        zip_file = filedialog.askopenfilename(
            title='选择字体包',
            filetypes=[('ZIP 文件', '*.zip'), ('所有文件', '*.*')]
        )
        if zip_file:
            self.zip_path = zip_file
            filename = os.path.basename(zip_file) if zip_file else ''
            self.file_label.config(text=f'✓ {filename}', foreground='green')
    
    def _execute(self):
        """执行任务"""
        if self.is_running:
            messagebox.showwarning('警告', '任务正在执行中，请稍候...')
            return
        
        mode = self.mode_var.get()
        
        if mode == "remote":
            if not self.selected_asset:
                messagebox.showerror('错误', '请先选择要下载的字体包')
                return
        else:
            if not self.zip_path:
                messagebox.showerror('错误', '请先选择本地字体包文件')
                return
        
        # 在新线程中执行任务
        self.is_running = True
        self.execute_button.config(state=tk.DISABLED)
        thread = threading.Thread(target=self._run_task, args=(mode,))
        thread.daemon = True
        thread.start()
    
    def _run_task(self, mode: str):
        """在后台线程执行任务"""
        try:
            self.log_text.delete('1.0', tk.END)
            
            # 重定向 print 输出到 log_text
            old_stdout = sys.stdout
            sys.stdout = io.StringIO()
            
            try:
                if mode == "remote":
                    success, msg = download_and_install_fonts(self.selected_asset)
                else:
                    success, msg = setup_fonts(self.zip_path)
                
                output = sys.stdout.getvalue()
            finally:
                sys.stdout = old_stdout
            
            # 更新 UI
            self.log_text.insert(tk.END, output)
            self.log_text.insert(tk.END, f"\n{msg}\n")
            
            if success:
                messagebox.showinfo('成功', '字体安装完成！')
            else:
                messagebox.showerror('失败', msg)
        
        except Exception as e:
            self.log_text.insert(tk.END, f"❌ 异常: {str(e)}\n")
            messagebox.showerror('异常', f'执行过程出错: {str(e)}')
        
        finally:
            self.is_running = False
            self.execute_button.config(state=tk.NORMAL)
