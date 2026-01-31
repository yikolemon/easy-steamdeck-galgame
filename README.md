# SteamDeck 中文环境配置工具

🎮 为 SteamDeck 配置中文游戏环境的工具

通过这个工具，你可以：
- 为系统安装中文语言支持（locale）
- 为游戏安装中文字体
- 配置游戏中文启动环境

## 🚀 快速安装

### 安装依赖

```bash
# 安装所有依赖
pip install -r requirements.txt
```

### 运行应用

```bash
# 默认启动 TUI 模式（推荐 SteamDeck）
python3 run.py

# 或者指定 GUI 模式
python3 run.py --gui

# 显式指定 TUI 模式
python3 run.py --tui
```

**注意**：本项目现已同时支持 **TUI（终端界面）** 和 **GUI（图形界面）** 两种运行方式。
- **TUI 模式**：无需图形环境，更适合 SteamDeck，直接获得系统权限
- **GUI 模式**：需要 X11/Wayland 和 Tkinter

## 功能

### 1️⃣ 中文 Locale 安装
- 为系统启用简体中文语言支持
- 自动管理系统权限
- 只需执行一次

### 2️⃣ 中文字体安装
- 安装中文显示字体
- 智能跳过已存在的字体
- 只需执行一次

### 3️⃣ 游戏启动选项配置
- 为游戏提供中文启动命令
- 支持复制到剪贴板
- 每个游戏配置一次

## 系统要求

- SteamOS 3.0+（SteamDeck 原装系统）
- Python 3.7+
- 100MB 磁盘空间

**对于 TUI 模式**：无额外依赖

**对于 GUI 模式**：需要 Tkinter 和图形环境（X11/Wayland）

## 使用方法

### TUI 模式使用（推荐 SteamDeck）

1. 运行应用：`python3 run.py`
2. 使用数字键选择功能
3. 按照提示操作

详见 [TUI_USAGE.md](./TUI_USAGE.md)

### GUI 模式使用

1. 运行应用：`python3 run.py --gui`
2. 使用鼠标点击按钮
3. 按照提示操作

## 项目结构

该项目采用模块化架构，支持 TUI 和 GUI 两种界面：

```
src/
├── tui/              # TUI 模块（新增）
│   ├── __init__.py
│   └── main.py
├── ui/               # GUI 模块
│   ├── main.py
│   ├── widgets.py
│   └── ...
├── core/             # 核心业务逻辑（TUI/GUI 共用）
│   ├── installers/
│   └── ...
└── utils/            # 工具函数（TUI/GUI 共用）
```

详见：

- 📄 [STRUCTURE.md](./STRUCTURE.md) - 详细项目结构说明
- 📄 [OPTIMIZATION_REPORT.md](./OPTIMIZATION_REPORT.md) - 优化改进详细分析
- 📄 [TUI_USAGE.md](./TUI_USAGE.md) - TUI 模式详细说明

### 快速命令

```bash
python3 run.py          # 运行应用
make run                # 使用 Makefile 运行
make test               # 运行测试
make lint               # 代码检查
make format             # 代码格式化
make clean              # 清理临时文件
```

## 许可证

MIT License

## 版本

v1.0.0 - 完整模块化重构版本

