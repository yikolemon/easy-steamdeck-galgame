#!/usr/bin/env python3
"""
Syntax verification - just check if files can parse
"""
import ast
import sys

files = ['utils.py', 'locale_installer.py', 'font_installer.py', 'game_launcher.py', 'main.py']
all_ok = True

print("=" * 60)
print("🧪 Python Syntax Verification")
print("=" * 60)

for filename in files:
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            code = f.read()
            ast.parse(code)
        print(f"✅ {filename:30} - OK")
    except SyntaxError as e:
        print(f"❌ {filename:30} - SYNTAX ERROR: {e}")
        all_ok = False
    except Exception as e:
        print(f"⚠️  {filename:30} - ERROR: {e}")

print("=" * 60)
if all_ok:
    print("✅ All files have valid Python syntax!")
    sys.exit(0)
else:
    print("❌ Some files have syntax errors")
    sys.exit(1)
