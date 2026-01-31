#!/usr/bin/env python3
import sys
print("Python version:", sys.version)
print("Python path:", sys.path[:3])

try:
    print("Importing rich...", end=" ")
    import rich
    print("OK")
except ImportError as e:
    print("FAILED:", e)
    sys.exit(1)

try:
    print("Importing src.tui.main...", end=" ")
    from src.tui.main import TUIApplication
    print("OK")
    print("TUIApplication loaded successfully")
except ImportError as e:
    print("FAILED:", e)
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\nAll imports successful!")
