"""
TUI 主程序 - 使用 Rich 库实现交互式终端界面
"""

import os
import sys
from typing import Optional, Tuple
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.prompt import Prompt, Confirm
from rich.progress import track
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


class TUIApplication:
    """TUI应用程序"""
    
    def __init__(self):
        self.console = Console()
        self.running = True
    
    def clear_screen(self):
        """清空屏幕"""
        os.system('clear' if os.name != 'nt' else 'cls')
    
    def print_header(self):
        """打印应用头部"""
        header = Text()
        title = t('title', "SteamDeck 中文环境配置工具", "SteamDeck Chinese Environment Config Tool")
        header.append(title, style="bold cyan")
        
        panel = Panel(
            header,
            title=t('app_name', "[bold]SteamDeck 中文配置[/bold]", "[bold]SteamDeck Config[/bold]"),
            style="bold blue",
            expand=True
        )
        self.console.print(panel)
    
    def show_main_menu(self) -> str:
        """显示主菜单，返回用户选择"""
        self.clear_screen()
        self.print_header()
        
        table = Table(show_header=False, show_footer=False, box=None)
        table.add_column(style="cyan")
        
        if is_chinese():
            table.add_row("[1] 中文 Locale 安装")
            table.add_row("[2] 中文字体安装")
            table.add_row("[3] 游戏启动选项配置")
            table.add_row("[4] 查看系统状态")
            table.add_row("[5] 退出程序")
        else:
            table.add_row("[1] Install Chinese Locale")
            table.add_row("[2] Install Chinese Fonts")
            table.add_row("[3] Game Launch Options")
            table.add_row("[4] System Status")
            table.add_row("[5] Exit")
        
        self.console.print(table)
        self.console.print()
        
        prompt_text = t('select_function', "请选择功能", "Select function")
        choice = Prompt.ask(prompt_text, choices=["1", "2", "3", "4", "5"])
        return choice
    
    def show_locale_menu(self):
        """显示 Locale 菜单"""
        self.clear_screen()
        self.print_header()
        
        if is_chinese():
            self.console.print("\n[bold cyan]功能 1: 中文 Locale 安装[/bold cyan]\n")
            
            # 检查当前状态
            is_installed = check_locale_status()
            status_text = "[green]✓ 已安装[/green]" if is_installed else "[red]✗ 未安装[/red]"
            
            self.console.print(f"当前状态: {status_text}\n")
            
            if is_installed:
                self.console.print("[yellow]⚠️  Locale 已安装，无需重复安装。[/yellow]\n")
                Prompt.ask("按 Enter 返回主菜单", default="")
                return
            
            self.console.print("[cyan]此功能将：[/cyan]")
            self.console.print("  1. 关闭 SteamOS 只读模式")
            self.console.print("  2. 初始化 pacman 密钥")
            self.console.print("  3. 启用简体中文 locale (zh_CN.UTF-8)")
            self.console.print("  4. 生成 locale")
            self.console.print("  5. 恢复 SteamOS 只读模式\n")
            
            if not Confirm.ask("[yellow]需要获取 root 权限，是否继续？[/yellow]"):
                self.console.print("[yellow]已取消操作[/yellow]")
                Prompt.ask("按 Enter 返回主菜单", default="")
                return
            
            self._run_task_with_progress("安装中文 Locale", setup_locale)
            
            Prompt.ask("按 Enter 返回主菜单", default="")
        else:
            self.console.print("\n[bold cyan]Function 1: Install Chinese Locale[/bold cyan]\n")
            
            # 检查当前状态
            is_installed = check_locale_status()
            status_text = "[green]OK[/green]" if is_installed else "[red]X[/red]"
            
            self.console.print(f"Status: {status_text}\n")
            
            if is_installed:
                self.console.print("[yellow]Locale already installed.[/yellow]\n")
                Prompt.ask("Press Enter to return", default="")
                return
            
            self.console.print("[cyan]This will:[/cyan]")
            self.console.print("  1. Disable SteamOS read-only mode")
            self.console.print("  2. Initialize pacman keys")
            self.console.print("  3. Enable Simplified Chinese locale (zh_CN.UTF-8)")
            self.console.print("  4. Generate locale")
            self.console.print("  5. Restore SteamOS read-only mode\n")
            
            if not Confirm.ask("[yellow]Requires root permission, continue?[/yellow]"):
                self.console.print("[yellow]Cancelled[/yellow]")
                Prompt.ask("Press Enter to return", default="")
                return
            
            self._run_task_with_progress("Installing Chinese Locale", setup_locale)
            
            Prompt.ask("Press Enter to return", default="")
    
    def show_font_menu(self):
        """显示字体菜单"""
        self.clear_screen()
        self.print_header()
        
        if is_chinese():
            self.console.print("\n[bold cyan]功能 2: 中文字体安装[/bold cyan]\n")
            
            # 检查当前状态
            is_installed = check_fonts_status()
            count = get_fonts_count()
            status_text = f"[green]✓ 已安装 ({count} 个字体)[/green]" if is_installed else "[red]✗ 未安装[/red]"
            
            self.console.print(f"当前状态: {status_text}\n")
            
            self.console.print("[cyan]选择安装方式：[/cyan]")
            self.console.print("[1] 从 GitHub 下载并安装")
            self.console.print("[2] 使用本地字体包文件")
            self.console.print("[3] 返回主菜单\n")
        else:
            self.console.print("\n[bold cyan]Function 2: Install Chinese Fonts[/bold cyan]\n")
            
            # 检查当前状态
            is_installed = check_fonts_status()
            count = get_fonts_count()
            status_text = f"[green]OK ({count})[/green]" if is_installed else "[red]X[/red]"
            
            self.console.print(f"Status: {status_text}\n")
            
            self.console.print("[cyan]Select installation method:[/cyan]")
            self.console.print("[1] Download from GitHub")
            self.console.print("[2] Use local font package")
            self.console.print("[3] Return to menu\n")
        
        choice = Prompt.ask("请选择" if is_chinese() else "Select", choices=["1", "2", "3"])
        
        if choice == "1":
            self._install_fonts_from_github()
        elif choice == "2":
            self._install_fonts_from_local()
    
    def _install_fonts_from_github(self):
        """从 GitHub 下载并安装字体"""
        self.clear_screen()
        self.print_header()
        
        if is_chinese():
            self.console.print("\n[cyan]获取可用的字体包...[/cyan]\n")
        else:
            self.console.print("\n[cyan]Fetching available font packages...[/cyan]\n")
        
        try:
            success, assets = list_available_fonts()
            if not success or not assets:
                error_msg = "[red]❌ 无法获取字体列表[/red]" if is_chinese() else "[red]X Cannot get font list[/red]"
                self.console.print(error_msg + "\n")
                Prompt.ask("按 Enter 返回" if is_chinese() else "Press Enter", default="")
                return
            
            # 显示可用的字体包
            title = "可用的字体包" if is_chinese() else "Available Fonts"
            table = Table(title=title, show_header=True)
            table.add_column("序号" if is_chinese() else "No.", style="cyan")
            table.add_column("名称" if is_chinese() else "Name")
            table.add_column("大小" if is_chinese() else "Size")
            
            for idx, asset in enumerate(assets, 1):
                size_mb = asset.size / (1024 * 1024)
                table.add_row(str(idx), asset.name, f"{size_mb:.2f} MB")
            
            self.console.print(table)
            self.console.print()
            
            prompt = "请选择要下载的字体包" if is_chinese() else "Select font package"
            choice = Prompt.ask(prompt, choices=[str(i) for i in range(1, len(assets) + 1)])
            selected_asset = assets[int(choice) - 1]
            
            confirm_msg = f"\n[yellow]确认下载并安装 {selected_asset.name}？[/yellow]" if is_chinese() else f"\n[yellow]Confirm download and install {selected_asset.name}?[/yellow]"
            if not Confirm.ask(confirm_msg):
                self.console.print("[yellow]已取消[/yellow]" if is_chinese() else "[yellow]Cancelled[/yellow]")
                Prompt.ask("按 Enter 返回" if is_chinese() else "Press Enter", default="")
                return
            
            task_name = f"下载并安装 {selected_asset.name}"
            self._run_task_with_progress(
                task_name,
                download_and_install_fonts,
                selected_asset
            )
        
        except Exception as e:
            error = f"[red]❌ 异常: {str(e)}[/red]" if is_chinese() else f"[red]X Error: {str(e)}[/red]"
            self.console.print(error + "\n")
        
        Prompt.ask("按 Enter 返回" if is_chinese() else "Press Enter", default="")
    
    def _install_fonts_from_local(self):
        """从本地文件安装字体"""
        self.clear_screen()
        self.print_header()
        
        if is_chinese():
            self.console.print("\n[cyan]请输入本地字体包的完整路径：[/cyan]\n")
            zip_path = Prompt.ask("字体包路径")
        else:
            self.console.print("\n[cyan]Enter full path to local font package:[/cyan]\n")
            zip_path = Prompt.ask("Font package path")
        
        if not os.path.isfile(zip_path):
            error = f"[red]❌ 文件不存在: {zip_path}[/red]" if is_chinese() else f"[red]X File not found: {zip_path}[/red]"
            self.console.print(error + "\n")
            Prompt.ask("按 Enter 返回" if is_chinese() else "Press Enter", default="")
            return
        
        confirm_msg = f"\n[yellow]确认使用 {os.path.basename(zip_path)}？[/yellow]" if is_chinese() else f"\n[yellow]Confirm use {os.path.basename(zip_path)}?[/yellow]"
        if not Confirm.ask(confirm_msg):
            self.console.print("[yellow]已取消[/yellow]" if is_chinese() else "[yellow]Cancelled[/yellow]")
            Prompt.ask("按 Enter 返回" if is_chinese() else "Press Enter", default="")
            return
        
        task_name = f"安装字体: {os.path.basename(zip_path)}" if is_chinese() else f"Install font: {os.path.basename(zip_path)}"
        self._run_task_with_progress(
            task_name,
            setup_fonts,
            zip_path
        )
        
        Prompt.ask("按 Enter 返回" if is_chinese() else "Press Enter", default="")
    
    def show_system_status(self):
        """显示系统状态"""
        self.clear_screen()
        self.print_header()
        
        if is_chinese():
            self.console.print("\n[bold cyan]系统状态[/bold cyan]\n")
            
            table = Table(show_header=True)
            table.add_column("功能", style="cyan")
            table.add_column("状态")
            
            # Locale 状态
            locale_installed = check_locale_status()
            locale_status = "[green]✓ 已安装[/green]" if locale_installed else "[red]✗ 未安装[/red]"
            table.add_row("中文 Locale", locale_status)
            
            # 字体状态
            fonts_installed = check_fonts_status()
            fonts_count = get_fonts_count()
            fonts_status = f"[green]✓ 已安装 ({fonts_count} 个)[/green]" if fonts_installed else "[red]✗ 未安装[/red]"
            table.add_row("中文字体", fonts_status)
            
            self.console.print(table)
            self.console.print()
            
            Prompt.ask("按 Enter 返回主菜单", default="")
        else:
            self.console.print("\n[bold cyan]System Status[/bold cyan]\n")
            
            table = Table(show_header=True)
            table.add_column("Function", style="cyan")
            table.add_column("Status")
            
            # Locale 状态
            locale_installed = check_locale_status()
            locale_status = "[green]OK[/green]" if locale_installed else "[red]X[/red]"
            table.add_row("Chinese Locale", locale_status)
            
            # 字体状态
            fonts_installed = check_fonts_status()
            fonts_count = get_fonts_count()
            fonts_status = f"[green]OK ({fonts_count})[/green]" if fonts_installed else "[red]X[/red]"
            table.add_row("Chinese Fonts", fonts_status)
            
            self.console.print(table)
            self.console.print()
            
            Prompt.ask("Press Enter to return", default="")
    
    def _run_task_with_progress(self, task_name: str, task_func, *args):
        """运行任务并显示进度"""
        self.clear_screen()
        self.print_header()
        
        self.console.print(f"\n[cyan]{task_name}...[/cyan]\n")
        
        # 创建一个输出缓冲区来捕获打印输出
        output_lines = []
        
        def task_wrapper():
            """包装任务函数以捕获输出"""
            import io
            old_stdout = sys.stdout
            
            try:
                # 创建一个StringIO对象来捕获输出
                capture = io.StringIO()
                sys.stdout = capture
                
                # 执行任务
                if args:
                    success, msg = task_func(*args)
                else:
                    success, msg = task_func()
                
                # 获取捕获的输出
                output = capture.getvalue()
                if output:
                    output_lines.extend(output.strip().split('\n'))
                
                output_lines.append(msg)
                
                return success, msg
            
            finally:
                sys.stdout = old_stdout
        
        # 在线程中运行任务
        result_container = []
        
        def run_in_thread():
            result = task_wrapper()
            result_container.append(result)
        
        thread = threading.Thread(target=run_in_thread, daemon=True)
        thread.start()
        thread.join(timeout=300)  # 最多等待5分钟
        
        # 显示输出
        for line in output_lines:
            if line:
                # 根据内容添加相应的样式
                if '✓' in line or '✅' in line or '[OK]' in line:
                    self.console.print(f"[green]{line}[/green]")
                elif '❌' in line or '✗' in line or '[X]' in line:
                    self.console.print(f"[red]{line}[/red]")
                elif '⚠️' in line or '[!]' in line:
                    self.console.print(f"[yellow]{line}[/yellow]")
                elif '👉' in line or '>>' in line:
                    self.console.print(f"[cyan]{line}[/cyan]")
                else:
                    self.console.print(line)
        
        if result_container:
            success, msg = result_container[0]
            if success:
                finish = "[green bold]✓ 操作完成！[/green bold]" if is_chinese() else "[green bold]OK[/green bold]"
                self.console.print(f"\n{finish}")
            else:
                fail = "[red bold]✗ 操作失败[/red bold]" if is_chinese() else "[red bold]X Failed[/red bold]"
                self.console.print(f"\n{fail}")
        else:
            timeout = "[yellow bold]⚠️  任务执行超时或中断[/yellow bold]" if is_chinese() else "[yellow bold]Timeout[/yellow bold]"
            self.console.print(f"\n{timeout}")
        
        self.console.print()
    
    def run(self):
        """运行应用程序"""
        while self.running:
            choice = self.show_main_menu()
            
            if choice == "1":
                self.show_locale_menu()
            elif choice == "2":
                self.show_font_menu()
            elif choice == "3":
                self.show_game_launcher_menu()
            elif choice == "4":
                self.show_system_status()
            elif choice == "5":
                if is_chinese():
                    self.console.print("\n[cyan]谢谢使用！再见 👋[/cyan]\n")
                else:
                    self.console.print("\n[cyan]Thank you and goodbye![/cyan]\n")
                self.running = False
    
    def show_game_launcher_menu(self):
        """显示游戏启动选项菜单"""
        self.clear_screen()
        self.print_header()
        
        if is_chinese():
            self.console.print("\n[bold cyan]功能 3: 游戏启动选项配置[/bold cyan]\n")
            
            self.console.print("[cyan]此功能用于配置游戏的启动环境变量。[/cyan]\n")
            
            self.console.print("[yellow]启动命令：[/yellow]")
            self.console.print('LANG=zh_CN.UTF-8 LANGUAGE=zh_CN %command%\n')
            
            self.console.print("[cyan]使用步骤：[/cyan]")
            self.console.print("1. 在 Steam 中打开游戏属性")
            self.console.print("2. 找到「启动选项」字段")
            self.console.print("3. 复制上面的启动命令粘贴进去")
            self.console.print("4. 保存并启动游戏\n")
            
            Prompt.ask("按 Enter 返回主菜单", default="")
        else:
            self.console.print("\n[bold cyan]Function 3: Game Launch Options[/bold cyan]\n")
            
            self.console.print("[cyan]Configure game launch environment variables.[/cyan]\n")
            
            self.console.print("[yellow]Launch Command:[/yellow]")
            self.console.print('LANG=zh_CN.UTF-8 LANGUAGE=zh_CN %command%\n')
            
            self.console.print("[cyan]Steps:[/cyan]")
            self.console.print("1. Open game properties in Steam")
            self.console.print("2. Find 'Launch Options' field")
            self.console.print("3. Paste the command above")
            self.console.print("4. Save and launch the game\n")
            
            Prompt.ask("Press Enter to return", default="")


def main():
    """主函数"""
    app = TUIApplication()
    try:
        app.run()
    except KeyboardInterrupt:
        app.console.print("\n\n[yellow]程序已中断[/yellow]\n" if is_chinese() else "\n\n[yellow]Interrupted[/yellow]\n")
        sys.exit(0)
    except Exception as e:
        error = f"\n\n[red]❌ 程序异常: {str(e)}[/red]\n" if is_chinese() else f"\n\n[red]X Error: {str(e)}[/red]\n"
        app.console.print(error)
        sys.exit(1)


if __name__ == '__main__':
    main()
