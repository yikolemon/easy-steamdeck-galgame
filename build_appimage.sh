#!/bin/bash

# SteamDeck GAL Config - AppImage 构建脚本
# 这个脚本将项目打包成 AppImage 格式

set -e

# 配置
APP_NAME="steamdeck-galgame"
APP_VERSION="1.0.0"
APP_ID="io.github.steamdeck_galgame"
ARCH="x86_64"
OUTPUT_FILE="${APP_NAME}-${APP_VERSION}-${ARCH}.AppImage"

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_status() {
    echo -e "${BLUE}==>${NC} $1"
}

print_success() {
    echo -e "${GREEN}✓${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

# 检查前置条件
check_requirements() {
    print_status "检查前置条件..."
    
    # 检查必要的工具
    local required_tools=("python3" "pip3" "wget" "fuse")
    
    for tool in "${required_tools[@]}"; do
        if ! command -v "$tool" &> /dev/null; then
            print_warning "$tool 未安装"
        else
            print_success "找到 $tool"
        fi
    done
    
    # 检查 appimagetool
    if ! command -v appimagetool &> /dev/null; then
        print_warning "appimagetool 未安装，将自动下载"
        download_appimagetool
    else
        print_success "找到 appimagetool"
    fi
}

download_appimagetool() {
    print_status "下载 appimagetool..."
    
    local appimagetool_url="https://github.com/AppImage/AppImageKit/releases/download/13/appimagetool-${ARCH}.AppImage"
    local appimagetool_path="/tmp/appimagetool-${ARCH}.AppImage"
    
    if [ ! -f "$appimagetool_path" ]; then
        wget -q --show-progress "$appimagetool_url" -O "$appimagetool_path"
        chmod +x "$appimagetool_path"
        print_success "appimagetool 已下载"
    fi
}

# 创建 AppDir 目录结构
setup_appdir() {
    print_status "设置 AppDir 目录结构..."
    
    local appdir="AppDir"
    
    # 清理旧的 AppDir
    if [ -d "$appdir" ]; then
        rm -rf "$appdir"
    fi
    
    # 创建基本目录结构
    mkdir -p "$appdir"/{app,bin,lib,usr/share/{applications,icons/hicolor/scalable/apps}}
    
    # 复制应用文件
    cp -r src "$appdir/app/"
    cp run.py "$appdir/app/"
    cp requirements.txt "$appdir/app/"
    cp -r data "$appdir/app/"
    
    print_success "AppDir 目录结构已创建"
}

# 设置 Python 环境
setup_python_env() {
    print_status "设置 Python 虚拟环境..."
    
    local appdir="AppDir"
    local venv_path="$appdir/app/venv"
    
    # 创建虚拟环境
    python3 -m venv "$venv_path"
    
    # 升级 pip
    "$venv_path/bin/pip" install --upgrade pip setuptools wheel -q
    
    # 安装依赖
    print_status "安装 Python 依赖..."
    "$venv_path/bin/pip" install -r "$appdir/app/requirements.txt" -q
    
    print_success "Python 环境已设置"
}

# 创建启动脚本
create_apprun_script() {
    print_status "创建 AppRun 启动脚本..."
    
    local appdir="AppDir"
    local apprun_script="$appdir/AppRun"
    
    cat > "$apprun_script" << 'EOF'
#!/bin/bash
set -e

# 获取 AppDir 路径
APPDIR="$(cd "$(dirname "$0")" && pwd)"

# 设置环境变量
export LD_LIBRARY_PATH="${APPDIR}/lib:${LD_LIBRARY_PATH}"
export PATH="${APPDIR}/bin:${PATH}"
export PYTHONHOME="${APPDIR}/app/venv"
export PYTHONPATH="${APPDIR}/app:${PYTHONPATH}"

# 以 TUI 模式运行应用
exec "${APPDIR}/app/venv/bin/python3" "${APPDIR}/app/run.py" --tui "$@"
EOF

    chmod +x "$apprun_script"
    print_success "AppRun 启动脚本已创建"
}

# 创建 .desktop 文件
create_desktop_file() {
    print_status "创建 .desktop 应用菜单文件..."
    
    local appdir="AppDir"
    local desktop_file="$appdir/io.github.steamdeck_galgame.desktop"
    
    cat > "$desktop_file" << 'EOF'
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

    chmod 644 "$desktop_file"
    print_success ".desktop 文件已创建"
}

# 处理图标
setup_icons() {
    print_status "设置应用图标..."
    
    local appdir="AppDir"
    local icon_src="data/icons/io.github.steamdeck_galgame.svg"
    local icon_dest="$appdir/usr/share/icons/hicolor/scalable/apps/io.github.steamdeck_galgame.svg"
    
    if [ -f "$icon_src" ]; then
        cp "$icon_src" "$icon_dest"
        print_success "图标已复制"
    else
        print_warning "未找到图标文件: $icon_src"
    fi
}

# 打包 AppImage
create_appimage() {
    print_status "打包 AppImage..."
    
    local appdir="AppDir"
    local appimagetool_path
    
    # 查找 appimagetool
    if command -v appimagetool &> /dev/null; then
        appimagetool_path=$(command -v appimagetool)
    else
        appimagetool_path="/tmp/appimagetool-${ARCH}.AppImage"
    fi
    
    if [ ! -f "$appimagetool_path" ]; then
        print_error "找不到 appimagetool"
        return 1
    fi
    
    # 运行 appimagetool
    "$appimagetool_path" "$appdir" "$OUTPUT_FILE"
    
    # 设置执行权限
    chmod +x "$OUTPUT_FILE"
    
    print_success "AppImage 已创建: $OUTPUT_FILE"
}

# 显示构建信息
show_build_info() {
    print_status "构建信息"
    
    echo ""
    echo "应用名称: SteamDeck GAL Config"
    echo "应用 ID: $APP_ID"
    echo "版本: $APP_VERSION"
    echo "架构: $ARCH"
    echo "输出文件: $OUTPUT_FILE"
    echo ""
    
    if [ -f "$OUTPUT_FILE" ]; then
        local size=$(du -h "$OUTPUT_FILE" | cut -f1)
        print_success "构建完成！文件大小: $size"
    fi
}

# 清理临时文件
cleanup() {
    print_status "清理..."
    
    # 可选: 删除 AppDir（保留以便调试）
    # rm -rf AppDir
    
    print_success "清理完成"
}

# 主函数
main() {
    echo ""
    echo "╔════════════════════════════════════════════════════════════════╗"
    echo "║        SteamDeck GAL Config - AppImage 构建脚本                 ║"
    echo "╚════════════════════════════════════════════════════════════════╝"
    echo ""
    
    # 检查前置条件
    check_requirements
    echo ""
    
    # 设置 AppDir
    setup_appdir
    echo ""
    
    # 设置 Python 环境
    setup_python_env
    echo ""
    
    # 创建启动脚本和文件
    create_apprun_script
    echo ""
    
    create_desktop_file
    echo ""
    
    setup_icons
    echo ""
    
    # 创建 AppImage
    create_appimage
    echo ""
    
    # 显示信息
    show_build_info
    echo ""
    
    # 清理
    cleanup
    echo ""
    
    echo "╔════════════════════════════════════════════════════════════════╗"
    echo "║  构建完成！AppImage 已准备就绪。                                ║"
    echo "║                                                                ║"
    echo "║  使用方式:                                                     ║"
    echo "║    1. 直接运行: ./${OUTPUT_FILE}"
    echo "║    2. 在 Steam 中添加为非 Steam 游戏                          ║"
    echo "║    3. 复制到 /usr/bin: sudo cp ${OUTPUT_FILE} /usr/local/bin/ ║"
    echo "╚════════════════════════════════════════════════════════════════╝"
    echo ""
}

# 运行主函数
main
