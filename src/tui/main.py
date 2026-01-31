"""
TUI Main Program - Interactive terminal interface using Rich library
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
from src.core.game_launcher import (
    get_zh_locale_command
)


class TUIApplication:
    """TUI Application"""
    
    def __init__(self):
        self.console = Console()
        self.running = True
    
    def clear_screen(self):
        """Clear screen"""
        os.system('clear' if os.name != 'nt' else 'cls')
    
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
        
        table = Table(show_header=False, show_footer=False, box=None)
        table.add_column(style="cyan")
        
        if is_chinese():
            table.add_row("[1] Install Chinese Locale")
            table.add_row("[2] Install Chinese Fonts")
            table.add_row("[3] Game Launch Options")
            table.add_row("[4] System Status")
            table.add_row("[5] Exit")
        else:
            table.add_row("[1] Install Chinese Locale")
            table.add_row("[2] Install Chinese Fonts")
            table.add_row("[3] Game Launch Options")
            table.add_row("[4] System Status")
            table.add_row("[5] Exit")
        
        self.console.print(table)
        self.console.print()
        
        prompt_text = "Select function"
        choice = Prompt.ask(prompt_text, choices=["1", "2", "3", "4", "5"])
        return choice
    
    def show_locale_menu(self):
        """Show Locale menu"""
        self.clear_screen()
        self.print_header()
        
        if is_chinese():
            self.console.print("\n[bold cyan]Function 1: Install Chinese Locale[/bold cyan]\n")
            
            # Check current status
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
        else:
            self.console.print("\n[bold cyan]Function 1: Install Chinese Locale[/bold cyan]\n")
            
            # Check current status
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
        """Show Font menu"""
        self.clear_screen()
        self.print_header()
        
        if is_chinese():
            self.console.print("\n[bold cyan]Function 2: Install Chinese Fonts[/bold cyan]\n")
            
            # Check current status
            is_installed = check_fonts_status()
            count = get_fonts_count()
            status_text = f"[green]OK ({count})[/green]" if is_installed else "[red]X[/red]"
            
            self.console.print(f"Status: {status_text}\n")
            
            self.console.print("[cyan]Select installation method:[/cyan]")
            self.console.print("[1] Download from GitHub")
            self.console.print("[2] Use local font package")
            self.console.print("[3] Return to menu\n")
        else:
            self.console.print("\n[bold cyan]Function 2: Install Chinese Fonts[/bold cyan]\n")
            
            # Check current status
            is_installed = check_fonts_status()
            count = get_fonts_count()
            status_text = f"[green]OK ({count})[/green]" if is_installed else "[red]X[/red]"
            
            self.console.print(f"Status: {status_text}\n")
            
            self.console.print("[cyan]Select installation method:[/cyan]")
            self.console.print("[1] Download from GitHub")
            self.console.print("[2] Use local font package")
            self.console.print("[3] Return to menu\n")
        
        choice = Prompt.ask("Select" if is_chinese() else "Select", choices=["1", "2", "3"])
        
        if choice == "1":
            self._install_fonts_from_github()
        elif choice == "2":
            self._install_fonts_from_local()
    
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
    
    def show_system_status(self):
        """Show system status"""
        self.clear_screen()
        self.print_header()
        
        if is_chinese():
            self.console.print("\n[bold cyan]System Status[/bold cyan]\n")
            
            table = Table(show_header=True)
            table.add_column("Function", style="cyan")
            table.add_column("Status")
            
            # Locale status
            locale_installed = check_locale_status()
            locale_status = "[green]OK[/green]" if locale_installed else "[red]X[/red]"
            table.add_row("Chinese Locale", locale_status)
            
            # Font status
            fonts_installed = check_fonts_status()
            fonts_count = get_fonts_count()
            fonts_status = f"[green]OK ({fonts_count})[/green]" if fonts_installed else "[red]X[/red]"
            table.add_row("Chinese Fonts", fonts_status)
            
            self.console.print(table)
            self.console.print()
            
            Prompt.ask("Press Enter to return", default="")
        else:
            self.console.print("\n[bold cyan]System Status[/bold cyan]\n")
            
            table = Table(show_header=True)
            table.add_column("Function", style="cyan")
            table.add_column("Status")
            
            # Check locale status
            locale_installed = check_locale_status()
            locale_status = "[green]OK[/green]" if locale_installed else "[red]X[/red]"
            table.add_row("Chinese Locale", locale_status)
            
            # Check font status
            fonts_installed = check_fonts_status()
            fonts_count = get_fonts_count()
            fonts_status = f"[green]OK ({fonts_count})[/green]" if fonts_installed else "[red]X[/red]"
            table.add_row("Chinese Fonts", fonts_status)
            
            self.console.print(table)
            self.console.print()
            
            Prompt.ask("Press Enter to return", default="")
    
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
                    self.console.print("\n[cyan]Thank you and goodbye![/cyan]\n")
                else:
                    self.console.print("\n[cyan]Thank you and goodbye![/cyan]\n")
                self.running = False
    
    def show_game_launcher_menu(self):
        """Show game launch options menu"""
        self.clear_screen()
        self.print_header()
        
        if is_chinese():
            self.console.print("\n[bold cyan]Function 3: Game Launch Options[/bold cyan]\n")
            
            self.console.print("[cyan]Configure game launch environment variables.[/cyan]\n")
            
            self.console.print("[yellow]Launch Command:[/yellow]")
            self.console.print(get_zh_locale_command() + '\n')
            
            self.console.print("[cyan]Steps:[/cyan]")
            self.console.print("1. Open game properties in Steam")
            self.console.print("2. Find 'Launch Options' field")
            self.console.print("3. Paste the command above")
            self.console.print("4. Save and launch the game\n")
            
            Prompt.ask("Press Enter to return", default="")
        else:
            self.console.print("\n[bold cyan]Function 3: Game Launch Options[/bold cyan]\n")
            
            self.console.print("[cyan]Configure game launch environment variables.[/cyan]\n")
            
            self.console.print("[yellow]Launch Command:[/yellow]")

            self.console.print(get_zh_locale_command() + '\n')
            
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
