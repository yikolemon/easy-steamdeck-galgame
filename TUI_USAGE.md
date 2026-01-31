# TUI 模式使用指南

## 概述

本应用现已支持 **TUI（终端用户界面）** 模式，完全适配 SteamDeck。TUI 模式无需 GUI 环境，直接在终端中运行。

## 安装依赖

```bash
# 安装所有依赖
pip install -r requirements.txt

# 或者只安装 TUI 所需的依赖
pip install requests>=2.25.0 rich>=10.0.0
```

## 运行方式

### 方式 1: 默认启动（推荐 SteamDeck）
```bash
python3 run.py
```
默认启动 **TUI 模式**（更适合 SteamDeck）

### 方式 2: 显式指定 TUI 模式
```bash
python3 run.py --tui
```

### 方式 3: 启动 GUI 模式（需要图形环境）
```bash
python3 run.py --gui
```

## 功能说明

### 1️⃣ 中文 Locale 安装
- 检查当前 locale 安装状态
- 需要 root 权限（会提示输入密码）
- 操作流程：关闭只读 → 初始化 pacman → 启用 locale → 恢复只读

### 2️⃣ 中文字体安装
**两种方式选择：**
- **从 GitHub 下载**：自动列出可用字体包，支持下载后直接安装
- **使用本地文件**：指定本地 zip 字体包的路径

### 3️⃣ 游戏启动选项配置
显示标准的启动命令，用于在 Steam 游戏属性中配置。

### 4️⃣ 查看系统状态
实时显示：
- 中文 Locale 是否已安装
- 中文字体安装数量

## 键盘操作

- 使用 **数字键** 选择菜单项
- 使用 **Enter** 确认选择
- 使用 **Y/N** 确认或取消操作（需要时）
- 使用 **Ctrl+C** 中断程序

## SteamDeck 特殊说明

### 为什么选择 TUI？

1. **权限充足**：可以直接获得系统权限修改 locale
2. **轻量级**：不依赖 X11/Wayland 和 GUI 库
3. **手柄兼容**：通过虚拟键盘或按键映射支持手柄操作
4. **稳定可靠**：避免 GUI 在特殊环境下的兼容性问题

### SteamDeck 上使用

在 SteamDeck 上，可以通过以下方式运行：

```bash
# 在 Konsole 终端中直接运行
python3 run.py

# 或者创建一个启动脚本
chmod +x start.sh
./start.sh
```

### 添加到 Steam 作为非 Steam 游戏

1. 创建 `steamdeck_config.sh`：
```bash
#!/bin/bash
cd /path/to/steamdeck-galgame
python3 run.py --tui
```

2. 在 Steam 中添加为"非 Steam 游戏"
3. 设置启动程序为该脚本

## 故障排除

### 问题 1: 导入错误
```
错误: 无法导入 TUI 模块
```

**解决方案：**
```bash
pip install rich>=10.0.0
```

### 问题 2: 权限不足
```
❌ 无法关闭只读模式
```

**解决方案：**
- 需要 sudo 权限
- 在 SteamDeck 上需要设置 sudoers 规则

### 问题 3: 下载字体包失败
- 检查网络连接
- 如果 GitHub 访问慢，可使用本地 zip 文件

## 架构说明

```
src/
├── tui/                 # TUI 模块
│   ├── __init__.py
│   └── main.py         # TUI 主程序
├── ui/                 # GUI 模块
│   ├── main.py
│   ├── widgets.py
│   └── ...
├── core/               # 核心业务逻辑（TUI/GUI 共用）
│   └── installers/
└── utils/              # 工具函数（TUI/GUI 共用）
```

### 核心逻辑复用

- TUI 和 GUI 共用所有核心业务逻辑
- 只有用户界面层不同
- 所有系统操作（locale、字体安装等）完全一致

## 许可证

MIT License
