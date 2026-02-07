#!/usr/bin/env python3
"""
Import test script
"""

import sys

print("Python version:", sys.version)
print("Python path:", sys.path[:3])

try:
    print("Importing tkinter...", end=" ")
    import tkinter

    print("OK")
except ImportError as e:
    print("FAILED:", e)
    sys.exit(1)

try:
    print("Importing src.gui.main...", end=" ")
    from src.gui.main import GUIApplication

    print("OK")
    print("GUIApplication loaded successfully")
except ImportError as e:
    print("FAILED:", e)
    import traceback

    traceback.print_exc()
    sys.exit(1)

print("\nAll imports successful!")
