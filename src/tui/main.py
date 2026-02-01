"""
TUI Main Program - Interactive terminal interface using Rich library
"""

import os
import sys
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.prompt import Prompt, Confirm
from rich.text import Text
import threading

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


class TUIApplication:
    """TUI Application"""
    
    def __init__(self):
        self.console = Console()
        self.running = True
        self.target_language = None  # Will be set by show_language_selection
    
    def clear_screen(self):
        """Clear screen"""
        os.system('clear' if os.name != 'nt' else 'cls')
    
    def show_language_selection(self) -> str:
        """
        Show target language selection menu
        Returns: Selected language code ('zh' or 'ja')
        """
        self.clear_screen()
        
        # Check if language is already selected
        saved_lang = Config.get_target_language()
        if saved_lang:
            # Show current selection and ask if user wants to change
            self.console.print(f"\n[cyan]Current target language: {TargetLanguage.get_name(saved_lang, 'zh' if is_chinese() else 'en')}[/cyan]\n")
            if not Confirm.ask(t('change_lang', '是否更改目标语言？', 'Change target language?')):
                self.target_language = saved_lang
                return saved_lang
        
        # Show language selection
        self.console.print(Panel(
            Text(t('select_target', '选择目标语言 / Select Target Language', 'Select Target Language'), style="bold cyan"),
            style="bold blue",
            expand=True
        ))
        
        self.console.print()
        table = Table(show_header=False, show_footer=False, box=None)
        table.add_column(style="cyan")
        
        if is_chinese():
            table.add_row("[1] 简体中文 (Simplified Chinese)")
            table.add_row("[2] 日本語 (Japanese)")
        else:
            table.add_row("[1] Simplified Chinese (简体中文)")
            table.add_row("[2] Japanese (日本語)")
        
        self.console.print(table)
        self.console.print()
        
        choice = Prompt.ask(
            t('select', '请选择', 'Select'),
            choices=["1", "2"]
        )
        
        lang = TargetLanguage.CHINESE if choice == "1" else TargetLanguage.JAPANESE
        Config.set_target_language(lang)
        self.target_language = lang
        return lang
    
    def print_header(self):
        """Print application header"""
        header = Text()
        title = "SteamDeck Chinese Environment Config Tool"
        header.append(title, style="bold cyan")
        
        panel = Panel(
            header,
            title="[bold]SteamDeck Config[/bold]",
            style="bold blue",
            expand=True
        )
        self.console.print(panel)
    
    def show_main_menu(self) -> str:
        """Show main menu and return user choice"""
        self.clear_screen()
        self.print_header()
        
        # Get target language name for menu (use default if not set)
        target_lang = self.target_language or Config.get_target_language()
        target_lang_name = TargetLanguage.get_name(target_lang, 'zh' if is_chinese() else 'en')
        
        table = Table(show_header=False, show_footer=False, box=None)
        table.add_column(style="cyan")
        
        if is_chinese():
            table.add_row(f"[1] 安装{target_lang_name}语言环境")
            table.add_row(f"[2] 安装{target_lang_name}字体")
            table.add_row("[3] 游戏启动选项")
            table.add_row("[4] 添加非Steam游戏到Steam库")
            table.add_row("[5] 系统状态")
            table.add_row(f"[6] 更改目标语言 (当前: {target_lang_name})")
            table.add_row("[7] 退出")
        else:
            table.add_row(f"[1] Install {target_lang_name} Locale")
            table.add_row(f"[2] Install {target_lang_name} Fonts")
            table.add_row("[3] Game Launch Options")
            table.add_row("[4] Add Non-Steam Game to Steam")
            table.add_row("[5] System Status")
            table.add_row(f"[6] Change Target Language (Current: {target_lang_name})")
            table.add_row("[7] Exit")
        
        self.console.print(table)
        self.console.print()
        
        prompt_text = "Select function"
        choice = Prompt.ask(prompt_text, choices=["1", "2", "3", "4", "5", "6", "7"])
        return choice
    
    def show_locale_menu(self):
        """Show Locale menu"""
        self.clear_screen()
        self.print_header()
        
        target_lang = self.target_language or Config.get_target_language()
        target_lang_name = TargetLanguage.get_name(target_lang, 'zh' if is_chinese() else 'en')
        locale_code = TargetLanguage.get_locale(target_lang)
        
        if is_chinese():
            self.console.print(f"\n[bold cyan]功能 1: 安装{target_lang_name}语言环境[/bold cyan]\n")
            
            # Check current status
            is_installed = check_locale_status(locale_code)
            status_text = "[green]OK[/green]" if is_installed else "[red]X[/red]"
            
            self.console.print(f"状态: {status_text}\n")
            
            if is_installed:
                self.console.print(f"[yellow]{target_lang_name}语言环境已安装。[/yellow]\n")
                Prompt.ask("按回车返回", default="")
                return
            
            self.console.print("[cyan]此操作将:[/cyan]")
            self.console.print("  1. 禁用 SteamOS 只读模式")
            self.console.print("  2. 初始化 pacman 密钥")
            self.console.print(f"  3. 启用{target_lang_name}语言环境 ({locale_code})")
            self.console.print("  4. 生成语言环境")
            self.console.print("  5. 恢复 SteamOS 只读模式\n")
            
            if not Confirm.ask("[yellow]需要 root 权限，是否继续?[/yellow]"):
                self.console.print("[yellow]已取消[/yellow]")
                Prompt.ask("按回车返回", default="")
                return
            
            self._run_task_with_progress(f"安装{target_lang_name}语言环境", setup_locale, locale_code)
            
            Prompt.ask("按回车返回", default="")
        else:
            self.console.print(f"\n[bold cyan]Function 1: Install {target_lang_name} Locale[/bold cyan]\n")
            
            # Check current status
            is_installed = check_locale_status(locale_code)
            status_text = "[green]OK[/green]" if is_installed else "[red]X[/red]"
            
            self.console.print(f"Status: {status_text}\n")
            
            if is_installed:
                self.console.print(f"[yellow]{target_lang_name} locale already installed.[/yellow]\n")
                Prompt.ask("Press Enter to return", default="")
                return
            
            self.console.print("[cyan]This will:[/cyan]")
            self.console.print("  1. Disable SteamOS read-only mode")
            self.console.print("  2. Initialize pacman keys")
            self.console.print(f"  3. Enable {target_lang_name} locale ({locale_code})")
            self.console.print("  4. Generate locale")
            self.console.print("  5. Restore SteamOS read-only mode\n")
            
            if not Confirm.ask("[yellow]Requires root permission, continue?[/yellow]"):
                self.console.print("[yellow]Cancelled[/yellow]")
                Prompt.ask("Press Enter to return", default="")
                return
            
            self._run_task_with_progress(f"Installing {target_lang_name} Locale", setup_locale, locale_code)
            
            Prompt.ask("Press Enter to return", default="")
    
    def show_font_menu(self):
        """Show Font menu"""
        self.clear_screen()
        self.print_header()
        
        target_lang = self.target_language or Config.get_target_language()
        target_lang_name = TargetLanguage.get_name(target_lang, 'zh' if is_chinese() else 'en')
        
        # Check current status
        is_installed = check_fonts_status()
        count = get_fonts_count()
        status_text = f"[green]OK ({count})[/green]" if is_installed else "[red]X[/red]"
        
        # Check if default font path is configured
        default_path = Config.get_default_font_path()
        default_path_info = f"[cyan]{default_path}[/cyan]" if default_path else "[yellow]Not configured[/yellow]"
        
        if is_chinese():
            self.console.print(f"\n[bold cyan]功能 2: 安装{target_lang_name}字体[/bold cyan]\n")
            self.console.print(f"状态: {status_text}")
            self.console.print(f"默认字体路径: {default_path_info}\n")
            
            self.console.print("[cyan]选择安装方式:[/cyan]")
            self.console.print("[1] 从 GitHub 下载")
            self.console.print("[2] 使用本地字体包（手动输入路径）")
            self.console.print("[3] 从默认字体路径选择")
            self.console.print("[4] 设置默认字体路径")
            self.console.print("[5] 返回主菜单\n")
        else:
            self.console.print(f"\n[bold cyan]Function 2: Install {target_lang_name} Fonts[/bold cyan]\n")
            self.console.print(f"Status: {status_text}")
            self.console.print(f"Default font path: {default_path_info}\n")
            
            self.console.print("[cyan]Select installation method:[/cyan]")
            self.console.print("[1] Download from GitHub")
            self.console.print("[2] Use local font package (manual input)")
            self.console.print("[3] Browse default font path")
            self.console.print("[4] Set default font path")
            self.console.print("[5] Return to menu\n")
        
        choice = Prompt.ask("选择" if is_chinese() else "Select", choices=["1", "2", "3", "4", "5"])
        
        if choice == "1":
            self._install_fonts_from_github()
        elif choice == "2":
            self._install_fonts_from_local()
        elif choice == "3":
            self._install_fonts_from_default_path()
        elif choice == "4":
            self._set_default_font_path()
    
    def _install_fonts_from_github(self):
        """Download and install fonts from GitHub"""
        self.clear_screen()
        self.print_header()
        
        if is_chinese():
            self.console.print("\n[cyan]Fetching available font packages...[/cyan]\n")
        else:
            self.console.print("\n[cyan]Fetching available font packages...[/cyan]\n")
        
        try:
            success, assets = list_available_fonts()
            if not success or not assets:
                error_msg = "[red]X Cannot get font list[/red]" if is_chinese() else "[red]X Cannot get font list[/red]"
                self.console.print(error_msg + "\n")
                Prompt.ask("Press Enter" if is_chinese() else "Press Enter", default="")
                return
            
            # Display available font packages
            title = "Available Fonts" if is_chinese() else "Available Fonts"
            table = Table(title=title, show_header=True)
            table.add_column("No." if is_chinese() else "No.", style="cyan")
            table.add_column("Name" if is_chinese() else "Name")
            table.add_column("Size" if is_chinese() else "Size")
            
            for idx, asset in enumerate(assets, 1):
                size_mb = asset.size / (1024 * 1024)
                table.add_row(str(idx), asset.name, f"{size_mb:.2f} MB")
            
            self.console.print(table)
            self.console.print()
            
            prompt = "Select font package" if is_chinese() else "Select font package"
            choice = Prompt.ask(prompt, choices=[str(i) for i in range(1, len(assets) + 1)])
            selected_asset = assets[int(choice) - 1]
            
            confirm_msg = f"\n[yellow]Confirm download and install {selected_asset.name}?[/yellow]" if is_chinese() else f"\n[yellow]Confirm download and install {selected_asset.name}?[/yellow]"
            if not Confirm.ask(confirm_msg):
                self.console.print("[yellow]Cancelled[/yellow]" if is_chinese() else "[yellow]Cancelled[/yellow]")
                Prompt.ask("Press Enter" if is_chinese() else "Press Enter", default="")
                return
            
            task_name = f"Download and install {selected_asset.name}"
            self._run_task_with_progress(
                task_name,
                download_and_install_fonts,
                selected_asset
            )
        
        except Exception as e:
            error = f"[red]X Error: {str(e)}[/red]" if is_chinese() else f"[red]X Error: {str(e)}[/red]"
            self.console.print(error + "\n")
        
        Prompt.ask("Press Enter" if is_chinese() else "Press Enter", default="")
    
    def _install_fonts_from_local(self):
        """Install fonts from local file"""
        self.clear_screen()
        self.print_header()
        
        if is_chinese():
            self.console.print("\n[cyan]Enter full path to local font package:[/cyan]\n")
            zip_path = Prompt.ask("Font package path")
        else:
            self.console.print("\n[cyan]Enter full path to local font package:[/cyan]\n")
            zip_path = Prompt.ask("Font package path")
        
        if not os.path.isfile(zip_path):
            error = f"[red]X File not found: {zip_path}[/red]" if is_chinese() else f"[red]X File not found: {zip_path}[/red]"
            self.console.print(error + "\n")
            Prompt.ask("Press Enter" if is_chinese() else "Press Enter", default="")
            return
        
        confirm_msg = f"\n[yellow]Confirm use {os.path.basename(zip_path)}?[/yellow]" if is_chinese() else f"\n[yellow]Confirm use {os.path.basename(zip_path)}?[/yellow]"
        if not Confirm.ask(confirm_msg):
            self.console.print("[yellow]Cancelled[/yellow]" if is_chinese() else "[yellow]Cancelled[/yellow]")
            Prompt.ask("Press Enter" if is_chinese() else "Press Enter", default="")
            return
        
        task_name = f"Install font: {os.path.basename(zip_path)}" if is_chinese() else f"Install font: {os.path.basename(zip_path)}"
        self._run_task_with_progress(
            task_name,
            setup_fonts,
            zip_path
        )
        
        Prompt.ask("Press Enter" if is_chinese() else "Press Enter", default="")
    
    def _set_default_font_path(self):
        """Set default font zip package search path"""
        self.clear_screen()
        self.print_header()
        
        current_path = Config.get_default_font_path()
        
        if is_chinese():
            self.console.print("\n[cyan]设置默认字体包路径[/cyan]\n")
            if current_path:
                self.console.print(f"当前路径: [yellow]{current_path}[/yellow]\n")
            else:
                self.console.print("当前路径: [yellow]未设置[/yellow]\n")
            
            new_path = Prompt.ask("请输入新的默认路径（留空取消）")
        else:
            self.console.print("\n[cyan]Set Default Font Package Path[/cyan]\n")
            if current_path:
                self.console.print(f"Current path: [yellow]{current_path}[/yellow]\n")
            else:
                self.console.print("Current path: [yellow]Not set[/yellow]\n")
            
            new_path = Prompt.ask("Enter new default path (leave empty to cancel)")
        
        if not new_path:
            self.console.print("[yellow]Cancelled[/yellow]" if is_chinese() else "[yellow]Cancelled[/yellow]")
            Prompt.ask("Press Enter" if is_chinese() else "Press Enter", default="")
            return
        
        # Validate path
        if not os.path.isdir(new_path):
            self.console.print(f"[red]X 路径不存在: {new_path}[/red]" if is_chinese() else f"[red]X Path does not exist: {new_path}[/red]")
            Prompt.ask("Press Enter" if is_chinese() else "Press Enter", default="")
            return
        
        Config.set_default_font_path(new_path)
        self.console.print("[green]✓ 默认路径已设置[/green]" if is_chinese() else "[green]✓ Default path set successfully[/green]")
        Prompt.ask("Press Enter" if is_chinese() else "Press Enter", default="")
    
    def _install_fonts_from_default_path(self):
        """Install fonts from default path"""
        self.clear_screen()
        self.print_header()
        
        default_path = Config.get_default_font_path()
        
        if not default_path:
            self.console.print("[yellow]Default font path not configured. Please set it first.[/yellow]" if not is_chinese() else "[yellow]默认字体路径未配置，请先设置。[/yellow]")
            Prompt.ask("Press Enter" if is_chinese() else "Press Enter", default="")
            return
        
        if not os.path.isdir(default_path):
            self.console.print(f"[red]X Default path does not exist: {default_path}[/red]" if not is_chinese() else f"[red]X 默认路径不存在: {default_path}[/red]")
            Prompt.ask("Press Enter" if is_chinese() else "Press Enter", default="")
            return
        
        # List zip files in the directory
        try:
            zip_files = [f for f in os.listdir(default_path) if f.lower().endswith('.zip')]
            
            if not zip_files:
                self.console.print("[yellow]No zip files found in default path[/yellow]" if not is_chinese() else "[yellow]默认路径中未找到 zip 文件[/yellow]")
                Prompt.ask("Press Enter" if is_chinese() else "Press Enter", default="")
                return
            
            # Display available font packages
            if is_chinese():
                self.console.print(f"\n[cyan]在默认路径中找到 {len(zip_files)} 个字体包:[/cyan]\n")
            else:
                self.console.print(f"\n[cyan]Found {len(zip_files)} font packages in default path:[/cyan]\n")
            
            table = Table(show_header=True)
            table.add_column("编号" if is_chinese() else "No.", style="cyan")
            table.add_column("文件名" if is_chinese() else "File Name")
            table.add_column("大小" if is_chinese() else "Size")
            
            for idx, zip_file in enumerate(zip_files, 1):
                file_path = os.path.join(default_path, zip_file)
                size_mb = os.path.getsize(file_path) / (1024 * 1024)
                table.add_row(str(idx), zip_file, f"{size_mb:.2f} MB")
            
            self.console.print(table)
            self.console.print()
            
            # Let user select a package
            choices = [str(i) for i in range(1, len(zip_files) + 1)] + ['0']
            prompt = "选择字体包 (0=取消)" if is_chinese() else "Select font package (0=Cancel)"
            choice = Prompt.ask(prompt, choices=choices)
            
            if choice == '0':
                self.console.print("[yellow]Cancelled[/yellow]" if is_chinese() else "[yellow]Cancelled[/yellow]")
                Prompt.ask("Press Enter" if is_chinese() else "Press Enter", default="")
                return
            
            selected_file = zip_files[int(choice) - 1]
            selected_path = os.path.join(default_path, selected_file)
            
            # Confirm with user
            if is_chinese():
                if not Confirm.ask(f"\n[yellow]确认安装 {selected_file}?[/yellow]"):
                    self.console.print("[yellow]已取消[/yellow]")
                    Prompt.ask("按回车返回", default="")
                    return
            else:
                if not Confirm.ask(f"\n[yellow]Confirm install {selected_file}?[/yellow]"):
                    self.console.print("[yellow]Cancelled[/yellow]")
                    Prompt.ask("Press Enter to return", default="")
                    return
            
            task_name = f"安装字体: {selected_file}" if is_chinese() else f"Installing font: {selected_file}"
            self._run_task_with_progress(
                task_name,
                setup_fonts,
                selected_path
            )
            
        except Exception as e:
            error = f"[red]X 错误: {str(e)}[/red]" if is_chinese() else f"[red]X Error: {str(e)}[/red]"
            self.console.print(error + "\n")
        
        Prompt.ask("Press Enter" if is_chinese() else "Press Enter", default="")
    
    def show_system_status(self):
        """Show system status"""
        self.clear_screen()
        self.print_header()
        
        target_lang = self.target_language or Config.get_target_language()
        target_lang_name = TargetLanguage.get_name(target_lang, 'zh' if is_chinese() else 'en')
        locale_code = TargetLanguage.get_locale(target_lang)
        
        if is_chinese():
            self.console.print("\n[bold cyan]系统状态[/bold cyan]\n")
            
            table = Table(show_header=True)
            table.add_column("功能", style="cyan")
            table.add_column("状态")
            
            # Target language
            table.add_row("目标语言", f"[cyan]{target_lang_name}[/cyan]")
            
            # Locale status
            locale_installed = check_locale_status(locale_code)
            locale_status = "[green]OK[/green]" if locale_installed else "[red]X[/red]"
            table.add_row(f"{target_lang_name}语言环境", locale_status)
            
            # Font status
            fonts_installed = check_fonts_status()
            fonts_count = get_fonts_count()
            fonts_status = f"[green]OK ({fonts_count})[/green]" if fonts_installed else "[red]X[/red]"
            table.add_row(f"{target_lang_name}字体", fonts_status)
            
            self.console.print(table)
            self.console.print()
            
            Prompt.ask("按回车返回", default="")
        else:
            self.console.print("\n[bold cyan]System Status[/bold cyan]\n")
            
            table = Table(show_header=True)
            table.add_column("Function", style="cyan")
            table.add_column("Status")
            
            # Target language
            table.add_row("Target Language", f"[cyan]{target_lang_name}[/cyan]")
            
            # Check locale status
            locale_installed = check_locale_status(locale_code)
            locale_status = "[green]OK[/green]" if locale_installed else "[red]X[/red]"
            table.add_row(f"{target_lang_name} Locale", locale_status)
            
            # Check font status
            fonts_installed = check_fonts_status()
            fonts_count = get_fonts_count()
            fonts_status = f"[green]OK ({fonts_count})[/green]" if fonts_installed else "[red]X[/red]"
            table.add_row(f"{target_lang_name} Fonts", fonts_status)
            
            self.console.print(table)
            self.console.print()
            
            Prompt.ask("Press Enter to return", default="")
    
    def show_add_game_menu(self):
        """Show add non-Steam game menu"""
        self.clear_screen()
        self.print_header()
        
        target_lang = self.target_language or Config.get_target_language()
        target_lang_name = TargetLanguage.get_name(target_lang, 'zh' if is_chinese() else 'en')
        
        if is_chinese():
            self.console.print(f"\n[bold cyan]功能 4: 添加非Steam游戏[/bold cyan]\n")
            
            self.console.print("[cyan]选择操作:[/cyan]")
            self.console.print("[1] 管理游戏搜索路径")
            self.console.print("[2] 浏览并添加游戏")
            self.console.print("[3] 返回主菜单\n")
        else:
            self.console.print(f"\n[bold cyan]Function 4: Add Non-Steam Game[/bold cyan]\n")
            
            self.console.print("[cyan]Select action:[/cyan]")
            self.console.print("[1] Manage game search paths")
            self.console.print("[2] Browse and add game")
            self.console.print("[3] Return to main menu\n")
        
        choice = Prompt.ask("选择" if is_chinese() else "Select", choices=["1", "2", "3"])
        
        if choice == "1":
            self._manage_game_search_paths()
        elif choice == "2":
            self._browse_and_add_game()
    
    def _manage_game_search_paths(self):
        """Manage game search paths"""
        while True:
            self.clear_screen()
            self.print_header()
            
            if is_chinese():
                self.console.print("\n[bold cyan]管理游戏搜索路径[/bold cyan]\n")
            else:
                self.console.print("\n[bold cyan]Manage Game Search Paths[/bold cyan]\n")
            
            paths = get_game_search_paths()
            
            if paths:
                table = Table(show_header=True)
                table.add_column("编号" if is_chinese() else "No.", style="cyan")
                table.add_column("路径" if is_chinese() else "Path")
                
                for idx, path in enumerate(paths, 1):
                    table.add_row(str(idx), path)
                
                self.console.print(table)
                self.console.print()
            else:
                self.console.print("[yellow]没有配置的搜索路径[/yellow]\n" if is_chinese() else "[yellow]No configured search paths[/yellow]\n")
            
            if is_chinese():
                self.console.print("[cyan]选择操作:[/cyan]")
                self.console.print("[1] 添加新路径")
                self.console.print("[2] 删除路径")
                self.console.print("[3] 返回\n")
            else:
                self.console.print("[cyan]Select action:[/cyan]")
                self.console.print("[1] Add new path")
                self.console.print("[2] Remove path")
                self.console.print("[3] Return\n")
            
            choice = Prompt.ask("选择" if is_chinese() else "Select", choices=["1", "2", "3"])
            
            if choice == "1":
                new_path = Prompt.ask("输入路径" if is_chinese() else "Enter path")
                success, msg = add_game_search_path(new_path)
                if success:
                    self.console.print(f"[green]✓ {msg}[/green]")
                else:
                    self.console.print(f"[red]X {msg}[/red]")
                Prompt.ask("按回车继续" if is_chinese() else "Press Enter to continue", default="")
            elif choice == "2":
                if not paths:
                    self.console.print("[yellow]没有路径可删除[/yellow]" if is_chinese() else "[yellow]No paths to remove[/yellow]")
                    Prompt.ask("按回车继续" if is_chinese() else "Press Enter to continue", default="")
                    continue
                
                choices = [str(i) for i in range(1, len(paths) + 1)] + ['0']
                idx_choice = Prompt.ask("选择要删除的路径 (0=取消)" if is_chinese() else "Select path to remove (0=Cancel)", choices=choices)
                
                if idx_choice != '0':
                    path_to_remove = paths[int(idx_choice) - 1]
                    success, msg = remove_game_search_path(path_to_remove)
                    if success:
                        self.console.print(f"[green]✓ {msg}[/green]")
                    else:
                        self.console.print(f"[red]X {msg}[/red]")
                    Prompt.ask("按回车继续" if is_chinese() else "Press Enter to continue", default="")
            elif choice == "3":
                break
    
    def _browse_and_add_game(self):
        """Browse directories and add game to Steam"""
        self.clear_screen()
        self.print_header()
        
        target_lang = self.target_language or Config.get_target_language()
        
        # Get search paths
        paths = get_game_search_paths()
        
        if not paths:
            if is_chinese():
                self.console.print("\n[yellow]请先配置游戏搜索路径[/yellow]\n")
            else:
                self.console.print("\n[yellow]Please configure game search paths first[/yellow]\n")
            Prompt.ask("按回车返回" if is_chinese() else "Press Enter to return", default="")
            return
        
        # Let user select search path
        if is_chinese():
            self.console.print("\n[cyan]选择搜索路径:[/cyan]\n")
        else:
            self.console.print("\n[cyan]Select search path:[/cyan]\n")
        
        table = Table(show_header=True)
        table.add_column("编号" if is_chinese() else "No.", style="cyan")
        table.add_column("路径" if is_chinese() else "Path")
        
        for idx, path in enumerate(paths, 1):
            table.add_row(str(idx), path)
        
        self.console.print(table)
        self.console.print()
        
        choices = [str(i) for i in range(1, len(paths) + 1)] + ['0']
        path_choice = Prompt.ask("选择路径 (0=取消)" if is_chinese() else "Select path (0=Cancel)", choices=choices)
        
        if path_choice == '0':
            return
        
        selected_path = paths[int(path_choice) - 1]
        
        # Browse directory
        current_path = selected_path
        
        while True:
            self.clear_screen()
            self.print_header()
            
            if is_chinese():
                self.console.print(f"\n[cyan]当前路径: {current_path}[/cyan]\n")
            else:
                self.console.print(f"\n[cyan]Current path: {current_path}[/cyan]\n")
            
            subdirs, exe_files = SteamManager.browse_directory(current_path)
            
            # Display directories
            if subdirs:
                if is_chinese():
                    self.console.print("[bold]文件夹:[/bold]")
                else:
                    self.console.print("[bold]Folders:[/bold]")
                
                dir_table = Table(show_header=True)
                dir_table.add_column("编号" if is_chinese() else "No.", style="cyan")
                dir_table.add_column("名称" if is_chinese() else "Name")
                
                for idx, subdir in enumerate(subdirs, 1):
                    dir_table.add_row(f"D{idx}", subdir)
                
                self.console.print(dir_table)
                self.console.print()
            
            # Display exe files
            if exe_files:
                if is_chinese():
                    self.console.print("[bold]可执行文件:[/bold]")
                else:
                    self.console.print("[bold]Executable files:[/bold]")
                
                exe_table = Table(show_header=True)
                exe_table.add_column("编号" if is_chinese() else "No.", style="cyan")
                exe_table.add_column("名称" if is_chinese() else "Name")
                
                for idx, exe in enumerate(exe_files, 1):
                    exe_table.add_row(f"E{idx}", exe)
                
                self.console.print(exe_table)
                self.console.print()
            
            if not subdirs and not exe_files:
                self.console.print("[yellow]空目录[/yellow]\n" if is_chinese() else "[yellow]Empty directory[/yellow]\n")
            
            # Prompt for action
            if is_chinese():
                self.console.print("[cyan]操作:[/cyan]")
                self.console.print("  输入 D# 进入文件夹")
                self.console.print("  输入 E# 选择可执行文件")
                self.console.print("  输入 .. 返回上级目录")
                self.console.print("  输入 0 取消\n")
            else:
                self.console.print("[cyan]Actions:[/cyan]")
                self.console.print("  Enter D# to enter folder")
                self.console.print("  Enter E# to select executable")
                self.console.print("  Enter .. to go up")
                self.console.print("  Enter 0 to cancel\n")
            
            user_input = Prompt.ask("选择" if is_chinese() else "Select")
            
            if user_input == '0':
                return
            elif user_input == '..':
                # Go up one directory
                parent = os.path.dirname(current_path)
                if parent and parent != current_path:
                    current_path = parent
                else:
                    if is_chinese():
                        self.console.print("[yellow]已经在根目录[/yellow]")
                    else:
                        self.console.print("[yellow]Already at root[/yellow]")
                    Prompt.ask("按回车继续" if is_chinese() else "Press Enter to continue", default="")
            elif user_input.upper().startswith('D'):
                # Enter directory
                try:
                    idx = int(user_input[1:])
                    if 1 <= idx <= len(subdirs):
                        current_path = os.path.join(current_path, subdirs[idx - 1])
                    else:
                        self.console.print("[red]无效选择[/red]" if is_chinese() else "[red]Invalid selection[/red]")
                        Prompt.ask("按回车继续" if is_chinese() else "Press Enter to continue", default="")
                except:
                    self.console.print("[red]无效输入[/red]" if is_chinese() else "[red]Invalid input[/red]")
                    Prompt.ask("按回车继续" if is_chinese() else "Press Enter to continue", default="")
            elif user_input.upper().startswith('E'):
                # Select exe file
                try:
                    idx = int(user_input[1:])
                    if 1 <= idx <= len(exe_files):
                        selected_exe = exe_files[idx - 1]
                        exe_path = os.path.join(current_path, selected_exe)
                        
                        # Add game
                        self._add_game_to_steam(exe_path, target_lang)
                        return
                    else:
                        self.console.print("[red]无效选择[/red]" if is_chinese() else "[red]Invalid selection[/red]")
                        Prompt.ask("按回车继续" if is_chinese() else "Press Enter to continue", default="")
                except:
                    self.console.print("[red]无效输入[/red]" if is_chinese() else "[red]Invalid input[/red]")
                    Prompt.ask("按回车继续" if is_chinese() else "Press Enter to continue", default="")
            else:
                self.console.print("[red]无效输入[/red]" if is_chinese() else "[red]Invalid input[/red]")
                Prompt.ask("按回车继续" if is_chinese() else "Press Enter to continue", default="")
    
    def _add_game_to_steam(self, exe_path: str, target_lang: str):
        """Add selected game to Steam"""
        self.clear_screen()
        self.print_header()
        
        # Get default game name from exe filename
        default_name = os.path.splitext(os.path.basename(exe_path))[0]
        
        if is_chinese():
            self.console.print(f"\n[cyan]添加游戏到Steam[/cyan]\n")
            self.console.print(f"可执行文件: [yellow]{exe_path}[/yellow]\n")
            game_name = Prompt.ask("输入游戏名称", default=default_name)
        else:
            self.console.print(f"\n[cyan]Add Game to Steam[/cyan]\n")
            self.console.print(f"Executable: [yellow]{exe_path}[/yellow]\n")
            game_name = Prompt.ask("Enter game name", default=default_name)
        
        # Generate launch options with target language
        launch_options = get_locale_command(target_lang)
        
        if is_chinese():
            self.console.print(f"\n启动选项: [cyan]{launch_options}[/cyan]\n")
            
            if not Confirm.ask("[yellow]确认添加到Steam?[/yellow]"):
                self.console.print("[yellow]已取消[/yellow]")
                Prompt.ask("按回车返回", default="")
                return
        else:
            self.console.print(f"\nLaunch options: [cyan]{launch_options}[/cyan]\n")
            
            if not Confirm.ask("[yellow]Confirm add to Steam?[/yellow]"):
                self.console.print("[yellow]Cancelled[/yellow]")
                Prompt.ask("Press Enter to return", default="")
                return
        
        # Add to Steam
        success, msg = SteamManager.add_non_steam_game(
            exe_path=exe_path,
            app_name=game_name,
            launch_options=launch_options
        )
        
        if success:
            self.console.print(f"[green]✓ {msg}[/green]")
        else:
            self.console.print(f"[red]X {msg}[/red]")
        
        Prompt.ask("按回车返回" if is_chinese() else "Press Enter to return", default="")
    
    def _run_task_with_progress(self, task_name: str, task_func, *args):
        """Run task and display progress"""
        self.clear_screen()
        self.print_header()
        
        self.console.print(f"\n[cyan]{task_name}...[/cyan]\n")
        
        # Create an output buffer to capture print output
        output_lines = []
        
        def task_wrapper():
            """Wrap task function to capture output"""
            import io
            old_stdout = sys.stdout
            
            try:
                # Create StringIO object to capture output
                capture = io.StringIO()
                sys.stdout = capture
                
                # Execute task
                if args:
                    success, msg = task_func(*args)
                else:
                    success, msg = task_func()
                
                # Get captured output
                output = capture.getvalue()
                if output:
                    output_lines.extend(output.strip().split('\n'))
                
                output_lines.append(msg)
                
                return success, msg
            
            finally:
                sys.stdout = old_stdout
        
        # Run task in thread
        result_container = []
        
        def run_in_thread():
            result = task_wrapper()
            result_container.append(result)
        
        thread = threading.Thread(target=run_in_thread, daemon=True)
        thread.start()
        thread.join(timeout=300)  # Wait up to 5 minutes
        
        # Display output
        for line in output_lines:
            if line:
                # Add styles based on content
                if 'OK' in line or '[OK]' in line or '✓' in line:
                    self.console.print(f"[green]{line}[/green]")
                elif 'ERROR' in line or 'X' in line or '[X]' in line or '❌' in line or '✗' in line:
                    self.console.print(f"[red]{line}[/red]")
                elif '[WARN]' in line or '⚠️' in line or '[!]' in line:
                    self.console.print(f"[yellow]{line}[/yellow]")
                elif '>>' in line or '👉' in line:
                    self.console.print(f"[cyan]{line}[/cyan]")
                else:
                    self.console.print(line)
        
        if result_container:
            success, msg = result_container[0]
            if success:
                finish = "[green bold]SUCCESS[/green bold]" if is_chinese() else "[green bold]OK[/green bold]"
                self.console.print(f"\n{finish}")
            else:
                fail = "[red bold]X Failed[/red bold]" if is_chinese() else "[red bold]X Failed[/red bold]"
                self.console.print(f"\n{fail}")
        else:
            timeout = "[yellow bold]Timeout[/yellow bold]" if is_chinese() else "[yellow bold]Timeout[/yellow bold]"
            self.console.print(f"\n{timeout}")
        
        self.console.print()
    
    def run(self):
        """Run application"""
        # Show language selection at startup
        self.show_language_selection()
        
        while self.running:
            choice = self.show_main_menu()
            
            if choice == "1":
                self.show_locale_menu()
            elif choice == "2":
                self.show_font_menu()
            elif choice == "3":
                self.show_game_launcher_menu()
            elif choice == "4":
                self.show_add_game_menu()
            elif choice == "5":
                self.show_system_status()
            elif choice == "6":
                # Change target language
                self.show_language_selection()
            elif choice == "7":
                if is_chinese():
                    self.console.print("\n[cyan]Thank you and goodbye![/cyan]\n")
                else:
                    self.console.print("\n[cyan]Thank you and goodbye![/cyan]\n")
                self.running = False
    
    def show_game_launcher_menu(self):
        """Show game launch options menu"""
        self.clear_screen()
        self.print_header()
        
        target_lang = self.target_language or Config.get_target_language()
        target_lang_name = TargetLanguage.get_name(target_lang, 'zh' if is_chinese() else 'en')
        
        if is_chinese():
            self.console.print(f"\n[bold cyan]功能 3: {target_lang_name}游戏启动选项[/bold cyan]\n")
            
            self.console.print(f"[cyan]配置游戏启动环境变量以使用{target_lang_name}环境。[/cyan]\n")
            
            self.console.print("[yellow]启动命令:[/yellow]")
            self.console.print(get_locale_command(target_lang) + '\n')
            
            self.console.print("[cyan]使用步骤:[/cyan]")
            self.console.print("1. 在 Steam 中打开游戏属性")
            self.console.print("2. 找到'启动选项'字段")
            self.console.print("3. 粘贴上面的命令")
            self.console.print("4. 保存并启动游戏\n")
            
            Prompt.ask("按回车返回", default="")
        else:
            self.console.print(f"\n[bold cyan]Function 3: {target_lang_name} Game Launch Options[/bold cyan]\n")
            
            self.console.print(f"[cyan]Configure game launch environment variables for {target_lang_name}.[/cyan]\n")
            
            self.console.print("[yellow]Launch Command:[/yellow]")

            self.console.print(get_locale_command(target_lang) + '\n')
            
            self.console.print("[cyan]Steps:[/cyan]")
            self.console.print("1. Open game properties in Steam")
            self.console.print("2. Find 'Launch Options' field")
            self.console.print("3. Paste the command above")
            self.console.print("4. Save and launch the game\n")
            
            Prompt.ask("Press Enter to return", default="")


def main():
    """Main function"""
    app = TUIApplication()
    try:
        app.run()
    except KeyboardInterrupt:
        app.console.print("\n\n[yellow]Interrupted[/yellow]\n" if is_chinese() else "\n\n[yellow]Interrupted[/yellow]\n")
        sys.exit(0)
    except Exception as e:
        error = f"\n\n[red]X Error: {str(e)}[/red]\n" if is_chinese() else f"\n\n[red]X Error: {str(e)}[/red]\n"
        app.console.print(error)
        sys.exit(1)


if __name__ == '__main__':
    main()
