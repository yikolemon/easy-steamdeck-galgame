#!/bin/bash

set -e

echo "👉 1. 关闭 SteamOS 只读模式"
sudo steamos-readonly disable

echo "👉 2. 初始化 pacman key"
sudo pacman-key --init
sudo pacman-key --populate archlinux

echo "👉 3. 启用简体中文 locale（zh_CN.UTF-8）"
if grep -q "^#zh_CN.UTF-8 UTF-8" /etc/locale.gen; then
    sudo sed -i 's/^#zh_CN.UTF-8 UTF-8/zh_CN.UTF-8 UTF-8/' /etc/locale.gen
else
    echo "⚠️ zh_CN.UTF-8 已启用或不存在，跳过修改"
fi

echo "👉 4. 生成 locale"
sudo locale-gen

echo "👉 5. 恢复 SteamOS 只读模式"
sudo steamos-readonly enable

echo "✅ 完成！"
echo
echo "🎮 如需让某个 Steam 游戏使用中文 locale："
echo "在【游戏 → 属性 → 启动选项】中填写："
echo
echo "LANG=zh_CN.UTF-8 LC_ALL=zh_CN.UTF-8 LC_CTYPE=zh_CN.UTF-8 LC_MESSAGES=zh_CN.UTF-8 LANGUAGE=zh_CN %command%"
