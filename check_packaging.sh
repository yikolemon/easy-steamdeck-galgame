#!/bin/bash

# 打包完整性检查脚本

echo "════════════════════════════════════════════════════════════════"
echo "  Linux 打包检查清单"
echo "════════════════════════════════════════════════════════════════"
echo ""

CHECK_PASSED=0
CHECK_FAILED=0

check_file() {
    local file=$1
    local desc=$2
    
    if [ -f "$file" ]; then
        echo "✓ $file ($desc)"
        ((CHECK_PASSED++))
    else
        echo "✗ $file ($desc) - 缺失"
        ((CHECK_FAILED++))
    fi
}

check_executable() {
    local file=$1
    local desc=$2
    
    if [ -x "$file" ]; then
        echo "✓ $file ($desc) - 可执行"
        ((CHECK_PASSED++))
    else
        echo "✗ $file ($desc) - 不可执行或缺失"
        ((CHECK_FAILED++))
    fi
}

echo "📋 必要文件检查:"
echo ""

# 检查源代码文件
check_file "run.py" "主程序"
check_file "requirements.txt" "Python 依赖"
check_file "src/tui/main.py" "TUI 模块"
check_file "src/ui/main.py" "GUI 模块"
check_file "data/icons/io.github.steamdeck_galgame.svg" "应用图标"

echo ""
echo "🛠️  打包工具检查:"
echo ""

# 检查打包脚本
check_executable "build_linux_package.sh" "主打包脚本"
check_executable "build_appimage.sh" "AppImage 构建脚本"
check_executable "start_tui.sh" "TUI 启动脚本"

echo ""
echo "📝 配置文件检查:"
echo ""

# 检查配置文件
check_file "io.github.steamdeck_galgame.desktop" ".desktop 菜单文件"
check_file "AppImageBuilder.yml" "AppImage 配置"

echo ""
echo "📚 文档检查:"
echo ""

# 检查文档
check_file "README.md" "项目说明"
check_file "LINUX_PACKAGING.md" "打包指南"
check_file "TUI_USAGE.md" "TUI 使用指南"
check_file "TUI_IMPLEMENTATION.md" "TUI 实现说明"
check_file "PROJECT_STATUS.md" "项目状态"

echo ""
echo "════════════════════════════════════════════════════════════════"
echo "  检查结果"
echo "════════════════════════════════════════════════════════════════"
echo ""
echo "✓ 通过: $CHECK_PASSED"
echo "✗ 失败: $CHECK_FAILED"
echo ""

if [ $CHECK_FAILED -eq 0 ]; then
    echo "🎉 所有文件都已就绪！"
    echo ""
    echo "🚀 现在可以运行打包脚本："
    echo ""
    echo "   bash build_linux_package.sh"
    echo ""
    exit 0
else
    echo "⚠️  有些文件缺失，请检查。"
    exit 1
fi
