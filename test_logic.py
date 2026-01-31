#!/usr/bin/env python3
"""
Application Logic Test Suite - No GUI Required
Tests core functionality without display
"""

def test_imports():
    """Test that all modules can be imported"""
    try:
        from utils import run_command, is_zh_locale_enabled, is_fonts_installed
        from locale_installer import setup_locale
        from font_installer import setup_fonts
        from game_launcher import get_zh_locale_preset
        print("✅ All module imports successful")
        return True
    except ImportError as e:
        print(f"❌ Import failed: {e}")
        return False

def test_game_launcher():
    """Test game launcher functions"""
    try:
        from game_launcher import get_zh_locale_preset
        preset = get_zh_locale_preset()
        if isinstance(preset, str) and len(preset) > 0:
            print(f"✅ Game launcher preset OK ({len(preset)} chars)")
            return True
        else:
            print("❌ Game launcher preset invalid")
            return False
    except Exception as e:
        print(f"❌ Game launcher test failed: {e}")
        return False

def test_utils():
    """Test utility functions"""
    try:
        from utils import get_home_dir, get_zh_locale_command
        home = get_home_dir()
        cmd = get_zh_locale_command()
        if isinstance(home, str) and isinstance(cmd, str):
            print(f"✅ Utility functions OK")
            return True
        else:
            print("❌ Utility functions failed")
            return False
    except Exception as e:
        print(f"❌ Utils test failed: {e}")
        return False

def main():
    print("=" * 60)
    print("🧪 SteamDeck GalGame Application Test Suite")
    print("=" * 60)
    print()
    
    results = {
        "Imports": test_imports(),
        "Game Launcher": test_game_launcher(),
        "Utils": test_utils(),
    }
    
    print()
    print("=" * 60)
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    if passed == total:
        print(f"✅ ALL TESTS PASSED ({passed}/{total})")
        print("🎉 Application logic verified successfully!")
    else:
        print(f"❌ Some tests failed ({passed}/{total})")
    
    print("=" * 60)
    return all(results.values())

if __name__ == "__main__":
    exit(0 if main() else 1)
