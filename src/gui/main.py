"""
GUI Main Application - CustomTkinter-based modern graphical interface
"""

import os
import sys
import threading
import tkinter as tk
from tkinter import filedialog
from typing import Optional

import customtkinter as ctk

from src.core.installers import (
    setup_locale,
    check_locale_status,
    setup_fonts,
    check_fonts_status,
    get_fonts_count,
    list_available_fonts,
)
from src.utils.locale import t, is_chinese
from src.core.game_launcher import get_locale_command
from src.config import Config, TargetLanguage
from src.core.steam_manager import SteamManager


# Configure CustomTkinter
ctk.set_appearance_mode("System")  # Modes: "System", "Dark", "Light"
ctk.set_default_color_theme("blue")  # Themes: "blue", "dark-blue", "green"


class CTkMessageBox(ctk.CTkToplevel):
    """Custom message box using CustomTkinter"""

    def __init__(
        self,
        parent,
        title: str = "Message",
        message: str = "",
        icon: str = "info",  # "info", "warning", "error", "question"
        option_1: str = "OK",
        option_2: Optional[str] = None,
    ):
        super().__init__(parent)
        self.result = None

        self.title(title)
        self.resizable(False, False)
        self.transient(parent)

        # Icon colors
        icon_colors = {
            "info": "#3B8ED0",
            "success": "#2FA572",
            "warning": "#F0A30A",
            "error": "#D32F2F",
            "question": "#3B8ED0",
        }
        icon_symbols = {
            "info": "ℹ",
            "success": "✓",
            "warning": "⚠",
            "error": "✕",
            "question": "?",
        }

        # Content frame
        content_frame = ctk.CTkFrame(self, fg_color="transparent")
        content_frame.pack(padx=30, pady=25, fill="both", expand=True)

        # Icon
        icon_label = ctk.CTkLabel(
            content_frame,
            text=icon_symbols.get(icon, "ℹ"),
            font=ctk.CTkFont(size=36, weight="bold"),
            text_color=icon_colors.get(icon, "#3B8ED0"),
        )
        icon_label.pack(pady=(0, 15))

        # Message
        msg_label = ctk.CTkLabel(
            content_frame,
            text=message,
            font=ctk.CTkFont(size=13),
            wraplength=350,
            justify="center",
        )
        msg_label.pack(pady=(0, 20))

        # Buttons
        btn_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
        btn_frame.pack()

        if option_2:
            ctk.CTkButton(
                btn_frame,
                text=option_1,
                width=100,
                command=lambda: self._on_click(option_1),
            ).pack(side="left", padx=10)
            ctk.CTkButton(
                btn_frame,
                text=option_2,
                width=100,
                fg_color="gray50",
                hover_color="gray40",
                command=lambda: self._on_click(option_2),
            ).pack(side="left", padx=10)
        else:
            ctk.CTkButton(
                btn_frame,
                text=option_1,
                width=120,
                command=lambda: self._on_click(option_1),
            ).pack()

        # Calculate size and center
        self.update_idletasks()
        width = max(400, msg_label.winfo_reqwidth() + 60)
        height = content_frame.winfo_reqheight() + 50
        x = parent.winfo_x() + (parent.winfo_width() - width) // 2
        y = parent.winfo_y() + (parent.winfo_height() - height) // 2
        self.geometry(f"{width}x{height}+{x}+{y}")

        # Grab after window is ready
        self.after(100, lambda: self.grab_set())

        # Handle close button
        self.protocol("WM_DELETE_WINDOW", lambda: self._on_click(None))

    def _on_click(self, value):
        self.result = value
        self.destroy()

    def get_result(self):
        self.wait_window()
        return self.result


def show_info(parent, title: str, message: str):
    """Show info message box"""
    dialog = CTkMessageBox(parent, title=title, message=message, icon="info")
    dialog.get_result()


def show_success(parent, title: str, message: str):
    """Show success message box"""
    dialog = CTkMessageBox(parent, title=title, message=message, icon="success")
    dialog.get_result()


def show_warning(parent, title: str, message: str):
    """Show warning message box"""
    dialog = CTkMessageBox(parent, title=title, message=message, icon="warning")
    dialog.get_result()


def show_error(parent, title: str, message: str):
    """Show error message box"""
    dialog = CTkMessageBox(parent, title=title, message=message, icon="error")
    dialog.get_result()


def ask_yes_no(parent, title: str, message: str) -> bool:
    """Show yes/no question dialog, returns True if yes"""
    yes_text = "是" if is_chinese() else "Yes"
    no_text = "否" if is_chinese() else "No"
    dialog = CTkMessageBox(
        parent,
        title=title,
        message=message,
        icon="question",
        option_1=yes_text,
        option_2=no_text,
    )
    result = dialog.get_result()
    return result == yes_text


