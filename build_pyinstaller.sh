#!/bin/bash

# SteamDeck PyInstaller 打包脚本
# 在 Linux/SteamDeck 环境上构建独立可执行文件
#
# 使用方法:
#   ./build_pyinstaller.sh              # 构建 release 版本 (默认)
#   ./build_pyinstaller.sh debug        # 构建 debug 版本 (包含详细日志)
#   ./build_pyinstaller.sh release      # 显式构建 release 版本
#   ./build_pyinstaller.sh all          # 同时构建 debug 和 release 版本

set -e

# 提取构建类型参数 (默认: release)
BUILD_TYPE="${1:-release}"
BUILD_TYPE=$(echo "$BUILD_TYPE" | tr '[:upper:]' '[:lower:]')

# 验证构建类型
if [[ ! "$BUILD_TYPE" =~ ^(debug|release|all)$ ]]; then
    echo "❌ 无效的构建类型: $BUILD_TYPE"
    echo "允许的值: debug, release, all"
    exit 1
fi

echo "════════════════════════════════════════════════════════════════"
echo "  SteamDeck 中文环境配置工具 - PyInstaller 打包"
if [[ "$BUILD_TYPE" == "all" ]]; then
    echo "  模式: DEBUG + RELEASE"
else
    echo "  模式: $(echo $BUILD_TYPE | tr '[:lower:]' '[:upper:]')"
fi
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

# 构建函数
build_variant() {
    local variant=$1
    echo ""
    echo "🔨 开始打包 $variant 版本..."
    
    export BUILD_TYPE=$variant
    pyinstaller --clean steamdeck_galgame.spec
    
    echo "✅ $variant 版本打包完成"
    
    # 检查输出
    if [ -f "dist/steamdeck-galgame-$variant" ]; then
        ls -lh "dist/steamdeck-galgame-$variant"
    else
        echo "❌ $variant 版本打包失败！"
        exit 1
    fi
}

# 根据构建类型执行打包
if [[ "$BUILD_TYPE" == "debug" ]]; then
    build_variant "debug"
elif [[ "$BUILD_TYPE" == "release" ]]; then
    build_variant "release"
elif [[ "$BUILD_TYPE" == "all" ]]; then
    build_variant "debug"
    build_variant "release"
fi

# 检查输出
echo ""
echo "✅ 打包完成！"
echo ""
echo "════════════════════════════════════════════════════════════════"
echo "  输出文件位置"
echo "════════════════════════════════════════════════════════════════"
echo ""

# 显示生成的可执行文件
cd dist
for exe in steamdeck-galgame-*; do
    if [ -f "$exe" ]; then
        echo "📦 $exe ($(du -h "$exe" | cut -f1))"
    fi
done

echo ""
echo "════════════════════════════════════════════════════════════════"
echo "  版本说明"
echo "════════════════════════════════════════════════════════════════"
echo ""
echo "🟢 release - 生产版本"
echo "   - 日志级别: INFO"
echo "   - 仅显示重要信息"
echo "   - 文件体积小"
echo ""
echo "🔵 debug - 调试版本"
echo "   - 日志级别: DEBUG"
echo "   - 显示所有调试信息"
echo "   - 用于开发和故障排除"
echo ""
echo "════════════════════════════════════════════════════════════════"
echo "  使用方法"
echo "════════════════════════════════════════════════════════════════"
echo ""
echo "1️⃣ 复制文件到 SteamDeck:"
echo "   scp dist/steamdeck-galgame-release deck@steamdeck:~/"
echo "   # 或"
echo "   scp dist/steamdeck-galgame-debug deck@steamdeck:~/"
echo ""
echo "2️⃣ 在 SteamDeck 上运行:"
echo "   chmod +x ~/steamdeck-galgame-release"
echo "   ~/steamdeck-galgame-release"
echo ""
echo "✨ 无需 Python 和 pip！"
echo ""
echo "════════════════════════════════════════════════════════════════"
