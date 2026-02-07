"""
GUI Main Application - Tkinter-based graphical interface
"""

import os
import sys
import threading
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from typing import Optional, Callable

from src.core.installers import (
    setup_locale,
    check_locale_status,
    setup_fonts,
    check_fonts_status,
    get_fonts_count,
    list_available_fonts,
    download_and_install_fonts,
)
from src.utils.locale import t, is_chinese
from src.core.game_launcher import get_locale_command
from src.config import Config, TargetLanguage
from src.core.steam_manager import (
    SteamManager,
    get_game_search_paths,
    add_game_search_path,
    remove_game_search_path,
)


class ScrollableFrame(ttk.Frame):
    """A scrollable frame container that can be used in dialogs"""

    def __init__(self, container, *args, **kwargs):
        super().__init__(container, *args, **kwargs)

        # Create canvas and scrollbar
        self.canvas = tk.Canvas(self, highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(
            self, orient="vertical", command=self.canvas.yview
        )
        self.scrollable_frame = ttk.Frame(self.canvas)

        # Configure scrolling
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")),
        )

        self.canvas_frame = self.canvas.create_window(
            (0, 0), window=self.scrollable_frame, anchor="nw"
        )
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        # Bind canvas resize to adjust frame width
        self.canvas.bind("<Configure>", self._on_canvas_configure)

        # Pack canvas and scrollbar
        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        # Bind mousewheel
        self.scrollable_frame.bind("<Enter>", self._bind_mousewheel)
        self.scrollable_frame.bind("<Leave>", self._unbind_mousewheel)

    def _on_canvas_configure(self, event):
        """Adjust the scrollable frame width to match canvas"""
        self.canvas.itemconfig(self.canvas_frame, width=event.width)

    def _bind_mousewheel(self, event):
        """Bind mousewheel when mouse enters"""
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)
        self.canvas.bind_all("<Button-4>", self._on_mousewheel)
        self.canvas.bind_all("<Button-5>", self._on_mousewheel)

    def _unbind_mousewheel(self, event):
        """Unbind mousewheel when mouse leaves"""
        self.canvas.unbind_all("<MouseWheel>")
        self.canvas.unbind_all("<Button-4>")
        self.canvas.unbind_all("<Button-5>")

    def _on_mousewheel(self, event):
        """Handle mousewheel scroll"""
        if event.num == 4:  # Linux scroll up
            self.canvas.yview_scroll(-1, "units")
        elif event.num == 5:  # Linux scroll down
            self.canvas.yview_scroll(1, "units")
        else:  # Windows/macOS
            self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")


