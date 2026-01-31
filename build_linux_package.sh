#!/bin/bash

# SteamDeck GAL Config - 简化版 AppImage 构建脚本
# 使用 linuxdeploy 工具链和 Python 打包

set -e

APP_NAME="steamdeck-galgame"
APP_VERSION="1.0.0"
APP_ID="io.github.steamdeck_galgame"
ARCH="x86_64"
OUTPUT_DIR="dist"
BUILD_DIR="build"

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_header() {
    echo ""
    echo "╔════════════════════════════════════════════════════════════════╗"
    echo "║        $1"
    echo "╚════════════════════════════════════════════════════════════════╝"
    echo ""
}

print_status() {
    echo -e "${BLUE}==>${NC} $1"
}

print_success() {
    echo -e "${GREEN}✓${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

# 检查依赖
check_deps() {
    print_status "检查依赖..."
    
    local missing_deps=0
    
    for cmd in python3 pip3; do
        if ! command -v "$cmd" &> /dev/null; then
            print_error "缺少 $cmd"
            missing_deps=$((missing_deps + 1))
        else
            print_success "找到 $cmd"
        fi
    done
    
    if [ $missing_deps -gt 0 ]; then
        print_error "缺少必要的依赖，请安装:"
        echo "  Ubuntu/Debian: sudo apt-get install python3 python3-pip python3-venv"
        echo "  Fedora/RHEL: sudo dnf install python3 python3-pip"
        echo "  Arch/SteamOS: sudo pacman -S python python-pip"
        exit 1
    fi
    
    # 检查 appimage-builder（可选）
    if ! command -v appimage-builder &> /dev/null; then
        print_status "appimage-builder 未安装"
        print_status "将使用简化打包方式"
    else
        print_success "找到 appimage-builder"
    fi
}

# 清理
cleanup() {
    print_status "清理旧文件..."
    rm -rf "$BUILD_DIR" "$OUTPUT_DIR" AppDir
}

# 创建 AppDir 结构
create_appdir() {
    print_status "创建 AppDir 结构..."
    
    mkdir -p AppDir/{app,lib,usr/share/{applications,icons/hicolor/scalable/apps}}
    
    # 复制应用文件
    cp -r src AppDir/app/
    cp run.py AppDir/app/
    cp requirements.txt AppDir/app/
    cp -r data AppDir/app/
    
    print_success "AppDir 结构已创建"
}

# 设置 Python 虚拟环境
setup_venv() {
    print_status "设置 Python 虚拟环境..."
    
    local venv_path="AppDir/app/venv"
    
    # 创建虚拟环境
    python3 -m venv "$venv_path"
    
    # 升级工具
    "$venv_path/bin/pip" install --upgrade pip setuptools wheel -q
    
    # 安装依赖
    print_status "安装 Python 依赖..."
    "$venv_path/bin/pip" install -q -r AppDir/app/requirements.txt
    
    # 清理虚拟环境中的不必要文件
    print_status "优化虚拟环境大小..."
    find "$venv_path" -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
    find "$venv_path" -type d -name "*.dist-info" -exec rm -rf {} + 2>/dev/null || true
    find "$venv_path" -name "*.pyc" -delete 2>/dev/null || true
    
    print_success "Python 虚拟环境已设置"
}

# 创建 AppRun 脚本
create_apprun() {
    print_status "创建 AppRun 启动脚本..."
    
    cat > AppDir/AppRun << 'EOF'
#!/bin/bash
set -e

# 获取 AppDir 路径
APPDIR="$(cd "$(dirname "$0")" && pwd)"

# 设置环境变量
export LD_LIBRARY_PATH="${APPDIR}/lib:${LD_LIBRARY_PATH}"
export PATH="${APPDIR}/bin:${PATH}"
export PYTHONHOME="${APPDIR}/app/venv"
export PYTHONPATH="${APPDIR}/app:${PYTHONPATH}"

# 创建符号链接到 venv 中的 python
if [ ! -L "${APPDIR}/bin/python3" ]; then
    mkdir -p "${APPDIR}/bin"
    ln -sf "${APPDIR}/app/venv/bin/python3" "${APPDIR}/bin/python3"
fi

# 执行应用
exec "${APPDIR}/app/venv/bin/python3" "${APPDIR}/app/run.py" --tui "$@"
EOF

    chmod +x AppDir/AppRun
    print_success "AppRun 脚本已创建"
}

# 创建 .desktop 文件
create_desktop() {
    print_status "创建 .desktop 文件..."
    
    cat > AppDir/io.github.steamdeck_galgame.desktop << 'EOF'
[Desktop Entry]
Version=1.0
Type=Application
Name=SteamDeck GAL Config
Comment=Configure Chinese environment for SteamDeck games
Icon=io.github.steamdeck_galgame
Exec=steamdeck-galgame %U
Terminal=true
Categories=Utility;Game;
Keywords=Chinese;Locale;Font;SteamDeck;
X-AppImage-Name=SteamDeck GAL Config
X-AppImage-Version=1.0.0
EOF

    print_success ".desktop 文件已创建"
}

# 复制图标
setup_icons() {
    print_status "设置应用图标..."
    
    if [ -f "data/icons/io.github.steamdeck_galgame.svg" ]; then
        cp data/icons/io.github.steamdeck_galgame.svg \
           AppDir/usr/share/icons/hicolor/scalable/apps/
        print_success "图标已复制"
    else
        print_error "未找到图标文件"
    fi
}

# 使用 appimage-builder 打包（如果可用）
build_with_appimage_builder() {
    print_status "使用 appimage-builder 打包..."
    
    if ! command -v appimage-builder &> /dev/null; then
        return 1
    fi
    
    appimage-builder --appdir AppDir --output appimage
    
    # 移动到 dist 目录
    mkdir -p "$OUTPUT_DIR"
    mv *.AppImage* "$OUTPUT_DIR/" 2>/dev/null || true
    
    print_success "AppImage 打包完成"
}

# 使用 mksquashfs 打包（备选方案）
build_with_mksquashfs() {
    print_status "使用 mksquashfs 打包..."
    
    if ! command -v mksquashfs &> /dev/null; then
        print_error "mksquashfs 未安装，跳过"
        return 1
    fi
    
    local appimage_name="${APP_NAME}-${APP_VERSION}-${ARCH}.AppImage"
    
    # 下载或创建 AppImage 运行时
    if [ ! -f "AppRun" ]; then
        print_status "下载 AppImage runtime..."
        wget -q https://github.com/AppImage/AppImageKit/releases/download/13/AppRun-${ARCH} -O AppDir/AppRun
        chmod +x AppDir/AppRun
    fi
    
    # 创建 squashfs
    mksquashfs AppDir/ "${appimage_name}.mount" -noappend -quiet
    
    # 创建可执行的 AppImage
    mkdir -p "$OUTPUT_DIR"
    cat AppDir/AppRun "${appimage_name}.mount" > "$OUTPUT_DIR/$appimage_name" 2>/dev/null || {
        print_error "无法创建 AppImage"
        return 1
    }
    
    chmod +x "$OUTPUT_DIR/$appimage_name"
    rm -f "${appimage_name}.mount"
    
    print_success "AppImage 打包完成"
}

# 创建便携式压缩包（备选方案）
create_portable_package() {
    print_status "创建便携式压缩包..."
    
    mkdir -p "$OUTPUT_DIR"
    
    local package_name="${APP_NAME}-${APP_VERSION}-portable"
    
    # 创建打包脚本
    cat > AppDir/steamdeck-galgame << 'EOF'
#!/bin/bash
APPDIR="$(cd "$(dirname "$0")" && pwd)"
export PYTHONHOME="${APPDIR}/venv"
export PYTHONPATH="${APPDIR}:${PYTHONPATH}"
exec "${APPDIR}/venv/bin/python3" "${APPDIR}/run.py" --tui "$@"
EOF

    chmod +x AppDir/steamdeck-galgame
    
    # 创建压缩包
    tar -czf "$OUTPUT_DIR/${package_name}.tar.gz" AppDir/
    
    print_success "便携式压缩包已创建"
}

# 显示结果
show_results() {
    print_status "构建结果"
    
    if [ -d "$OUTPUT_DIR" ] && [ "$(ls -A $OUTPUT_DIR)" ]; then
        echo ""
        echo "输出文件:"
        ls -lh "$OUTPUT_DIR"/*
        echo ""
        
        local total_size=$(du -sh "$OUTPUT_DIR" | cut -f1)
        print_success "总大小: $total_size"
    else
        print_error "没有生成输出文件"
    fi
}

# 显示使用说明
show_usage() {
    echo ""
    echo "╔════════════════════════════════════════════════════════════════╗"
    echo "║  构建完成！已生成 Linux 可执行包。                               ║"
    echo "╚════════════════════════════════════════════════════════════════╝"
    echo ""
    echo "📦 输出文件位于: $OUTPUT_DIR/"
    echo ""
    echo "🚀 使用方式:"
    echo ""
    echo "  1. 如果是 AppImage 文件:"
    echo "     ./dist/*.AppImage"
    echo ""
    echo "  2. 如果是 tar.gz 文件:"
    echo "     tar -xzf dist/*.tar.gz"
    echo "     cd AppDir"
    echo "     ./steamdeck-galgame"
    echo ""
    echo "  3. 在 SteamDeck 中添加为非 Steam 游戏:"
    echo "     - 打开 Steam"
    echo "     - 添加 → 添加非 Steam 游戏"
    echo "     - 浏览到 AppImage 文件"
    echo "     - 保存"
    echo ""
    echo "📋 系统要求:"
    echo "  - Linux (任何发行版)"
    echo "  - x86_64 架构"
    echo "  - glibc 2.29+ (Ubuntu 19.04+, Fedora 30+, etc.)"
    echo ""
}

# 主函数
main() {
    print_header "SteamDeck GAL Config - Linux 打包"
    
    # 检查依赖
    check_deps
    echo ""
    
    # 清理
    cleanup
    echo ""
    
    # 创建 AppDir
    create_appdir
    echo ""
    
    # 设置虚拟环境
    setup_venv
    echo ""
    
    # 创建配置文件
    create_apprun
    echo ""
    
    create_desktop
    echo ""
    
    setup_icons
    echo ""
    
    # 尝试打包
    mkdir -p "$OUTPUT_DIR"
    
    if ! build_with_appimage_builder; then
        print_status "appimage-builder 不可用，尝试备选方案..."
        if ! build_with_mksquashfs; then
            print_status "mksquashfs 不可用，创建便携式包..."
            create_portable_package
        fi
    fi
    echo ""
    
    # 显示结果
    show_results
    echo ""
    
    # 显示使用说明
    show_usage
}

# 运行
main "$@"
