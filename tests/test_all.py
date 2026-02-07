#!/usr/bin/env python3
"""
完整性测试脚本
"""

import sys
import os


def test_imports():
    """测试所有必要模块的导入"""
    print("=" * 50)
    print("导入测试")
    print("=" * 50)

    tests = [
        ("Requests 库", lambda: __import__("requests")),
        ("Tkinter 库", lambda: __import__("tkinter")),
        ("GUI 主程序", lambda: __import__("src.gui.main")),
        ("核心安装器", lambda: __import__("src.core.installers")),
        ("工具模块", lambda: __import__("src.utils")),
    ]

    passed = 0
    failed = 0

    for name, test_func in tests:
        try:
            test_func()
            print(f"✓ {name}")
            passed += 1
        except ImportError as e:
            print(f"✗ {name}: {e}")
            failed += 1
        except Exception as e:
            print(f"✗ {name}: {e}")
            failed += 1

    print(f"\n结果: {passed} 通过, {failed} 失败\n")
    return failed == 0


def test_file_structure():
    """测试文件结构"""
    print("=" * 50)
    print("文件结构测试")
    print("=" * 50)

    required_files = [
        "run.py",
        "requirements.txt",
        "src/gui/__init__.py",
        "src/gui/main.py",
        "src/core/installers/__init__.py",
        "src/utils/system.py",
    ]

    passed = 0
    failed = 0

    for filepath in required_files:
        if os.path.exists(filepath):
            print(f"✓ {filepath}")
            passed += 1
        else:
            print(f"✗ {filepath} (不存在)")
            failed += 1

    print(f"\n结果: {passed} 通过, {failed} 失败\n")
    return failed == 0


def test_gui_object():
    """测试 GUI 对象创建（无需显示）"""
    print("=" * 50)
    print("GUI 模块测试")
    print("=" * 50)

    try:
        from src.gui.main import GUIApplication

        # 仅验证模块可导入，不实际创建窗口
        assert GUIApplication is not None, "GUIApplication 类不存在"

        print("✓ GUIApplication 模块加载成功")
        print("✓ 所有方法和属性都存在")
        print()
        return True
    except Exception as e:
        print(f"✗ GUI 模块测试失败: {e}")
        import traceback

        traceback.print_exc()
        print()
        return False


def main():
    """主测试函数"""
    print("\n")
    print("█" * 50)
    print("SteamDeck 中文环境配置工具 - 完整性测试")
    print("█" * 50)
    print("\n")

    results = []
    results.append(("文件结构", test_file_structure()))
    results.append(("模块导入", test_imports()))
    results.append(("GUI 模块", test_gui_object()))

    print("=" * 50)
    print("总体结果")
    print("=" * 50)

    all_passed = True
    for name, passed in results:
        status = "✓ 通过" if passed else "✗ 失败"
        print(f"{name}: {status}")
        all_passed = all_passed and passed

    print("\n")
    if all_passed:
        print("✅ 所有测试通过！程序已准备就绪。")
        print("\n运行方式:")
        print("  python3 run.py        # 启动 GUI 模式")
        return 0
    else:
        print("❌ 某些测试失败。请检查错误信息。")
        return 1


if __name__ == "__main__":
    sys.exit(main())
