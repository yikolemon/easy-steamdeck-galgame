# 项目结构说明

## 目录结构

```
steamdeck-galgame/
├── src/                          # 主源代码目录
│   ├── __init__.py              # 包初始化
│   ├── ui/                       # 用户界面模块
│   │   ├── __init__.py
│   │   ├── main.py              # 主窗口
│   │   ├── widgets.py           # UI 组件（StatusIndicator, TaskTab）
│   │   └── game_launcher_tab.py  # 游戏启动选项 Tab
│   ├── core/                     # 核心业务逻辑
│   │   ├── __init__.py
│   │   ├── game_launcher.py      # 游戏启动器
│   │   └── installers/          # 安装器模块
│   │       ├── __init__.py
│   │       ├── base.py          # 基类
│   │       ├── locale.py        # Locale 安装器
│   │       └── font.py          # 字体安装器
│   ├── utils/                    # 工具函数
│   │   ├── __init__.py
│   │   ├── command.py           # 命令执行
│   │   ├── system.py            # 系统操作
│   │   └── path.py              # 路径操作
│   └── config/                   # 配置管理
│       └── __init__.py          # 配置类
├── tests/                        # 测试目录
│   └── test_logic.py            # 逻辑测试
├── run.py                        # 应用入口
├── README.md                     # 项目说明
├── STRUCTURE.md                 # 本文件
├── io.github.steamdeck_galgame.json  # Flatpak 配置
└── GAL_Fonts_Minimal.zip        # 字体包

```

## 模块说明

### src/ui/ - 用户界面层
负责所有的用户界面相关代码：
- `main.py` - 主窗口框架
- `widgets.py` - 可复用的 UI 组件
- `game_launcher_tab.py` - 游戏启动选项配置界面

### src/core/ - 核心业务逻辑层
核心功能实现：
- `installers/` - 各种安装器
  - `base.py` - 安装器基类（抽象类）
  - `locale.py` - 中文 Locale 安装
  - `font.py` - 中文字体安装
- `game_launcher.py` - 游戏启动器配置

### src/utils/ - 工具层
通用工具函数：
- `command.py` - shell 命令执行
- `system.py` - 系统操作（readonly 模式、Locale 检查等）
- `path.py` - 路径操作

### src/config/ - 配置管理
集中管理所有配置常量：
- `Config` 类 - 应用配置

## 版本历史

### v1.0.0 (2026-01-31)
- 初始版本
- 完整重构：从平面结构优化为分层模块化结构
- 分离 UI 层、业务逻辑层和工具层
- 引入基类和工厂模式改进代码质量

## 运行应用

### 直接运行
```bash
python3 run.py
```

### 通过 Flatpak 运行
```bash
flatpak run io.github.steamdeck_galgame
```

## 开发建议

### 添加新功能
1. 在 `src/core/` 中添加新的业务逻辑类
2. 在 `src/ui/` 中添加对应的 UI 组件
3. 在 `tests/` 中添加测试

### 修改配置
所有配置常量都应该在 `src/config/__init__.py` 中定义，方便集中管理。

### 添加工具函数
新的工具函数应该放在 `src/utils/` 对应的模块中：
- 系统操作 → `system.py`
- 命令执行 → `command.py`
- 路径操作 → `path.py`
