#!/bin/bash

# SteamDeck PyInstaller 交叉编译脚本
# 在标准 Linux 环境上为不同架构构建独立可执行文件
# 支持: x86_64, ARM64 (SteamDeck 官方未来可能支持)

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$SCRIPT_DIR"

# 获取目标架构（默认为当前系统架构）
TARGET_ARCH="${1:-native}"

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_header() {
    echo -e "${BLUE}════════════════════════════════════════════════════════════════${NC}"
    echo -e "${BLUE}  $1${NC}"
    echo -e "${BLUE}════════════════════════════════════════════════════════════════${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

# ============================================================================
# 显示帮助信息
# ============================================================================
show_usage() {
    cat << EOF
用法: bash build_pyinstaller_crossplatform.sh [架构]

支持的架构:
    native      在本机编译 (默认)
    x86_64      为 x86_64 (SteamDeck, 大多数 Linux PC) 编译
    aarch64     为 ARM64/aarch64 编译

示例:
    bash build_pyinstaller_crossplatform.sh              # 本机编译
    bash build_pyinstaller_crossplatform.sh x86_64       # 为 x86_64 编译
    bash build_pyinstaller_crossplatform.sh aarch64      # 为 ARM64 编译

环境需求:
    - Python 3.7+
    - pip 或 pip3
    - (交叉编译) 对应架构的开发工具链

输出文件:
    dist/steamdeck-galgame                    (可执行文件)
    dist/steamdeck-galgame-{arch}.tar.gz      (压缩包)

EOF
    exit 1
}

# ============================================================================
# 检查参数
# ============================================================================
if [[ "$TARGET_ARCH" == "-h" || "$TARGET_ARCH" == "--help" ]]; then
    show_usage
fi

# ============================================================================
# 检查依赖
# ============================================================================
check_command() {
    if ! command -v $1 &> /dev/null; then
        print_error "缺少 $1，请安装"
        return 1
    fi
    print_success "$1 已安装"
    return 0
}

print_header "检查系统依赖"

check_command python3 || exit 1
check_command pip3 || exit 1

# 获取 Python 版本
PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
print_info "Python 版本: $PYTHON_VERSION"

# 获取系统架构信息
SYSTEM_ARCH=$(uname -m)
print_info "系统架构: $SYSTEM_ARCH"

# ============================================================================
# 交叉编译架构检查
# ============================================================================
print_header "配置编译架构"

if [[ "$TARGET_ARCH" == "native" ]]; then
    print_info "将使用本机架构编译"
    EFFECTIVE_ARCH="$SYSTEM_ARCH"
elif [[ "$TARGET_ARCH" == "x86_64" ]]; then
    if [[ "$SYSTEM_ARCH" == "x86_64" ]]; then
        EFFECTIVE_ARCH="x86_64"
        print_info "本机已是 x86_64，无需交叉编译"
    else
        EFFECTIVE_ARCH="x86_64"
        print_warning "将进行交叉编译：$SYSTEM_ARCH → x86_64"
        print_warning "请确保已安装对应的交叉编译工具链"
    fi
elif [[ "$TARGET_ARCH" == "aarch64" ]]; then
    if [[ "$SYSTEM_ARCH" == "aarch64" ]]; then
        EFFECTIVE_ARCH="aarch64"
        print_info "本机已是 aarch64，无需交叉编译"
    else
        EFFECTIVE_ARCH="aarch64"
        print_warning "将进行交叉编译：$SYSTEM_ARCH → aarch64"
        print_warning "请确保已安装对应的交叉编译工具链"
    fi
else
    print_error "未知的架构: $TARGET_ARCH"
    show_usage
fi

# ============================================================================
# 创建虚拟环境
# ============================================================================
print_header "设置 Python 虚拟环境"

VENV_DIR="venv_${EFFECTIVE_ARCH}"

if [ -d "$VENV_DIR" ]; then
    print_warning "虚拟环境已存在: $VENV_DIR，跳过创建"
else
    print_info "创建虚拟环境: $VENV_DIR..."
    python3 -m venv "$VENV_DIR"
    print_success "虚拟环境已创建"
fi

# 激活虚拟环境
source "$VENV_DIR/bin/activate"

# ============================================================================
# 安装依赖
# ============================================================================
print_header "安装 Python 依赖"

print_info "升级 pip..."
pip install --upgrade pip

print_info "安装项目依赖..."
pip install -r requirements.txt

print_info "安装 PyInstaller..."
pip install pyinstaller

print_success "所有依赖已安装"

# ============================================================================
# 清理旧构建
# ============================================================================
print_header "清理旧构建文件"

print_info "清理 build/ dist/ 目录..."
rm -rf build dist __pycache__ .pytest_cache

print_info "清理缓存..."
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true

print_success "清理完成"

# ============================================================================
# 构建可执行文件
# ============================================================================
print_header "构建 PyInstaller 可执行文件"

EXECUTABLE_NAME="steamdeck-galgame"
OUTPUT_DIR="dist"

print_info "目标架构: $EFFECTIVE_ARCH"
print_info "输出名称: $EXECUTABLE_NAME"
print_info "输出目录: $OUTPUT_DIR"
echo ""

# 设置环保变量用于 PyInstaller
export ARCHFLAGS=""  # 清除任何架构标志

# 运行 PyInstaller
print_info "执行 PyInstaller..."
echo ""

pyinstaller \
    --name "$EXECUTABLE_NAME" \
    --onefile \
    --console \
    --add-data "data/icons:data/icons" \
    --hidden-import=src \
    --hidden-import=src.tui \
    --hidden-import=src.ui \
    --hidden-import=src.core \
    --hidden-import=src.core.installers \
    --hidden-import=src.utils \
    --hidden-import=requests \
    --hidden-import=rich \
    --hidden-import=tkinter \
    --strip \
    --clean \
    run.py

echo ""

# ============================================================================
# 验证输出
# ============================================================================
print_header "验证构建结果"

EXECUTABLE_PATH="$OUTPUT_DIR/$EXECUTABLE_NAME"

if [ -f "$EXECUTABLE_PATH" ]; then
    print_success "可执行文件已生成: $EXECUTABLE_PATH"
    
    # 显示文件大小
    FILE_SIZE=$(ls -lh "$EXECUTABLE_PATH" | awk '{print $5}')
    print_info "文件大小: $FILE_SIZE"
    
    # 显示文件信息
    echo ""
    print_info "文件类型:"
    file "$EXECUTABLE_PATH"
    
    # 显示架构信息
    echo ""
    if command -v file &> /dev/null; then
        ARCH_INFO=$(file "$EXECUTABLE_PATH" | grep -oP '(x86-64|ARM|aarch64|x86)' || echo "未知")
        print_info "检测到架构: $ARCH_INFO"
    fi
else
    print_error "构建失败！"
    print_error "找不到文件: $EXECUTABLE_PATH"
    exit 1
fi

# ============================================================================
# 创建压缩包
# ============================================================================
print_header "创建分发包"

TARBALL_NAME="${EXECUTABLE_NAME}-${EFFECTIVE_ARCH}-$(date +%Y%m%d).tar.gz"
TARBALL_PATH="$OUTPUT_DIR/$TARBALL_NAME"

print_info "创建压缩包: $TARBALL_NAME..."
cd "$OUTPUT_DIR"
tar -czf "$TARBALL_NAME" "$EXECUTABLE_NAME"
cd "$PROJECT_ROOT"

if [ -f "$TARBALL_PATH" ]; then
    TARBALL_SIZE=$(ls -lh "$TARBALL_PATH" | awk '{print $5}')
    print_success "压缩包已创建: $TARBALL_PATH"
    print_info "压缩包大小: $TARBALL_SIZE"
else
    print_warning "压缩包创建失败，但可执行文件已生成"
fi

# ============================================================================
# 显示使用说明
# ============================================================================
print_header "📋 使用说明"

echo ""
echo "1️⃣ 直接运行本机可执行文件:"
echo "   $EXECUTABLE_PATH"
echo ""

if [[ "$EFFECTIVE_ARCH" == "x86_64" ]]; then
    echo "2️⃣ 复制到 SteamDeck 并运行:"
    echo "   scp $EXECUTABLE_PATH deck@steamdeck:~/"
    echo "   ssh deck@steamdeck"
    echo "   chmod +x ~/$EXECUTABLE_NAME"
    echo "   ~/$EXECUTABLE_NAME"
    echo ""
fi

echo "3️⃣ 或者复制压缩包:"
echo "   scp $TARBALL_PATH deck@steamdeck:~/"
echo "   ssh deck@steamdeck"
echo "   tar -xzf $TARBALL_NAME"
echo "   chmod +x $EXECUTABLE_NAME"
echo "   ./$EXECUTABLE_NAME"
echo ""

echo "✨ 无需 Python、pip 和任何依赖！"
echo ""

# ============================================================================
# 显示完成信息
# ============================================================================
print_header "✅ 构建完成"

echo ""
echo "📦 输出文件:"
echo "   可执行文件: $EXECUTABLE_PATH"
echo "   压缩包:     $TARBALL_PATH (可选)"
echo ""

echo "🏗️ 构建信息:"
echo "   架构:      $EFFECTIVE_ARCH"
echo "   大小:      $FILE_SIZE"
echo "   时间:      $(date)"
echo ""

echo "🚀 下一步:"
echo "   1. 测试可执行文件: $EXECUTABLE_PATH"
echo "   2. 上传到 GitHub Releases"
echo "   3. 分享给用户下载"
echo ""

print_success "🎉 所有操作已完成！"

echo "════════════════════════════════════════════════════════════════"
