# AGENTS.md - AI Coding Agent Instructions

This document provides instructions for AI coding agents working on the steamdeck-galgame project.

## Project Overview

SteamDeck Chinese Environment Configuration Tool - A Python GUI application for configuring Chinese/Japanese game environments on SteamDeck. Built with Python 3.7+ and Tkinter for GUI.

## Build & Run Commands

```bash
# Install dependencies
pip install -r requirements.txt

# Run application
python run.py

# Run all tests
pytest

# Run tests with verbose output
pytest -v --tb=short

# Run a single test file
pytest tests/test_logic.py

# Run a specific test function
pytest tests/test_logic.py::test_imports

# Build standalone executable (Linux only)
./build_pyinstaller.sh release    # Release build
./build_pyinstaller.sh debug      # Debug build
./build_pyinstaller.sh all        # Both versions

# Direct PyInstaller build
BUILD_TYPE=release pyinstaller --clean steamdeck_galgame.spec
```

## Linting & Formatting

```bash
# Format code (line length: 100)
black --line-length 100 .

# Sort imports
isort --profile black .

# Type checking
mypy src/
```

## Project Structure

```
steamdeck-galgame/
├── run.py                  # Application entry point
├── src/
│   ├── gui/                # GUI interface (Tkinter)
│   ├── core/               # Core business logic
│   │   ├── installers/     # Installation modules (ABC pattern)
│   │   └── downloader/     # GitHub release downloads
│   ├── utils/              # Utility functions
│   └── config/             # Configuration management
├── tests/                  # Test suite (pytest)
└── doc/                    # Documentation
```

## Code Style Guidelines

### Import Organization
```python
import os                           # 1. Standard library
from typing import Tuple, Optional

import requests                     # 2. Third-party libraries

from src.utils import run_command   # 3. Local imports
from .base import BaseInstaller     # 4. Relative imports last
```

### Naming Conventions
- **Classes**: PascalCase (`FontInstaller`, `GUIApplication`)
- **Functions/Methods**: snake_case (`run_command`, `check_status`)
- **Constants**: UPPER_SNAKE_CASE (`FONTS_DIR`, `ZH_LOCALE_COMMAND`)
- **Private methods**: _leading_underscore (`_detect_language`)

### Type Hints
All functions must include type hints. Use `from typing import` for complex types.
```python
def run_command(cmd: str, use_sudo: bool = False) -> Tuple[bool, str]:
    """Execute shell command"""
    pass
```

### Return Value Pattern
Most operations return `Tuple[bool, str]` with success flag and message:
```python
def some_operation() -> Tuple[bool, str]:
    try:
        return True, "SUCCESS: Operation completed"
    except SpecificException as e:
        return False, f"ERROR: Description: {str(e)}"
    except Exception as e:
        return False, f"ERROR: Exception occurred: {str(e)}"
```

### Error Handling
- Catch specific exceptions before general `Exception`
- Return `Tuple[bool, str]` rather than raising in public APIs
- Use logging for debug info, return messages for user feedback

### Progress Messages
Use `[step/total]` format for multi-step operations:
```python
print("[1/6] Checking if readonly mode needs to be disabled...")
```

Use status prefixes: `[OK]`, `[ERROR]`, `[WARN]`, `[SKIP]`

### Class Pattern (ABC)
```python
class BaseInstaller(ABC):
    @abstractmethod
    def install(self) -> Tuple[bool, str]:
        pass
    
    @abstractmethod
    def check_status(self) -> bool:
        pass
```

Provide module-level convenience functions after class definitions:
```python
def setup_fonts(zip_path: str) -> Tuple[bool, str]:
    """Convenience function to install Chinese fonts"""
    installer = FontInstaller(zip_path)
    return installer.install()
```

### Configuration
Use the `Config` class for all configuration access:
```python
from src.config import Config
fonts_dir = Config.get_fonts_dir()
```

### Bilingual Support
```python
from src.utils.locale import t, is_chinese
text = t('key', '中文文本', 'English text')
```

## GUI Development (Tkinter)
```python
import tkinter as tk
from tkinter import ttk, messagebox, filedialog

class GUIApplication:
    def __init__(self):
        self.root = tk.Tk()
        self._setup_style()
        self._create_ui()
    
    def run(self):
        self.root.mainloop()
```

## Testing Guidelines
```python
def test_function_name():
    """Test description"""
    assert result == expected

def main():
    """Manual test runner for debugging"""
    results = {"Test Name": test_function()}
    return all(results.values())

if __name__ == "__main__":
    exit(0 if main() else 1)
```

## Platform Considerations

- Target platform: SteamDeck (Linux/SteamOS)
- Requires root/sudo for system operations
- Uses `steamos-readonly` command for SteamOS filesystem
- Compatible with Arch Linux
- Python 3.7+ required
- Tkinter (tk) is Python's built-in GUI library

## Key Constants

- Fonts directory: `/usr/share/fonts/galgame`
- Temp directory: `/tmp/galgame_fonts_extract`
- Config file: `~/.steamdeck_galgame_config.json`
- Steam userdata: `~/.steam/root/userdata`
