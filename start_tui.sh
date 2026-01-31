#!/bin/bash
# SteamDeck 中文环境配置工具 - TUI 启动脚本
# 用于直接在终端或 Steam 中启动

set -e

# 获取脚本目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# 检查 Python
if ! command -v python3 &> /dev/null; then
    echo "❌ 错误: 未找到 python3"
    echo "请先安装 Python 3.7 或更高版本"
    exit 1
fi

# 检查依赖
echo "检查依赖..."
python3 -c "import rich" 2>/dev/null || {
    echo "安装 rich..."
    pip3 install -q rich requests
}

# 进入项目目录
cd "$SCRIPT_DIR"

# 启动应用
echo "启动 SteamDeck 中文环境配置工具..."
python3 run.py --tui

exit $?
