#!/bin/bash

# SteamDeck PyInstaller 打包脚本
# 在 Linux/SteamDeck 环境上构建独立可执行文件

set -e

echo "════════════════════════════════════════════════════════════════"
echo "  SteamDeck 中文环境配置工具 - PyInstaller 打包"
echo "════════════════════════════════════════════════════════════════"

# 检查依赖
echo ""
echo "📋 检查系统依赖..."

check_command() {
    if ! command -v $1 &> /dev/null; then
        echo "❌ 缺少 $1，请安装"
        return 1
    fi
    echo "✅ $1 已安装"
    return 0
}

check_command python3
check_command pip3

# 创建虚拟环境
echo ""
echo "🔧 创建虚拟环境..."
if [ -d "venv" ]; then
    echo "⚠️  虚拟环境已存在，跳过创建"
else
    python3 -m venv venv
    echo "✅ 虚拟环境已创建"
fi

# 激活虚拟环境
source venv/bin/activate

# 安装依赖
echo ""
echo "📦 安装 Python 依赖..."
pip install --upgrade pip
pip install -r requirements.txt
pip install pyinstaller

# 清理旧构建
echo ""
echo "🧹 清理旧构建文件..."
rm -rf build dist *.spec __pycache__ .pytest_cache
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true

# 运行 PyInstaller
echo ""
echo "🔨 开始打包..."
pyinstaller \
    --name steamdeck-galgame \
    --onefile \
    --windowed \
    --console \
    --add-data "data/icons:data/icons" \
    --hidden-import=src \
    --hidden-import=src.tui \
    --hidden-import=src.ui \
    --hidden-import=src.core \
    --hidden-import=src.core.installers \
    --hidden-import=src.utils \
    --hidden-import=requests \
    --hidden-import=tkinter \
    --icon=data/icons/io.github.steamdeck_galgame.svg \
    --strip \
    --clean \
    run.py

# 检查输出
echo ""
echo "✅ 打包完成！"
echo ""
echo "════════════════════════════════════════════════════════════════"
echo "  输出文件位置"
echo "════════════════════════════════════════════════════════════════"
echo ""

if [ -f "dist/steamdeck-galgame" ]; then
    echo "✅ 可执行文件: dist/steamdeck-galgame"
    ls -lh dist/steamdeck-galgame
    
    echo ""
    echo "📋 使用方法："
    echo ""
    echo "1️⃣ 复制文件到 SteamDeck:"
    echo "   scp dist/steamdeck-galgame deck@steamdeck:~/"
    echo ""
    echo "2️⃣ 在 SteamDeck 上运行:"
    echo "   chmod +x ~/steamdeck-galgame"
    echo "   ~/steamdeck-galgame"
    echo ""
    echo "✨ 无需 Python 和 pip！"
    echo ""
else
    echo "❌ 打包失败！"
    exit 1
fi

echo "════════════════════════════════════════════════════════════════"