class GUIApplication(ctk.CTk):
    """Main GUI Application using CustomTkinter"""

    def __init__(self):
        super().__init__()

        # Window configuration
        self.title("SteamDeck Galgame Config Tool")
        self.geometry("900x700")
        self.minsize(800, 600)

        # Target language
        self.target_language: Optional[str] = Config.get_target_language()

        # Configure grid weights for responsive layout
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=0)  # Header
        self.grid_rowconfigure(1, weight=0)  # Status
        self.grid_rowconfigure(2, weight=1)  # Main content (tabview)
        self.grid_rowconfigure(3, weight=0)  # Log area

        # Create main UI
        self._create_header()
        self._create_status_bar()
        self._create_tabview()
        self._create_log_area()

        # Check if language needs to be selected
        if not self.target_language:
            self.after(100, self._show_language_dialog)

    def _create_header(self):
        """Create header with title and language button"""
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.grid(row=0, column=0, padx=20, pady=(15, 5), sticky="ew")
        header_frame.grid_columnconfigure(0, weight=1)

        # Title
        title_text = (
            "SteamDeck 游戏环境配置工具"
            if is_chinese()
            else "SteamDeck Game Environment Config Tool"
        )
        title_label = ctk.CTkLabel(
            header_frame, text=title_text, font=ctk.CTkFont(size=20, weight="bold")
        )
        title_label.grid(row=0, column=0, sticky="w")

        # Language and theme buttons
        btn_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        btn_frame.grid(row=0, column=1, sticky="e")

        # Theme switch
        self.theme_switch = ctk.CTkSwitch(
            btn_frame,
            text=t("dark_mode", "深色模式", "Dark Mode"),
            command=self._toggle_theme,
            onvalue="dark",
            offvalue="light",
        )
        self.theme_switch.grid(row=0, column=0, padx=10)
        if ctk.get_appearance_mode().lower() == "dark":
            self.theme_switch.select()

        # Language button
        lang_btn_text = "切换语言" if is_chinese() else "Language"
        self.lang_btn = ctk.CTkButton(
            btn_frame,
            text=lang_btn_text,
            width=100,
            command=self._show_language_dialog,
        )
        self.lang_btn.grid(row=0, column=1)

    def _toggle_theme(self):
        """Toggle between light and dark theme"""
        if self.theme_switch.get() == "dark":
            ctk.set_appearance_mode("dark")
        else:
            ctk.set_appearance_mode("light")

    def _create_status_bar(self):
        """Create status bar showing current states"""
        status_frame = ctk.CTkFrame(self)
        status_frame.grid(row=1, column=0, padx=20, pady=5, sticky="ew")

        # Configure grid for even spacing
        for i in range(7):
            status_frame.grid_columnconfigure(i, weight=1 if i % 2 == 1 else 0)

        # Target language
        ctk.CTkLabel(
            status_frame,
            text=t("target_lang", "目标语言:", "Target Language:"),
            font=ctk.CTkFont(weight="bold"),
        ).grid(row=0, column=0, padx=(15, 5), pady=10, sticky="w")
        self.lang_status = ctk.CTkLabel(status_frame, text="--")
        self.lang_status.grid(row=0, column=1, padx=5, pady=10, sticky="w")

        # Locale status
        ctk.CTkLabel(
            status_frame,
            text=t("locale_status", "语言环境:", "Locale:"),
            font=ctk.CTkFont(weight="bold"),
        ).grid(row=0, column=2, padx=(15, 5), pady=10, sticky="w")
        self.locale_status = ctk.CTkLabel(status_frame, text="--")
        self.locale_status.grid(row=0, column=3, padx=5, pady=10, sticky="w")

        # Font status
        ctk.CTkLabel(
            status_frame,
            text=t("font_status", "字体:", "Fonts:"),
            font=ctk.CTkFont(weight="bold"),
        ).grid(row=0, column=4, padx=(15, 5), pady=10, sticky="w")
        self.font_status = ctk.CTkLabel(status_frame, text="--")
        self.font_status.grid(row=0, column=5, padx=5, pady=10, sticky="w")

        # Refresh button
        refresh_btn = ctk.CTkButton(
            status_frame,
            text=t("refresh", "刷新", "Refresh"),
            width=80,
            command=self._refresh_status,
        )
        refresh_btn.grid(row=0, column=6, padx=15, pady=10)

        # Initial refresh
        self.after(200, self._refresh_status)

    def _refresh_status(self):
        """Refresh status display"""
        # Target language
        if self.target_language:
            lang_name = TargetLanguage.get_name(
                self.target_language, "zh" if is_chinese() else "en"
            )
            self.lang_status.configure(text=lang_name, text_color="#3B8ED0")
        else:
            self.lang_status.configure(
                text=t("not_set", "未设置", "Not Set"), text_color="gray"
            )

        # Locale status
        if self.target_language:
            locale_code = TargetLanguage.get_locale(self.target_language)
            if check_locale_status(locale_code):
                self.locale_status.configure(text="✓ OK", text_color="#2FA572")
            else:
                self.locale_status.configure(
                    text="✗ " + t("not_installed", "未安装", "Not Installed"),
                    text_color="#E74C3C",
                )
        else:
            self.locale_status.configure(text="--", text_color="gray")

        # Font status
        if check_fonts_status():
            count = get_fonts_count()
            self.font_status.configure(text=f"✓ OK ({count})", text_color="#2FA572")
        else:
            self.font_status.configure(
                text="✗ " + t("not_installed", "未安装", "Not Installed"),
                text_color="#E74C3C",
            )

    def _create_tabview(self):
        """Create main tabview with all feature tabs"""
        self.tabview = ctk.CTkTabview(self)
        self.tabview.grid(row=2, column=0, padx=20, pady=5, sticky="nsew")

        # Create tabs
        self.tab_steam = self.tabview.add(t("steam_tab", "Steam游戏", "Steam Games"))
        self.tab_locale = self.tabview.add(t("locale_tab", "语言环境", "Locale"))
        self.tab_fonts = self.tabview.add(t("font_tab", "字体安装", "Fonts"))
        self.tab_launcher = self.tabview.add(
            t("launcher_tab", "启动选项", "Launch Options")
        )

        # Configure tab content
        self._create_steam_tab()
        self._create_locale_tab()
        self._create_font_tab()
        self._create_launcher_tab()

    def _create_steam_tab(self):
        """Create Steam game management tab"""
        tab = self.tab_steam
        tab.grid_columnconfigure(0, weight=1)
        tab.grid_rowconfigure(0, weight=1)

        # Scrollable container
        scroll = ctk.CTkScrollableFrame(tab, fg_color="transparent")
        scroll.grid(row=0, column=0, sticky="nsew")
        scroll.grid_columnconfigure(0, weight=1)

        # Description
        desc_text = t(
            "steam_desc",
            "管理由本程序添加到Steam库的游戏。",
            "Manage games added to Steam library by this program.",
        )
        ctk.CTkLabel(scroll, text=desc_text, wraplength=700).grid(
            row=0, column=0, padx=10, pady=10, sticky="w"
        )

        # Games frame
        games_frame = ctk.CTkFrame(scroll)
        games_frame.grid(row=1, column=0, padx=10, pady=5, sticky="ew")
        games_frame.grid_columnconfigure(0, weight=1)

        # Scrollable frame for games list
        self.games_scroll = ctk.CTkScrollableFrame(
            games_frame,
            label_text=t("managed_games", "已添加的游戏", "Managed Games"),
            height=200,
        )
        self.games_scroll.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        self.games_scroll.grid_columnconfigure(0, weight=2)
        self.games_scroll.grid_columnconfigure(1, weight=3)
        self.games_scroll.grid_columnconfigure(2, weight=1)

        # Header row
        ctk.CTkLabel(
            self.games_scroll,
            text=t("game_name", "游戏名称", "Game Name"),
            font=ctk.CTkFont(weight="bold"),
        ).grid(row=0, column=0, padx=5, pady=5, sticky="w")
        ctk.CTkLabel(
            self.games_scroll,
            text=t("game_path", "路径", "Path"),
            font=ctk.CTkFont(weight="bold"),
        ).grid(row=0, column=1, padx=5, pady=5, sticky="w")
        ctk.CTkLabel(
            self.games_scroll,
            text=t("language", "语言", "Language"),
            font=ctk.CTkFont(weight="bold"),
        ).grid(row=0, column=2, padx=5, pady=5, sticky="w")

        # Button frame
        btn_frame = ctk.CTkFrame(scroll, fg_color="transparent")
        btn_frame.grid(row=2, column=0, padx=10, pady=10, sticky="ew")

        ctk.CTkButton(
            btn_frame,
            text=t("add_game", "添加游戏", "Add Game"),
            command=self._browse_add_game,
        ).grid(row=0, column=0, padx=5)

        ctk.CTkButton(
            btn_frame,
            text=t("refresh_games", "刷新列表", "Refresh"),
            command=self._refresh_games_list,
        ).grid(row=0, column=1, padx=5)

        # Initial refresh
        self.after(400, self._refresh_games_list)

    def _create_locale_tab(self):
        """Create locale installation tab"""
        tab = self.tab_locale
        tab.grid_columnconfigure(0, weight=1)
        tab.grid_rowconfigure(0, weight=1)

        # Scrollable container
        scroll = ctk.CTkScrollableFrame(tab, fg_color="transparent")
        scroll.grid(row=0, column=0, sticky="nsew")
        scroll.grid_columnconfigure(0, weight=1)

        # Description
        desc_text = t(
            "locale_desc",
            "安装系统语言环境，使游戏能够正确显示中文/日文。\n此操作需要root权限，将会修改系统文件。",
            "Install system locale to display Chinese/Japanese in games.\nThis requires root permission and will modify system files.",
        )
        ctk.CTkLabel(scroll, text=desc_text, wraplength=700, justify="left").grid(
            row=0, column=0, padx=20, pady=15, sticky="w"
        )

        # Steps frame
        steps_frame = ctk.CTkFrame(scroll)
        steps_frame.grid(row=1, column=0, padx=20, pady=10, sticky="ew")
        steps_frame.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            steps_frame,
            text=t("steps", "操作步骤", "Steps"),
            font=ctk.CTkFont(size=14, weight="bold"),
        ).grid(row=0, column=0, padx=15, pady=(15, 10), sticky="w")

        steps = [
            t("step1", "1. 禁用 SteamOS 只读模式", "1. Disable SteamOS read-only mode"),
            t("step2", "2. 初始化 pacman 密钥", "2. Initialize pacman keys"),
            t("step3", "3. 启用目标语言环境", "3. Enable target locale"),
            t("step4", "4. 生成语言环境", "4. Generate locale"),
            t("step5", "5. 恢复 SteamOS 只读模式", "5. Restore SteamOS read-only mode"),
        ]
        for i, step in enumerate(steps):
            ctk.CTkLabel(steps_frame, text=step).grid(
                row=i + 1, column=0, padx=25, pady=3, sticky="w"
            )

        # Spacer
        ctk.CTkLabel(steps_frame, text="").grid(row=len(steps) + 1, column=0, pady=5)

        # Button frame for better visibility
        btn_frame = ctk.CTkFrame(scroll, fg_color="transparent")
        btn_frame.grid(row=2, column=0, padx=20, pady=20, sticky="ew")
        btn_frame.grid_columnconfigure(0, weight=1)

        # Install button - centered
        self.locale_install_btn = ctk.CTkButton(
            btn_frame,
            text=t("install_locale", "安装语言环境", "Install Locale"),
            font=ctk.CTkFont(size=14),
            height=45,
            width=200,
            command=self._install_locale,
        )
        self.locale_install_btn.grid(row=0, column=0, pady=10)

    def _create_font_tab(self):
        """Create font installation tab"""
        tab = self.tab_fonts
        tab.grid_columnconfigure(0, weight=1)
        tab.grid_rowconfigure(0, weight=1)

        # Scrollable container
        scroll = ctk.CTkScrollableFrame(tab, fg_color="transparent")
        scroll.grid(row=0, column=0, sticky="nsew")
        scroll.grid_columnconfigure(0, weight=1)

        # Description
        desc_text = t(
            "font_desc",
            "安装中文/日文字体，确保游戏能够正确显示文字。",
            "Install Chinese/Japanese fonts for proper text display in games.",
        )
        ctk.CTkLabel(scroll, text=desc_text, wraplength=700).grid(
            row=0, column=0, padx=20, pady=15, sticky="w"
        )

        # Options frame
        options_frame = ctk.CTkFrame(scroll)
        options_frame.grid(row=1, column=0, padx=20, pady=10, sticky="ew")
        options_frame.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(
            options_frame,
            text=t("install_method", "安装方式", "Installation Method"),
            font=ctk.CTkFont(size=14, weight="bold"),
        ).grid(row=0, column=0, columnspan=3, padx=15, pady=(15, 10), sticky="w")

        # GitHub download
        ctk.CTkLabel(
            options_frame, text=t("from_github", "从 GitHub 下载:", "From GitHub:")
        ).grid(row=1, column=0, padx=(25, 10), pady=10, sticky="w")
        ctk.CTkButton(
            options_frame,
            text=t("download", "下载安装", "Download & Install"),
            command=self._install_fonts_github,
        ).grid(row=1, column=1, padx=10, pady=10, sticky="w")

        # Local file
        ctk.CTkLabel(
            options_frame, text=t("from_local", "从本地文件:", "From Local File:")
        ).grid(row=2, column=0, padx=(25, 10), pady=10, sticky="w")
        ctk.CTkButton(
            options_frame,
            text=t("browse", "浏览...", "Browse..."),
            command=self._install_fonts_local,
        ).grid(row=2, column=1, padx=10, pady=10, sticky="w")

        # Default path
        ctk.CTkLabel(
            options_frame, text=t("default_path", "默认路径:", "Default Path:")
        ).grid(row=3, column=0, padx=(25, 10), pady=10, sticky="w")

        path_frame = ctk.CTkFrame(options_frame, fg_color="transparent")
        path_frame.grid(row=3, column=1, columnspan=2, padx=10, pady=10, sticky="ew")

        self.default_path_var = tk.StringVar(
            value=Config.get_default_font_path() or t("not_set", "未设置", "Not Set")
        )
        ctk.CTkLabel(
            path_frame, textvariable=self.default_path_var, text_color="#3B8ED0"
        ).grid(row=0, column=0, padx=(0, 15), sticky="w")

        ctk.CTkButton(
            path_frame,
            text=t("set_path", "设置", "Set"),
            width=80,
            command=self._set_default_font_path,
        ).grid(row=0, column=1, padx=5)

        ctk.CTkButton(
            path_frame,
            text=t("browse_default", "从默认路径安装", "Install from Default"),
            command=self._install_fonts_default,
        ).grid(row=0, column=2, padx=5)

        # Spacer
        ctk.CTkLabel(options_frame, text="").grid(row=4, column=0, pady=5)

    def _create_launcher_tab(self):
        """Create game launcher options tab"""
        tab = self.tab_launcher
        tab.grid_columnconfigure(0, weight=1)
        tab.grid_rowconfigure(0, weight=1)

        # Scrollable container
        scroll = ctk.CTkScrollableFrame(tab, fg_color="transparent")
        scroll.grid(row=0, column=0, sticky="nsew")
        scroll.grid_columnconfigure(0, weight=1)

        # Description
        desc_text = t(
            "launcher_desc",
            "获取游戏启动命令，用于在Steam中配置游戏以使用中文/日文环境。",
            "Get game launch commands to configure games in Steam for Chinese/Japanese environment.",
        )
        ctk.CTkLabel(scroll, text=desc_text, wraplength=700).grid(
            row=0, column=0, padx=20, pady=15, sticky="w"
        )

        # Launch command frame
        cmd_frame = ctk.CTkFrame(scroll)
        cmd_frame.grid(row=1, column=0, padx=20, pady=10, sticky="ew")
        cmd_frame.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            cmd_frame,
            text=t("launch_cmd", "启动命令", "Launch Command"),
            font=ctk.CTkFont(size=14, weight="bold"),
        ).grid(row=0, column=0, padx=15, pady=(15, 10), sticky="w")

        self.launch_cmd_var = tk.StringVar()
        cmd_entry = ctk.CTkEntry(
            cmd_frame,
            textvariable=self.launch_cmd_var,
            state="readonly",
            font=ctk.CTkFont(family="Consolas", size=12),
            height=40,
        )
        cmd_entry.grid(row=1, column=0, padx=15, pady=5, sticky="ew")

        btn_frame = ctk.CTkFrame(cmd_frame, fg_color="transparent")
        btn_frame.grid(row=2, column=0, padx=15, pady=(5, 15), sticky="w")

        ctk.CTkButton(
            btn_frame,
            text=t("copy", "复制到剪贴板", "Copy to Clipboard"),
            command=self._copy_launch_cmd,
        ).grid(row=0, column=0, padx=(0, 10))

        ctk.CTkButton(
            btn_frame,
            text=t("refresh_cmd", "刷新", "Refresh"),
            width=80,
            command=self._update_launch_cmd,
        ).grid(row=0, column=1)

        # Instructions frame
        instr_frame = ctk.CTkFrame(scroll)
        instr_frame.grid(row=2, column=0, padx=20, pady=10, sticky="ew")

        ctk.CTkLabel(
            instr_frame,
            text=t("instructions", "使用说明", "Instructions"),
            font=ctk.CTkFont(size=14, weight="bold"),
        ).grid(row=0, column=0, padx=15, pady=(15, 10), sticky="w")

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
        for i, instr in enumerate(instructions):
            ctk.CTkLabel(instr_frame, text=instr).grid(
                row=i + 1, column=0, padx=25, pady=3, sticky="w"
            )

        ctk.CTkLabel(instr_frame, text="").grid(
            row=len(instructions) + 1, column=0, pady=5
        )

        # Update command initially
        self.after(300, self._update_launch_cmd)

    def _create_log_area(self):
        """Create log output area"""
        log_frame = ctk.CTkFrame(self)
        log_frame.grid(row=3, column=0, padx=20, pady=(5, 15), sticky="ew")
        log_frame.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            log_frame,
            text=t("log", "操作日志", "Log"),
            font=ctk.CTkFont(weight="bold"),
        ).grid(row=0, column=0, padx=15, pady=(10, 5), sticky="w")

        self.log_text = ctk.CTkTextbox(log_frame, height=120, state="disabled")
        self.log_text.grid(row=1, column=0, padx=15, pady=(0, 15), sticky="ew")

    def _log(self, message: str, level: str = "info"):
        """Add message to log"""
        self.log_text.configure(state="normal")

        # Add color prefix based on level
        prefix = ""
        if level == "success":
            prefix = "[OK] "
        elif level == "error":
            prefix = "[ERROR] "
        elif level == "warning":
            prefix = "[WARN] "

        self.log_text.insert("end", prefix + message + "\n")
        self.log_text.see("end")
        self.log_text.configure(state="disabled")
        self.update_idletasks()

    def _show_language_dialog(self):
        """Show language selection dialog"""
        dialog = ctk.CTkToplevel(self)
        dialog.title(t("select_lang", "选择目标语言", "Select Target Language"))
        dialog.geometry("380x220")
        dialog.resizable(False, False)
        dialog.transient(self)

        # Content
        ctk.CTkLabel(
            dialog,
            text=t("choose_lang", "请选择目标语言:", "Choose target language:"),
            font=ctk.CTkFont(size=14, weight="bold"),
        ).pack(pady=(25, 15))

        lang_var = tk.StringVar(value=self.target_language or TargetLanguage.CHINESE)

        ctk.CTkRadioButton(
            dialog,
            text="简体中文 (Simplified Chinese)",
            variable=lang_var,
            value=TargetLanguage.CHINESE,
        ).pack(anchor="w", padx=40, pady=5)

        ctk.CTkRadioButton(
            dialog,
            text="日本語 (Japanese)",
            variable=lang_var,
            value=TargetLanguage.JAPANESE,
        ).pack(anchor="w", padx=40, pady=5)

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

        btn_frame = ctk.CTkFrame(dialog, fg_color="transparent")
        btn_frame.pack(pady=20)

        ctk.CTkButton(
            btn_frame, text=t("confirm", "确认", "Confirm"), command=on_confirm
        ).pack(side="left", padx=10)
        ctk.CTkButton(
            btn_frame, text=t("cancel", "取消", "Cancel"), command=dialog.destroy
        ).pack(side="left", padx=10)

        # Center and grab after content is created
        dialog.update_idletasks()
        x = self.winfo_x() + (self.winfo_width() - 380) // 2
        y = self.winfo_y() + (self.winfo_height() - 220) // 2
        dialog.geometry(f"+{x}+{y}")
        dialog.after(100, lambda: dialog.grab_set())

    def _install_locale(self):
        """Install locale"""
        if not self.target_language:
            show_warning(
                self,
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
            show_info(
                self,
                t("info", "提示", "Info"),
                t("locale_installed", "语言环境已安装", "Locale already installed"),
            )
            return

        # Confirm
        if not ask_yes_no(
            self,
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

        def log_to_gui(message: str):
            """Thread-safe logging to GUI"""
            self.after(0, lambda: self._log(message, "info"))

        def task():
            try:
                success, msg = setup_locale(locale_code, log_callback=log_to_gui)
                self.after(0, lambda: self._on_task_complete(success, msg))
            except Exception as e:
                self.after(0, lambda: self._on_task_complete(False, str(e)))

        threading.Thread(target=task, daemon=True).start()

    def _on_task_complete(self, success: bool, message: str):
        """Handle task completion"""
        if success:
            self._log(message, "success")
            show_success(self, t("success", "成功", "Success"), message)
        else:
            self._log(message, "error")
            show_error(self, t("error", "错误", "Error"), message)
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
                    self.after(
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

                self.after(0, lambda: self._show_font_selection(assets))
            except Exception as e:
                self.after(0, lambda: self._log(f"Error: {str(e)}", "error"))

        threading.Thread(target=fetch_and_show, daemon=True).start()

    def _show_font_selection(self, assets):
        """Show font selection dialog"""
        dialog = ctk.CTkToplevel(self)
        dialog.title(t("select_font", "选择字体包", "Select Font Package"))
        dialog.geometry("500x350")
        dialog.transient(self)

        dialog.grid_columnconfigure(0, weight=1)
        dialog.grid_rowconfigure(1, weight=1)

        ctk.CTkLabel(
            dialog,
            text=t("available_fonts", "可用字体包:", "Available font packages:"),
            font=ctk.CTkFont(size=14, weight="bold"),
        ).grid(row=0, column=0, padx=20, pady=(20, 10), sticky="w")

        # Scrollable frame for font list
        scroll_frame = ctk.CTkScrollableFrame(dialog)
        scroll_frame.grid(row=1, column=0, padx=20, pady=5, sticky="nsew")

        self.font_radio_var = tk.StringVar(value="0")
        for i, asset in enumerate(assets):
            size_mb = asset.size / (1024 * 1024)
            ctk.CTkRadioButton(
                scroll_frame,
                text=f"{asset.name} ({size_mb:.2f} MB)",
                variable=self.font_radio_var,
                value=str(i),
            ).pack(anchor="w", pady=5)

        def on_install():
            idx = int(self.font_radio_var.get())
            asset = assets[idx]
            dialog.destroy()
            self._download_and_install_font(asset)

        btn_frame = ctk.CTkFrame(dialog, fg_color="transparent")
        btn_frame.grid(row=2, column=0, pady=15)

        ctk.CTkButton(
            btn_frame, text=t("install", "安装", "Install"), command=on_install
        ).pack(side="left", padx=10)
        ctk.CTkButton(
            btn_frame, text=t("cancel", "取消", "Cancel"), command=dialog.destroy
        ).pack(side="left", padx=10)

        # Center and grab after content is created
        dialog.update_idletasks()
        x = self.winfo_x() + (self.winfo_width() - 500) // 2
        y = self.winfo_y() + (self.winfo_height() - 350) // 2
        dialog.geometry(f"+{x}+{y}")
        dialog.after(100, lambda: dialog.grab_set())

    def _download_and_install_font(self, asset):
        """Download font with progress dialog, then confirm before installing"""
        dialog = ctk.CTkToplevel(self)
        dialog.title(t("downloading", "下载中", "Downloading"))
        dialog.geometry("480x220")
        dialog.resizable(False, False)
        dialog.transient(self)

        # Prevent closing during download
        dialog.protocol("WM_DELETE_WINDOW", lambda: None)

        # Content
        ctk.CTkLabel(
            dialog,
            text=t("downloading_file", "正在下载文件:", "Downloading file:"),
            font=ctk.CTkFont(weight="bold"),
        ).pack(anchor="w", padx=25, pady=(20, 5))
        ctk.CTkLabel(dialog, text=asset.name, text_color="#3B8ED0").pack(
            anchor="w", padx=25, pady=(0, 15)
        )

        # Progress bar
        self.progress_bar = ctk.CTkProgressBar(dialog, width=430)
        self.progress_bar.pack(padx=25, pady=5)
        self.progress_bar.set(0)

        # Progress text
        self.progress_label = ctk.CTkLabel(dialog, text="0%  0.00 / 0.00 MB")
        self.progress_label.pack(anchor="w", padx=25, pady=5)

        # Status label
        self.status_label = ctk.CTkLabel(
            dialog,
            text=t("connecting", "正在连接...", "Connecting..."),
            text_color="gray",
        )
        self.status_label.pack(anchor="w", padx=25, pady=5)

        # Button frame
        self.dl_btn_frame = ctk.CTkFrame(dialog, fg_color="transparent")
        self.dl_btn_frame.pack(pady=10)

        # Track download state
        download_state = {
            "cancelled": False,
            "success": False,
            "zip_path": None,
            "error_msg": None,
        }

        def on_cancel():
            download_state["cancelled"] = True
            self.status_label.configure(
                text=t("cancelling", "正在取消...", "Cancelling...")
            )

        self.cancel_btn = ctk.CTkButton(
            self.dl_btn_frame, text=t("cancel", "取消", "Cancel"), command=on_cancel
        )
        self.cancel_btn.pack()

        # Center and grab after content is created
        dialog.update_idletasks()
        x = self.winfo_x() + (self.winfo_width() - 480) // 2
        y = self.winfo_y() + (self.winfo_height() - 220) // 2
        dialog.geometry(f"+{x}+{y}")
        dialog.after(100, lambda: dialog.grab_set())

        def update_progress(downloaded: int, total: int):
            """Update progress bar from download callback"""
            if total > 0:
                percent = downloaded / total
                mb_downloaded = downloaded / (1024 * 1024)
                mb_total = total / (1024 * 1024)

                def do_update():
                    self.progress_bar.set(percent)
                    self.progress_label.configure(
                        text=f"{percent * 100:.1f}%  {mb_downloaded:.2f} / {mb_total:.2f} MB"
                    )
                    self.status_label.configure(
                        text=t("downloading", "下载中...", "Downloading...")
                    )

                self.after(0, do_update)

        def download_task():
            """Background download task"""
            from src.core.downloader import FontReleaseDownloader

            try:
                downloader = FontReleaseDownloader()
                success, msg, zip_path = downloader.download_font(
                    asset, update_progress
                )

                if download_state["cancelled"]:
                    if zip_path and os.path.exists(zip_path):
                        try:
                            os.remove(zip_path)
                        except:
                            pass
                    self.after(0, dialog.destroy)
                    self.after(
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

                self.after(0, on_download_complete)

            except Exception as e:
                download_state["success"] = False
                download_state["error_msg"] = str(e)
                self.after(0, on_download_complete)

        def on_download_complete():
            """Handle download completion"""
            # Clear buttons
            for widget in self.dl_btn_frame.winfo_children():
                widget.destroy()

            dialog.protocol("WM_DELETE_WINDOW", dialog.destroy)

            if download_state["success"] and download_state["zip_path"]:
                self.progress_bar.set(1)
                self.progress_label.configure(
                    text="100%  " + t("complete", "完成", "Complete")
                )
                self.status_label.configure(
                    text=t(
                        "download_success",
                        "下载成功！点击安装按钮开始安装字体。",
                        "Download successful! Click Install to begin.",
                    ),
                    text_color="#2FA572",
                )

                self._log(
                    t(
                        "download_complete",
                        f"下载完成: {asset.name}",
                        f"Download complete: {asset.name}",
                    ),
                    "success",
                )

                def on_install():
                    dialog.destroy()
                    self._install_downloaded_font(
                        download_state["zip_path"], asset.name
                    )

                def on_close():
                    dialog.destroy()
                    self._log(
                        t("install_skipped", "已跳过安装", "Installation skipped"),
                        "warning",
                    )

                ctk.CTkButton(
                    self.dl_btn_frame,
                    text=t("install", "安装", "Install"),
                    command=on_install,
                ).pack(side="left", padx=10)
                ctk.CTkButton(
                    self.dl_btn_frame,
                    text=t("close", "关闭", "Close"),
                    command=on_close,
                ).pack(side="left", padx=10)
            else:
                self.status_label.configure(
                    text=t("download_failed", "下载失败", "Download failed"),
                    text_color="#E74C3C",
                )

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

                ctk.CTkButton(
                    self.dl_btn_frame,
                    text=t("close", "关闭", "Close"),
                    command=dialog.destroy,
                ).pack()

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
                self.after(0, lambda: self._on_task_complete(success, msg))
            except Exception as e:
                self.after(0, lambda: self._on_task_complete(False, str(e)))

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
                self.after(0, lambda: self._on_task_complete(success, msg))
            except Exception as e:
                self.after(0, lambda: self._on_task_complete(False, str(e)))

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
            show_warning(
                self,
                t("warning", "警告", "Warning"),
                t(
                    "set_default_first",
                    "请先设置默认字体路径",
                    "Please set default font path first",
                ),
            )
            return

        if not os.path.isdir(default_path):
            show_error(
                self,
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
            show_info(
                self,
                t("info", "提示", "Info"),
                t(
                    "no_zip_found",
                    "在默认路径中未找到zip文件",
                    "No zip files found in default path",
                ),
            )
            return

        # Show selection dialog
        dialog = ctk.CTkToplevel(self)
        dialog.title(t("select_font", "选择字体包", "Select Font Package"))
        dialog.geometry("450x300")
        dialog.transient(self)

        dialog.grid_columnconfigure(0, weight=1)
        dialog.grid_rowconfigure(0, weight=1)

        scroll_frame = ctk.CTkScrollableFrame(dialog)
        scroll_frame.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")

        file_var = tk.StringVar(value="0")
        for i, f in enumerate(zip_files):
            file_path = os.path.join(default_path, f)
            size_mb = os.path.getsize(file_path) / (1024 * 1024)
            ctk.CTkRadioButton(
                scroll_frame,
                text=f"{f} ({size_mb:.2f} MB)",
                variable=file_var,
                value=str(i),
            ).pack(anchor="w", pady=5)

        def on_install():
            idx = int(file_var.get())
            file_name = zip_files[idx]
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
                    self.after(0, lambda: self._on_task_complete(success, msg))
                except Exception as e:
                    self.after(0, lambda: self._on_task_complete(False, str(e)))

            threading.Thread(target=task, daemon=True).start()

        btn_frame = ctk.CTkFrame(dialog, fg_color="transparent")
        btn_frame.grid(row=1, column=0, pady=10)

        ctk.CTkButton(
            btn_frame, text=t("install", "安装", "Install"), command=on_install
        ).pack(side="left", padx=10)
        ctk.CTkButton(
            btn_frame, text=t("cancel", "取消", "Cancel"), command=dialog.destroy
        ).pack(side="left", padx=10)

        # Center and grab after content is created
        dialog.update_idletasks()
        x = self.winfo_x() + (self.winfo_width() - 450) // 2
        y = self.winfo_y() + (self.winfo_height() - 300) // 2
        dialog.geometry(f"+{x}+{y}")
        dialog.after(100, lambda: dialog.grab_set())

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
            self.clipboard_clear()
            self.clipboard_append(cmd)
            self._log(t("copied", "已复制到剪贴板", "Copied to clipboard"), "success")

    def _refresh_games_list(self):
        """Refresh managed games list"""
        # Clear existing items
        for widget in self.games_scroll.winfo_children():
            if widget.grid_info().get("row", 0) > 0:  # Keep header
                widget.destroy()

        # Get managed games from config
        managed_games = Config.get_managed_games()

        if not managed_games:
            ctk.CTkLabel(
                self.games_scroll,
                text=t(
                    "no_games",
                    "暂无游戏，使用下方按钮添加",
                    "No games yet, use button below to add",
                ),
                text_color="gray",
            ).grid(row=1, column=0, columnspan=3, padx=5, pady=20)
            return

        # Populate with game data
        for i, game in enumerate(managed_games):
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

            row = i + 1
            ctk.CTkLabel(self.games_scroll, text=game_name).grid(
                row=row, column=0, padx=5, pady=3, sticky="w"
            )
            ctk.CTkLabel(
                self.games_scroll, text=game_path, text_color="gray", wraplength=250
            ).grid(row=row, column=1, padx=5, pady=3, sticky="w")
            ctk.CTkLabel(self.games_scroll, text=lang_display).grid(
                row=row, column=2, padx=5, pady=3, sticky="w"
            )

            # Delete button
            ctk.CTkButton(
                self.games_scroll,
                text="×",
                width=30,
                height=25,
                fg_color="#E74C3C",
                hover_color="#C0392B",
                command=lambda n=game_name: self._remove_game(n),
            ).grid(row=row, column=3, padx=5, pady=3)

    def _remove_game(self, game_name: str):
        """Remove a game from the list"""
        if not ask_yes_no(
            self,
            t("confirm", "确认", "Confirm"),
            t(
                "confirm_remove_game",
                f"确认从列表中移除游戏?\n{game_name}",
                f"Remove game from list?\n{game_name}",
            ),
        ):
            return

        managed_games = Config.get_managed_games()
        managed_games = [g for g in managed_games if g.get("name") != game_name]
        Config.set_managed_games(managed_games)

        self._refresh_games_list()
        self._log(
            t(
                "game_removed",
                f"游戏已从列表移除: {game_name}",
                f"Game removed: {game_name}",
            ),
            "success",
        )

    def _browse_add_game(self):
        """Browse and add game to Steam"""
        if not self.target_language:
            show_warning(
                self,
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

        # Show input dialog
        dialog = ctk.CTkToplevel(self)
        dialog.title(t("add_game", "添加游戏", "Add Game"))
        dialog.geometry("500x350")
        dialog.transient(self)

        dialog.grid_columnconfigure(0, weight=1)

        # Executable path
        ctk.CTkLabel(
            dialog,
            text=t("game_exe", "可执行文件:", "Executable:"),
            font=ctk.CTkFont(weight="bold"),
        ).grid(row=0, column=0, padx=25, pady=(25, 5), sticky="w")
        ctk.CTkLabel(dialog, text=file_path, text_color="#3B8ED0", wraplength=450).grid(
            row=1, column=0, padx=25, pady=(0, 10), sticky="w"
        )

        # Game name
        ctk.CTkLabel(
            dialog,
            text=t("game_name", "游戏名称:", "Game Name:"),
            font=ctk.CTkFont(weight="bold"),
        ).grid(row=2, column=0, padx=25, pady=(10, 5), sticky="w")
        name_entry = ctk.CTkEntry(dialog, width=450)
        name_entry.insert(0, default_name)
        name_entry.grid(row=3, column=0, padx=25, pady=(0, 10), sticky="w")

        # Launch options
        launch_options = get_locale_command(self.target_language)
        ctk.CTkLabel(
            dialog,
            text=t("launch_opts", "启动选项:", "Launch Options:"),
            font=ctk.CTkFont(weight="bold"),
        ).grid(row=4, column=0, padx=25, pady=(10, 5), sticky="w")
        ctk.CTkLabel(
            dialog, text=launch_options, text_color="#2FA572", wraplength=450
        ).grid(row=5, column=0, padx=25, pady=(0, 20), sticky="w")

        def on_add():
            game_name = name_entry.get().strip()
            if not game_name:
                show_warning(
                    self,
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

                    if success:
                        game_data = {
                            "name": game_name,
                            "exe_path": file_path,
                            "language": self.target_language,
                            "launch_options": launch_options,
                        }
                        Config.add_managed_game(game_data)
                        self.after(0, self._refresh_games_list)

                    self.after(0, lambda: self._on_task_complete(success, msg))
                except Exception as e:
                    self.after(0, lambda: self._on_task_complete(False, str(e)))

            threading.Thread(target=task, daemon=True).start()

        btn_frame = ctk.CTkFrame(dialog, fg_color="transparent")
        btn_frame.grid(row=6, column=0, pady=15)

        ctk.CTkButton(btn_frame, text=t("add", "添加", "Add"), command=on_add).pack(
            side="left", padx=10
        )
        ctk.CTkButton(
            btn_frame, text=t("cancel", "取消", "Cancel"), command=dialog.destroy
        ).pack(side="left", padx=10)

        # Center and grab after content is created
        dialog.update_idletasks()
        x = self.winfo_x() + (self.winfo_width() - 500) // 2
        y = self.winfo_y() + (self.winfo_height() - 350) // 2
        dialog.geometry(f"+{x}+{y}")
        dialog.after(100, lambda: dialog.grab_set())


def main():
    """Main function"""
    app = GUIApplication()
    try:
        app.mainloop()
    except KeyboardInterrupt:
        pass
    except Exception as e:
        show_error(app, "Error", f"Application error: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