class GUIApplication:
    """Main GUI Application using Tkinter"""

    def __init__(self):
        self.root = tk.Tk()
        self.root.title("SteamDeck Galgame Config Tool")
        self.root.geometry("800x600")
        self.root.minsize(700, 500)

        # Target language
        self.target_language: Optional[str] = Config.get_target_language()

        # Setup style
        self._setup_style()

        # Create main UI
        self._create_ui()

        # Check if language needs to be selected
        if not self.target_language:
            self.root.after(100, self._show_language_dialog)

    def _setup_style(self):
        """Setup ttk styles"""
        style = ttk.Style()

        # Try to use a nicer theme
        available_themes = style.theme_names()
        for theme in ["clam", "alt", "default"]:
            if theme in available_themes:
                style.theme_use(theme)
                break

        # Configure styles
        style.configure("Title.TLabel", font=("sans-serif", 16, "bold"))
        style.configure("Header.TLabel", font=("sans-serif", 12, "bold"))
        style.configure("Status.TLabel", font=("sans-serif", 10))
        style.configure("Big.TButton", font=("sans-serif", 11), padding=10)

    def _create_ui(self):
        """Create main UI layout"""
        # Main container
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Header
        header_frame = ttk.Frame(main_frame)
        header_frame.pack(fill=tk.X, pady=(0, 10))

        title_text = (
            "SteamDeck 游戏环境配置工具"
            if is_chinese()
            else "SteamDeck Game Environment Config Tool"
        )
        title_label = ttk.Label(header_frame, text=title_text, style="Title.TLabel")
        title_label.pack(side=tk.LEFT)

        # Language button
        lang_btn_text = "切换语言" if is_chinese() else "Change Language"
        self.lang_btn = ttk.Button(
            header_frame, text=lang_btn_text, command=self._show_language_dialog
        )
        self.lang_btn.pack(side=tk.RIGHT)

        # Status bar
        self._create_status_bar(main_frame)

        # Notebook for tabs
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True, pady=10)

        # Create tabs (Steam Games first as default)
        self._create_steam_tab()
        self._create_locale_tab()
        self._create_font_tab()
        self._create_launcher_tab()

        # Log output area
        self._create_log_area(main_frame)

    def _create_status_bar(self, parent):
        """Create status bar showing current states"""
        status_frame = ttk.LabelFrame(
            parent, text=t("status", "系统状态", "System Status"), padding="5"
        )
        status_frame.pack(fill=tk.X, pady=(0, 5))

        # Status labels
        status_grid = ttk.Frame(status_frame)
        status_grid.pack(fill=tk.X)

        # Target language
        ttk.Label(
            status_grid, text=t("target_lang", "目标语言:", "Target Language:")
        ).grid(row=0, column=0, sticky=tk.W, padx=5)
        self.lang_status = ttk.Label(status_grid, text="--", style="Status.TLabel")
        self.lang_status.grid(row=0, column=1, sticky=tk.W, padx=5)

        # Locale status
        ttk.Label(status_grid, text=t("locale_status", "语言环境:", "Locale:")).grid(
            row=0, column=2, sticky=tk.W, padx=5
        )
        self.locale_status = ttk.Label(status_grid, text="--", style="Status.TLabel")
        self.locale_status.grid(row=0, column=3, sticky=tk.W, padx=5)

        # Font status
        ttk.Label(status_grid, text=t("font_status", "字体:", "Fonts:")).grid(
            row=0, column=4, sticky=tk.W, padx=5
        )
        self.font_status = ttk.Label(status_grid, text="--", style="Status.TLabel")
        self.font_status.grid(row=0, column=5, sticky=tk.W, padx=5)

        # Refresh button
        refresh_btn = ttk.Button(
            status_grid,
            text=t("refresh", "刷新", "Refresh"),
            command=self._refresh_status,
        )
        refresh_btn.grid(row=0, column=6, padx=10)

        # Initial refresh
        self.root.after(200, self._refresh_status)

    def _refresh_status(self):
        """Refresh status display"""
        # Target language
        if self.target_language:
            lang_name = TargetLanguage.get_name(
                self.target_language, "zh" if is_chinese() else "en"
            )
            self.lang_status.config(text=lang_name, foreground="blue")
        else:
            self.lang_status.config(
                text=t("not_set", "未设置", "Not Set"), foreground="gray"
            )

        # Locale status
        if self.target_language:
            locale_code = TargetLanguage.get_locale(self.target_language)
            if check_locale_status(locale_code):
                self.locale_status.config(text="✓ OK", foreground="green")
            else:
                self.locale_status.config(
                    text="✗ " + t("not_installed", "未安装", "Not Installed"),
                    foreground="red",
                )
        else:
            self.locale_status.config(text="--", foreground="gray")

        # Font status
        if check_fonts_status():
            count = get_fonts_count()
            self.font_status.config(text=f"✓ OK ({count})", foreground="green")
        else:
            self.font_status.config(
                text="✗ " + t("not_installed", "未安装", "Not Installed"),
                foreground="red",
            )

    def _create_locale_tab(self):
        """Create locale installation tab"""
        tab = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(tab, text=t("locale_tab", "语言环境", "Locale"))

        # Description
        desc_text = t(
            "locale_desc",
            "安装系统语言环境，使游戏能够正确显示中文/日文。\n此操作需要root权限，将会修改系统文件。",
            "Install system locale to display Chinese/Japanese in games.\nThis requires root permission and will modify system files.",
        )
        ttk.Label(tab, text=desc_text, wraplength=600).pack(anchor=tk.W, pady=10)

        # Steps description
        steps_frame = ttk.LabelFrame(
            tab, text=t("steps", "操作步骤", "Steps"), padding="10"
        )
        steps_frame.pack(fill=tk.X, pady=10)

        steps = [
            t("step1", "1. 禁用 SteamOS 只读模式", "1. Disable SteamOS read-only mode"),
            t("step2", "2. 初始化 pacman 密钥", "2. Initialize pacman keys"),
            t("step3", "3. 启用目标语言环境", "3. Enable target locale"),
            t("step4", "4. 生成语言环境", "4. Generate locale"),
            t("step5", "5. 恢复 SteamOS 只读模式", "5. Restore SteamOS read-only mode"),
        ]
        for step in steps:
            ttk.Label(steps_frame, text=step).pack(anchor=tk.W)

        # Install button
        btn_frame = ttk.Frame(tab)
        btn_frame.pack(pady=20)

        install_btn = ttk.Button(
            btn_frame,
            text=t("install_locale", "安装语言环境", "Install Locale"),
            style="Big.TButton",
            command=self._install_locale,
        )
        install_btn.pack()

    def _create_font_tab(self):
        """Create font installation tab"""
        tab = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(tab, text=t("font_tab", "字体安装", "Fonts"))

        # Description
        desc_text = t(
            "font_desc",
            "安装中文/日文字体，确保游戏能够正确显示文字。",
            "Install Chinese/Japanese fonts for proper text display in games.",
        )
        ttk.Label(tab, text=desc_text, wraplength=600).pack(anchor=tk.W, pady=10)

        # Installation options
        options_frame = ttk.LabelFrame(
            tab,
            text=t("install_method", "安装方式", "Installation Method"),
            padding="10",
        )
        options_frame.pack(fill=tk.X, pady=10)

        # GitHub download
        github_frame = ttk.Frame(options_frame)
        github_frame.pack(fill=tk.X, pady=5)
        ttk.Label(
            github_frame, text=t("from_github", "从 GitHub 下载:", "From GitHub:")
        ).pack(side=tk.LEFT)
        ttk.Button(
            github_frame,
            text=t("download", "下载安装", "Download & Install"),
            command=self._install_fonts_github,
        ).pack(side=tk.LEFT, padx=10)

        # Local file
        local_frame = ttk.Frame(options_frame)
        local_frame.pack(fill=tk.X, pady=5)
        ttk.Label(
            local_frame, text=t("from_local", "从本地文件:", "From Local File:")
        ).pack(side=tk.LEFT)
        ttk.Button(
            local_frame,
            text=t("browse", "浏览...", "Browse..."),
            command=self._install_fonts_local,
        ).pack(side=tk.LEFT, padx=10)

        # Default path
        default_frame = ttk.Frame(options_frame)
        default_frame.pack(fill=tk.X, pady=5)
        ttk.Label(
            default_frame, text=t("default_path", "默认路径:", "Default Path:")
        ).pack(side=tk.LEFT)

        self.default_path_var = tk.StringVar(
            value=Config.get_default_font_path() or t("not_set", "未设置", "Not Set")
        )
        ttk.Label(
            default_frame, textvariable=self.default_path_var, foreground="blue"
        ).pack(side=tk.LEFT, padx=5)

        ttk.Button(
            default_frame,
            text=t("set_path", "设置", "Set"),
            command=self._set_default_font_path,
        ).pack(side=tk.LEFT, padx=5)
        ttk.Button(
            default_frame,
            text=t("browse_default", "从默认路径安装", "Install from Default"),
            command=self._install_fonts_default,
        ).pack(side=tk.LEFT, padx=5)

    def _create_launcher_tab(self):
        """Create game launcher options tab"""
        tab = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(tab, text=t("launcher_tab", "启动选项", "Launch Options"))

        # Description
        desc_text = t(
            "launcher_desc",
            "获取游戏启动命令，用于在Steam中配置游戏以使用中文/日文环境。",
            "Get game launch commands to configure games in Steam for Chinese/Japanese environment.",
        )
        ttk.Label(tab, text=desc_text, wraplength=600).pack(anchor=tk.W, pady=10)

        # Launch command display
        cmd_frame = ttk.LabelFrame(
            tab, text=t("launch_cmd", "启动命令", "Launch Command"), padding="10"
        )
        cmd_frame.pack(fill=tk.X, pady=10)

        self.launch_cmd_var = tk.StringVar()
        cmd_entry = ttk.Entry(
            cmd_frame,
            textvariable=self.launch_cmd_var,
            state="readonly",
            font=("monospace", 10),
        )
        cmd_entry.pack(fill=tk.X, pady=5)

        btn_frame = ttk.Frame(cmd_frame)
        btn_frame.pack(fill=tk.X)

        ttk.Button(
            btn_frame,
            text=t("copy", "复制到剪贴板", "Copy to Clipboard"),
            command=self._copy_launch_cmd,
        ).pack(side=tk.LEFT, padx=5)
        ttk.Button(
            btn_frame,
            text=t("refresh_cmd", "刷新", "Refresh"),
            command=self._update_launch_cmd,
        ).pack(side=tk.LEFT, padx=5)

        # Instructions
        instr_frame = ttk.LabelFrame(
            tab, text=t("instructions", "使用说明", "Instructions"), padding="10"
        )
        instr_frame.pack(fill=tk.X, pady=10)

        instructions = [
            t(
                "instr1",
                '1. 在 Steam 中右键点击游戏，选择"属性"',
                '1. Right-click game in Steam, select "Properties"',
            ),
            t(
                "instr2",
                '2. 找到"启动选项"输入框',
                '2. Find "Launch Options" input field',
            ),
            t("instr3", "3. 粘贴上面的命令", "3. Paste the command above"),
            t(
                "instr4",
                "4. 关闭属性窗口并启动游戏",
                "4. Close properties and launch game",
            ),
        ]
        for instr in instructions:
            ttk.Label(instr_frame, text=instr).pack(anchor=tk.W)

        # Update command initially
        self.root.after(300, self._update_launch_cmd)

    def _create_steam_tab(self):
        """Create Steam game management tab"""
        tab = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(tab, text=t("steam_tab", "Steam游戏", "Steam Games"))

        # Description
        desc_text = t(
            "steam_desc",
            "管理由本程序添加到Steam库的游戏。",
            "Manage games added to Steam library by this program.",
        )
        ttk.Label(tab, text=desc_text, wraplength=600).pack(anchor=tk.W, pady=10)

        # Games list section
        games_frame = ttk.LabelFrame(
            tab,
            text=t("managed_games", "已添加的游戏", "Managed Games"),
            padding="10",
        )
        games_frame.pack(fill=tk.BOTH, expand=True, pady=10)

        # Games treeview with scrollbar
        tree_frame = ttk.Frame(games_frame)
        tree_frame.pack(fill=tk.BOTH, expand=True)

        # Scrollbars
        vsb = ttk.Scrollbar(tree_frame, orient="vertical")
        vsb.pack(side=tk.RIGHT, fill=tk.Y)

        hsb = ttk.Scrollbar(tree_frame, orient="horizontal")
        hsb.pack(side=tk.BOTTOM, fill=tk.X)

        # Treeview for games
        columns = ("name", "path", "language")
        self.games_tree = ttk.Treeview(
            tree_frame,
            columns=columns,
            show="headings",
            yscrollcommand=vsb.set,
            xscrollcommand=hsb.set,
            height=8,
        )

        # Configure scrollbars
        vsb.config(command=self.games_tree.yview)
        hsb.config(command=self.games_tree.xview)

        # Column headings
        self.games_tree.heading("name", text=t("game_name", "游戏名称", "Game Name"))
        self.games_tree.heading("path", text=t("game_path", "路径", "Path"))
        self.games_tree.heading("language", text=t("language", "语言", "Language"))

        # Column widths
        self.games_tree.column("name", width=200, minwidth=150)
        self.games_tree.column("path", width=300, minwidth=200)
        self.games_tree.column("language", width=100, minwidth=80)

        self.games_tree.pack(fill=tk.BOTH, expand=True)

        # Game action buttons
        game_btn_frame = ttk.Frame(games_frame)
        game_btn_frame.pack(fill=tk.X, pady=5)

        ttk.Button(
            game_btn_frame,
            text=t("add_game", "添加游戏", "Add Game"),
            command=self._browse_add_game,
        ).pack(side=tk.LEFT, padx=5)

        ttk.Button(
            game_btn_frame,
            text=t("launch_game", "启动游戏", "Launch Game"),
            command=self._launch_selected_game,
        ).pack(side=tk.LEFT, padx=5)

        ttk.Button(
            game_btn_frame,
            text=t("remove_game", "移除游戏", "Remove Game"),
            command=self._remove_selected_game,
        ).pack(side=tk.LEFT, padx=5)

        ttk.Button(
            game_btn_frame,
            text=t("refresh_games", "刷新列表", "Refresh"),
            command=self._refresh_games_list,
        ).pack(side=tk.LEFT, padx=5)

        # Search paths section (collapsed)
        paths_frame = ttk.LabelFrame(
            tab,
            text=t("search_paths", "游戏搜索路径", "Game Search Paths"),
            padding="10",
        )
        paths_frame.pack(fill=tk.X, pady=5)

        # Path listbox with scrollbar
        list_frame = ttk.Frame(paths_frame)
        list_frame.pack(fill=tk.BOTH, expand=True)

        scrollbar = ttk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.paths_listbox = tk.Listbox(
            list_frame, yscrollcommand=scrollbar.set, height=4
        )
        self.paths_listbox.pack(fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.paths_listbox.yview)

        # Path buttons
        path_btn_frame = ttk.Frame(paths_frame)
        path_btn_frame.pack(fill=tk.X, pady=5)

        ttk.Button(
            path_btn_frame,
            text=t("add_path", "添加路径", "Add Path"),
            command=self._add_search_path,
        ).pack(side=tk.LEFT, padx=5)
        ttk.Button(
            path_btn_frame,
            text=t("remove_path", "删除路径", "Remove Path"),
            command=self._remove_search_path,
        ).pack(side=tk.LEFT, padx=5)

        # Initial refresh
        self.root.after(400, self._refresh_games_list)
        self.root.after(400, self._refresh_paths)

    def _create_log_area(self, parent):
        """Create log output area"""
        log_frame = ttk.LabelFrame(
            parent, text=t("log", "操作日志", "Log"), padding="5"
        )
        log_frame.pack(fill=tk.BOTH, expand=True)

        # Text widget with scrollbar
        text_frame = ttk.Frame(log_frame)
        text_frame.pack(fill=tk.BOTH, expand=True)

        scrollbar = ttk.Scrollbar(text_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.log_text = tk.Text(
            text_frame,
            height=8,
            yscrollcommand=scrollbar.set,
            state="disabled",
            wrap=tk.WORD,
            font=("monospace", 9),
        )
        self.log_text.pack(fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.log_text.yview)

        # Configure tags for colors
        self.log_text.tag_configure("info", foreground="black")
        self.log_text.tag_configure("success", foreground="green")
        self.log_text.tag_configure("error", foreground="red")
        self.log_text.tag_configure("warning", foreground="orange")

    def _create_dialog(
        self,
        title: str,
        width: int = 400,
        height: int = 300,
        min_width: int = 300,
        min_height: int = 200,
    ) -> tk.Toplevel:
        """
        Create a dialog window with proper sizing and centering.

        Args:
            title: Dialog title
            width: Preferred width
            height: Preferred height
            min_width: Minimum width
            min_height: Minimum height

        Returns:
            The created Toplevel dialog
        """
        dialog = tk.Toplevel(self.root)
        dialog.title(title)
        dialog.geometry(f"{width}x{height}")
        dialog.minsize(min_width, min_height)
        dialog.transient(self.root)
        dialog.grab_set()

        # Center dialog relative to main window
        dialog.update_idletasks()
        x = self.root.winfo_x() + (self.root.winfo_width() - width) // 2
        y = self.root.winfo_y() + (self.root.winfo_height() - height) // 2
        dialog.geometry(f"+{x}+{y}")

        return dialog

    def _log(self, message: str, level: str = "info"):
        """Add message to log"""
        self.log_text.config(state="normal")
        self.log_text.insert(tk.END, message + "\n", level)
        self.log_text.see(tk.END)
        self.log_text.config(state="disabled")
        self.root.update_idletasks()

    def _show_language_dialog(self):
        """Show language selection dialog"""
        dialog = self._create_dialog(
            title=t("select_lang", "选择目标语言", "Select Target Language"),
            width=350,
            height=200,
            min_width=300,
            min_height=180,
        )

        frame = ttk.Frame(dialog, padding="20")
        frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(
            frame,
            text=t("choose_lang", "请选择目标语言:", "Choose target language:"),
            style="Header.TLabel",
        ).pack(pady=(0, 15))

        lang_var = tk.StringVar(value=self.target_language or TargetLanguage.CHINESE)

        ttk.Radiobutton(
            frame,
            text="简体中文 (Simplified Chinese)",
            variable=lang_var,
            value=TargetLanguage.CHINESE,
        ).pack(anchor=tk.W, pady=2)
        ttk.Radiobutton(
            frame,
            text="日本語 (Japanese)",
            variable=lang_var,
            value=TargetLanguage.JAPANESE,
        ).pack(anchor=tk.W, pady=2)

        def on_confirm():
            self.target_language = lang_var.get()
            Config.set_target_language(self.target_language)
            self._refresh_status()
            self._update_launch_cmd()
            dialog.destroy()
            self._log(
                t(
                    "lang_set",
                    f"目标语言已设置为: {TargetLanguage.get_name(self.target_language, 'zh')}",
                    f"Target language set to: {TargetLanguage.get_name(self.target_language, 'en')}",
                ),
                "success",
            )

        btn_frame = ttk.Frame(frame)
        btn_frame.pack(fill=tk.X, pady=(20, 0))

        ttk.Button(
            btn_frame, text=t("confirm", "确认", "Confirm"), command=on_confirm
        ).pack(side=tk.LEFT, padx=5)
        ttk.Button(
            btn_frame, text=t("cancel", "取消", "Cancel"), command=dialog.destroy
        ).pack(side=tk.LEFT, padx=5)

    def _install_locale(self):
        """Install locale"""
        if not self.target_language:
            messagebox.showwarning(
                t("warning", "警告", "Warning"),
                t(
                    "select_lang_first",
                    "请先选择目标语言",
                    "Please select target language first",
                ),
            )
            self._show_language_dialog()
            return

        locale_code = TargetLanguage.get_locale(self.target_language)

        # Check if already installed
        if check_locale_status(locale_code):
            messagebox.showinfo(
                t("info", "提示", "Info"),
                t("locale_installed", "语言环境已安装", "Locale already installed"),
            )
            return

        # Confirm
        if not messagebox.askyesno(
            t("confirm", "确认", "Confirm"),
            t(
                "confirm_locale",
                "此操作需要root权限，是否继续?",
                "This requires root permission. Continue?",
            ),
        ):
            return

        self._log(
            t("installing_locale", "正在安装语言环境...", "Installing locale..."),
            "info",
        )

        def task():
            try:
                success, msg = setup_locale(locale_code)
                self.root.after(0, lambda: self._on_task_complete(success, msg))
            except Exception as e:
                self.root.after(0, lambda: self._on_task_complete(False, str(e)))

        threading.Thread(target=task, daemon=True).start()

    def _on_task_complete(self, success: bool, message: str):
        """Handle task completion"""
        if success:
            self._log(message, "success")
            messagebox.showinfo(t("success", "成功", "Success"), message)
        else:
            self._log(message, "error")
            messagebox.showerror(t("error", "错误", "Error"), message)
        self._refresh_status()

    def _install_fonts_github(self):
        """Install fonts from GitHub"""
        self._log(
            t(
                "fetching_fonts",
                "正在获取可用字体列表...",
                "Fetching available fonts...",
            ),
            "info",
        )

        def fetch_and_show():
            try:
                success, assets = list_available_fonts()
                if not success or not assets:
                    self.root.after(
                        0,
                        lambda: self._log(
                            t(
                                "fetch_failed",
                                "获取字体列表失败",
                                "Failed to fetch font list",
                            ),
                            "error",
                        ),
                    )
                    return

                self.root.after(0, lambda: self._show_font_selection(assets))
            except Exception as e:
                self.root.after(0, lambda: self._log(f"Error: {str(e)}", "error"))

        threading.Thread(target=fetch_and_show, daemon=True).start()

    def _show_font_selection(self, assets):
        """Show font selection dialog"""
        dialog = tk.Toplevel(self.root)
        dialog.title(t("select_font", "选择字体包", "Select Font Package"))
        dialog.geometry("500x300")
        dialog.transient(self.root)
        dialog.grab_set()

        frame = ttk.Frame(dialog, padding="10")
        frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(
            frame,
            text=t("available_fonts", "可用字体包:", "Available font packages:"),
            style="Header.TLabel",
        ).pack(anchor=tk.W, pady=5)

        # Listbox with fonts
        list_frame = ttk.Frame(frame)
        list_frame.pack(fill=tk.BOTH, expand=True)

        scrollbar = ttk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        listbox = tk.Listbox(list_frame, yscrollcommand=scrollbar.set)
        listbox.pack(fill=tk.BOTH, expand=True)
        scrollbar.config(command=listbox.yview)

        for asset in assets:
            size_mb = asset.size / (1024 * 1024)
            listbox.insert(tk.END, f"{asset.name} ({size_mb:.2f} MB)")

        if assets:
            listbox.selection_set(0)

        def on_install():
            selection = listbox.curselection()
            if not selection:
                messagebox.showwarning(
                    t("warning", "警告", "Warning"),
                    t(
                        "select_font_pkg",
                        "请选择一个字体包",
                        "Please select a font package",
                    ),
                )
                return

            asset = assets[selection[0]]
            dialog.destroy()
            self._download_and_install_font(asset)

        btn_frame = ttk.Frame(frame)
        btn_frame.pack(fill=tk.X, pady=10)

        ttk.Button(
            btn_frame, text=t("install", "安装", "Install"), command=on_install
        ).pack(side=tk.LEFT, padx=5)
        ttk.Button(
            btn_frame, text=t("cancel", "取消", "Cancel"), command=dialog.destroy
        ).pack(side=tk.LEFT, padx=5)

    def _download_and_install_font(self, asset):
        """Download font with progress dialog, then confirm before installing"""
        # Create download progress dialog
        dialog = self._create_dialog(
            title=t("downloading", "下载中", "Downloading"),
            width=450,
            height=200,
            min_width=400,
            min_height=180,
        )

        # Prevent closing during download
        dialog.protocol("WM_DELETE_WINDOW", lambda: None)

        frame = ttk.Frame(dialog, padding="20")
        frame.pack(fill=tk.BOTH, expand=True)

        # File name label
        ttk.Label(
            frame,
            text=t("downloading_file", "正在下载文件:", "Downloading file:"),
            style="Header.TLabel",
        ).pack(anchor=tk.W)
        ttk.Label(frame, text=asset.name, foreground="blue").pack(
            anchor=tk.W, pady=(0, 10)
        )

        # Progress bar
        progress_var = tk.DoubleVar(value=0)
        progress_bar = ttk.Progressbar(
            frame, variable=progress_var, maximum=100, length=380, mode="determinate"
        )
        progress_bar.pack(fill=tk.X, pady=5)

        # Progress text
        progress_text_var = tk.StringVar(value="0%  0.00 / 0.00 MB")
        progress_label = ttk.Label(frame, textvariable=progress_text_var)
        progress_label.pack(anchor=tk.W)

        # Status label
        status_var = tk.StringVar(value=t("connecting", "正在连接...", "Connecting..."))
        status_label = ttk.Label(frame, textvariable=status_var, foreground="gray")
        status_label.pack(anchor=tk.W, pady=(5, 0))

        # Cancel button (initially hidden, will be replaced by result buttons)
        btn_frame = ttk.Frame(dialog)
        btn_frame.pack(fill=tk.X, pady=10, padx=15)

        # Track download state
        download_state = {
            "cancelled": False,
            "success": False,
            "zip_path": None,
            "error_msg": None,
        }

        def on_cancel():
            download_state["cancelled"] = True
            status_var.set(t("cancelling", "正在取消...", "Cancelling..."))

        cancel_btn = ttk.Button(
            btn_frame, text=t("cancel", "取消", "Cancel"), command=on_cancel
        )
        cancel_btn.pack(side=tk.LEFT, padx=5)

        def update_progress(downloaded: int, total: int):
            """Update progress bar from download callback"""
            if total > 0:
                percent = (downloaded / total) * 100
                mb_downloaded = downloaded / (1024 * 1024)
                mb_total = total / (1024 * 1024)

                def do_update():
                    progress_var.set(percent)
                    progress_text_var.set(
                        f"{percent:.1f}%  {mb_downloaded:.2f} / {mb_total:.2f} MB"
                    )
                    status_var.set(t("downloading", "下载中...", "Downloading..."))

                self.root.after(0, do_update)

        def download_task():
            """Background download task"""
            from src.core.downloader import FontReleaseDownloader

            try:
                downloader = FontReleaseDownloader()

                # Custom download with progress callback
                success, msg, zip_path = downloader.download_font(
                    asset, update_progress
                )

                if download_state["cancelled"]:
                    # Clean up downloaded file if cancelled
                    if zip_path and os.path.exists(zip_path):
                        try:
                            os.remove(zip_path)
                        except:
                            pass
                    self.root.after(0, lambda: dialog.destroy())
                    self.root.after(
                        0,
                        lambda: self._log(
                            t("download_cancelled", "下载已取消", "Download cancelled"),
                            "warning",
                        ),
                    )
                    return

                download_state["success"] = success
                download_state["zip_path"] = zip_path
                download_state["error_msg"] = msg

                # Update UI on main thread
                self.root.after(0, lambda: on_download_complete())

            except Exception as e:
                download_state["success"] = False
                download_state["error_msg"] = str(e)
                self.root.after(0, lambda: on_download_complete())

        def on_download_complete():
            """Handle download completion - show result and install button"""
            # Clear cancel button
            for widget in btn_frame.winfo_children():
                widget.destroy()

            # Allow closing dialog now
            dialog.protocol("WM_DELETE_WINDOW", dialog.destroy)

            if download_state["success"] and download_state["zip_path"]:
                # Download successful - show install confirmation
                progress_var.set(100)
                progress_text_var.set("100%  " + t("complete", "完成", "Complete"))
                status_var.set(
                    t(
                        "download_success",
                        "下载成功！点击安装按钮开始安装字体。",
                        "Download successful! Click Install to begin font installation.",
                    )
                )
                status_label.config(foreground="green")

                self._log(
                    t(
                        "download_complete",
                        f"下载完成: {asset.name}",
                        f"Download complete: {asset.name}",
                    ),
                    "success",
                )

                def on_install():
                    """Start font installation"""
                    dialog.destroy()
                    self._install_downloaded_font(
                        download_state["zip_path"], asset.name
                    )

                def on_close():
                    """Close without installing"""
                    dialog.destroy()
                    self._log(
                        t("install_skipped", "已跳过安装", "Installation skipped"),
                        "warning",
                    )

                # Show install and close buttons
                ttk.Button(
                    btn_frame, text=t("install", "安装", "Install"), command=on_install
                ).pack(side=tk.LEFT, padx=5)
                ttk.Button(
                    btn_frame, text=t("close", "关闭", "Close"), command=on_close
                ).pack(side=tk.LEFT, padx=5)
            else:
                # Download failed - show error
                progress_bar.config(style="")  # Reset style
                status_var.set(t("download_failed", "下载失败", "Download failed"))
                status_label.config(foreground="red")

                error_msg = download_state["error_msg"] or t(
                    "unknown_error", "未知错误", "Unknown error"
                )
                self._log(
                    t(
                        "download_error",
                        f"下载失败: {error_msg}",
                        f"Download failed: {error_msg}",
                    ),
                    "error",
                )

                # Show only close button
                ttk.Button(
                    btn_frame, text=t("close", "关闭", "Close"), command=dialog.destroy
                ).pack(side=tk.LEFT, padx=5)

        # Start download in background thread
        self._log(
            t(
                "starting_download",
                f"开始下载: {asset.name}...",
                f"Starting download: {asset.name}...",
            ),
            "info",
        )
        threading.Thread(target=download_task, daemon=True).start()

    def _install_downloaded_font(self, zip_path: str, asset_name: str):
        """Install font from downloaded zip file"""
        self._log(
            t(
                "installing_font",
                f"正在安装字体: {asset_name}...",
                f"Installing font: {asset_name}...",
            ),
            "info",
        )

        def task():
            try:
                success, msg = setup_fonts(zip_path)
                self.root.after(0, lambda: self._on_task_complete(success, msg))
            except Exception as e:
                self.root.after(0, lambda: self._on_task_complete(False, str(e)))

        threading.Thread(target=task, daemon=True).start()

    def _install_fonts_local(self):
        """Install fonts from local file"""
        file_path = filedialog.askopenfilename(
            title=t("select_font_file", "选择字体包", "Select Font Package"),
            filetypes=[("ZIP files", "*.zip"), ("All files", "*.*")],
        )

        if not file_path:
            return

        self._log(
            t(
                "installing_font",
                f"正在安装字体: {os.path.basename(file_path)}...",
                f"Installing font: {os.path.basename(file_path)}...",
            ),
            "info",
        )

        def task():
            try:
                success, msg = setup_fonts(file_path)
                self.root.after(0, lambda: self._on_task_complete(success, msg))
            except Exception as e:
                self.root.after(0, lambda: self._on_task_complete(False, str(e)))

        threading.Thread(target=task, daemon=True).start()

    def _set_default_font_path(self):
        """Set default font path"""
        path = filedialog.askdirectory(
            title=t("select_font_dir", "选择字体目录", "Select Font Directory")
        )

        if path:
            Config.set_default_font_path(path)
            self.default_path_var.set(path)
            self._log(
                t(
                    "path_set",
                    f"默认字体路径已设置: {path}",
                    f"Default font path set: {path}",
                ),
                "success",
            )

    def _install_fonts_default(self):
        """Install fonts from default path"""
        default_path = Config.get_default_font_path()

        if not default_path:
            messagebox.showwarning(
                t("warning", "警告", "Warning"),
                t(
                    "set_default_first",
                    "请先设置默认字体路径",
                    "Please set default font path first",
                ),
            )
            return

        if not os.path.isdir(default_path):
            messagebox.showerror(
                t("error", "错误", "Error"),
                t(
                    "path_not_exist",
                    f"路径不存在: {default_path}",
                    f"Path does not exist: {default_path}",
                ),
            )
            return

        # List zip files
        zip_files = [f for f in os.listdir(default_path) if f.lower().endswith(".zip")]

        if not zip_files:
            messagebox.showinfo(
                t("info", "提示", "Info"),
                t(
                    "no_zip_found",
                    "在默认路径中未找到zip文件",
                    "No zip files found in default path",
                ),
            )
            return

        # Show selection dialog
        dialog = tk.Toplevel(self.root)
        dialog.title(t("select_font", "选择字体包", "Select Font Package"))
        dialog.geometry("400x250")
        dialog.transient(self.root)
        dialog.grab_set()

        frame = ttk.Frame(dialog, padding="10")
        frame.pack(fill=tk.BOTH, expand=True)

        list_frame = ttk.Frame(frame)
        list_frame.pack(fill=tk.BOTH, expand=True)

        scrollbar = ttk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        listbox = tk.Listbox(list_frame, yscrollcommand=scrollbar.set)
        listbox.pack(fill=tk.BOTH, expand=True)
        scrollbar.config(command=listbox.yview)

        for f in zip_files:
            file_path = os.path.join(default_path, f)
            size_mb = os.path.getsize(file_path) / (1024 * 1024)
            listbox.insert(tk.END, f"{f} ({size_mb:.2f} MB)")

        if zip_files:
            listbox.selection_set(0)

        def on_install():
            selection = listbox.curselection()
            if not selection:
                return

            file_name = zip_files[selection[0]]
            file_path = os.path.join(default_path, file_name)
            dialog.destroy()

            self._log(
                t(
                    "installing_font",
                    f"正在安装字体: {file_name}...",
                    f"Installing font: {file_name}...",
                ),
                "info",
            )

            def task():
                try:
                    success, msg = setup_fonts(file_path)
                    self.root.after(0, lambda: self._on_task_complete(success, msg))
                except Exception as e:
                    self.root.after(0, lambda: self._on_task_complete(False, str(e)))

            threading.Thread(target=task, daemon=True).start()

        btn_frame = ttk.Frame(frame)
        btn_frame.pack(fill=tk.X, pady=10)

        ttk.Button(
            btn_frame, text=t("install", "安装", "Install"), command=on_install
        ).pack(side=tk.LEFT, padx=5)
        ttk.Button(
            btn_frame, text=t("cancel", "取消", "Cancel"), command=dialog.destroy
        ).pack(side=tk.LEFT, padx=5)

    def _update_launch_cmd(self):
        """Update launch command display"""
        if self.target_language:
            cmd = get_locale_command(self.target_language)
            self.launch_cmd_var.set(cmd)
        else:
            self.launch_cmd_var.set(
                t(
                    "select_lang_first",
                    "请先选择目标语言",
                    "Please select target language first",
                )
            )

    def _copy_launch_cmd(self):
        """Copy launch command to clipboard"""
        cmd = self.launch_cmd_var.get()
        if cmd and not cmd.startswith(t("select_lang_first", "请先", "Please")):
            self.root.clipboard_clear()
            self.root.clipboard_append(cmd)
            self._log(t("copied", "已复制到剪贴板", "Copied to clipboard"), "success")

    def _refresh_paths(self):
        """Refresh search paths list"""
        self.paths_listbox.delete(0, tk.END)
        paths = get_game_search_paths()
        for path in paths:
            self.paths_listbox.insert(tk.END, path)

    def _add_search_path(self):
        """Add new search path"""
        path = filedialog.askdirectory(
            title=t("select_game_dir", "选择游戏目录", "Select Game Directory")
        )

        if path:
            success, msg = add_game_search_path(path)
            if success:
                self._log(msg, "success")
                self._refresh_paths()
            else:
                self._log(msg, "error")

    def _remove_search_path(self):
        """Remove selected search path"""
        selection = self.paths_listbox.curselection()
        if not selection:
            messagebox.showwarning(
                t("warning", "警告", "Warning"),
                t(
                    "select_path_first",
                    "请先选择一个路径",
                    "Please select a path first",
                ),
            )
            return

        path = self.paths_listbox.get(selection[0])
        success, msg = remove_game_search_path(path)
        if success:
            self._log(msg, "success")
            self._refresh_paths()
        else:
            self._log(msg, "error")

    def _refresh_games_list(self):
        """Refresh managed games list"""
        # Clear existing items
        for item in self.games_tree.get_children():
            self.games_tree.delete(item)

        # Get managed games from config
        managed_games = Config.get_managed_games()

        if not managed_games:
            # Insert placeholder message
            self.games_tree.insert(
                "",
                tk.END,
                values=(
                    t("no_games", "暂无游戏", "No games yet"),
                    t(
                        "use_add_button",
                        "使用下方按钮添加游戏",
                        "Use button below to add games",
                    ),
                    "",
                ),
            )
            return

        # Populate with game data
        for game in managed_games:
            game_name = game.get("name", "Unknown")
            game_path = game.get("exe_path", "")
            game_lang = game.get("language", "")

            # Convert language code to display name
            if game_lang == TargetLanguage.CHINESE:
                lang_display = "简体中文" if is_chinese() else "Chinese"
            elif game_lang == TargetLanguage.JAPANESE:
                lang_display = "日本語" if is_chinese() else "Japanese"
            else:
                lang_display = game_lang

            self.games_tree.insert(
                "", tk.END, values=(game_name, game_path, lang_display)
            )

    def _launch_selected_game(self):
        """Launch the selected game"""
        selection = self.games_tree.selection()
        if not selection:
            messagebox.showwarning(
                t("warning", "警告", "Warning"),
                t(
                    "select_game_first",
                    "请先选择一个游戏",
                    "Please select a game first",
                ),
            )
            return

        # Get selected game info
        item = self.games_tree.item(selection[0])
        game_name = item["values"][0]

        # Placeholder: Show not implemented message
        messagebox.showinfo(
            t("info", "提示", "Info"),
            t(
                "feature_coming_soon",
                f"启动游戏功能即将推出\n游戏: {game_name}",
                f"Launch game feature coming soon\nGame: {game_name}",
            ),
        )

    def _remove_selected_game(self):
        """Remove the selected game from managed list"""
        selection = self.games_tree.selection()
        if not selection:
            messagebox.showwarning(
                t("warning", "警告", "Warning"),
                t(
                    "select_game_first",
                    "请先选择一个游戏",
                    "Please select a game first",
                ),
            )
            return

        # Get selected game info
        item = self.games_tree.item(selection[0])
        game_name = item["values"][0]

        # Confirm removal
        if not messagebox.askyesno(
            t("confirm", "确认", "Confirm"),
            t(
                "confirm_remove_game",
                f"确认从列表中移除游戏?\n{game_name}\n\n注意:这只会从本程序的管理列表中移除,不会从Steam库中删除。",
                f"Remove game from managed list?\n{game_name}\n\nNote: This only removes from this program's list, not from Steam library.",
            ),
        ):
            return

        # Remove from config
        managed_games = Config.get_managed_games()
        managed_games = [g for g in managed_games if g.get("name") != game_name]
        Config.set_managed_games(managed_games)

        # Refresh display
        self._refresh_games_list()
        self._log(
            t(
                "game_removed",
                f"游戏已从列表移除: {game_name}",
                f"Game removed from list: {game_name}",
            ),
            "success",
        )

    def _browse_add_game(self):
        """Browse and add game to Steam"""
        if not self.target_language:
            messagebox.showwarning(
                t("warning", "警告", "Warning"),
                t(
                    "select_lang_first",
                    "请先选择目标语言",
                    "Please select target language first",
                ),
            )
            self._show_language_dialog()
            return

        # Select executable
        file_path = filedialog.askopenfilename(
            title=t("select_game_exe", "选择游戏可执行文件", "Select Game Executable"),
            filetypes=[
                ("Executable files", "*.exe *.sh *.AppImage"),
                ("All files", "*.*"),
            ],
        )

        if not file_path:
            return

        # Get game name
        default_name = os.path.splitext(os.path.basename(file_path))[0]

        # Show name input dialog with scrollable frame for long content
        dialog = self._create_dialog(
            title=t("add_game", "添加游戏", "Add Game"),
            width=450,
            height=320,
            min_width=400,
            min_height=280,
        )

        # Use ScrollableFrame for content that may overflow
        scroll_container = ScrollableFrame(dialog)
        scroll_container.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        frame = ttk.Frame(scroll_container.scrollable_frame, padding="15")
        frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(frame, text=t("game_exe", "可执行文件:", "Executable:")).pack(
            anchor=tk.W
        )
        ttk.Label(frame, text=file_path, foreground="blue", wraplength=380).pack(
            anchor=tk.W, pady=5
        )

        ttk.Label(frame, text=t("game_name", "游戏名称:", "Game Name:")).pack(
            anchor=tk.W, pady=(10, 0)
        )
        name_var = tk.StringVar(value=default_name)
        name_entry = ttk.Entry(frame, textvariable=name_var, width=45)
        name_entry.pack(fill=tk.X, pady=5)

        launch_options = get_locale_command(self.target_language)
        ttk.Label(frame, text=t("launch_opts", "启动选项:", "Launch Options:")).pack(
            anchor=tk.W, pady=(10, 0)
        )
        ttk.Label(frame, text=launch_options, foreground="green", wraplength=380).pack(
            anchor=tk.W
        )

        def on_add():
            game_name = name_var.get().strip()
            if not game_name:
                messagebox.showwarning(
                    t("warning", "警告", "Warning"),
                    t("enter_name", "请输入游戏名称", "Please enter game name"),
                )
                return

            dialog.destroy()

            self._log(
                t(
                    "adding_game",
                    f"正在添加游戏: {game_name}...",
                    f"Adding game: {game_name}...",
                ),
                "info",
            )

            def task():
                try:
                    success, msg = SteamManager.add_non_steam_game(
                        exe_path=file_path,
                        app_name=game_name,
                        launch_options=launch_options,
                    )

                    # If successful, save to managed games list
                    if success:
                        game_data = {
                            "name": game_name,
                            "exe_path": file_path,
                            "language": self.target_language,
                            "launch_options": launch_options,
                        }
                        Config.add_managed_game(game_data)
                        # Refresh games list on main thread
                        self.root.after(0, self._refresh_games_list)

                    self.root.after(0, lambda: self._on_task_complete(success, msg))
                except Exception as e:
                    self.root.after(0, lambda: self._on_task_complete(False, str(e)))

            threading.Thread(target=task, daemon=True).start()

        # Button frame outside scrollable area to ensure visibility
        btn_frame = ttk.Frame(dialog)
        btn_frame.pack(fill=tk.X, pady=10, padx=15)

        ttk.Button(btn_frame, text=t("add", "添加", "Add"), command=on_add).pack(
            side=tk.LEFT, padx=5
        )
        ttk.Button(
            btn_frame, text=t("cancel", "取消", "Cancel"), command=dialog.destroy
        ).pack(side=tk.LEFT, padx=5)

    def run(self):
        """Run the application"""
        self.root.mainloop()


def main():
    """Main function"""
    app = GUIApplication()
    try:
        app.run()
    except KeyboardInterrupt:
        pass
    except Exception as e:
        messagebox.showerror("Error", f"Application error: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
