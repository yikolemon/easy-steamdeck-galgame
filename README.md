# SteamDeck 环境配置工具

为 SteamDeck 提供快速、可复现的中文/日文游戏环境配置工具（GUI + 核心逻辑）。主要用于在 SteamOS 上为视觉小说与日语/中文游戏配置本地化支持、字体与启动参数。

- 徽章: ![python](https://img.shields.io/badge/python-3.7%2B-blue) ![license](https://img.shields.io/badge/license-MIT-green)

简体中文  |  [English](./README_en.md)


截图
------

应用界面示例：

![screenshot](assert/README/image-20260207191837688.png)

安装
----

两种常用方式：下载 Release 二进制或从源码运行。

- 从 [Release](https://github.com/yikolemon/easy-steamdeck-galgame/releases) 下载（推荐普通用户）

  1. 前往 Releases 页面下载对应的压缩包或可执行文件
  2. 解压并按照包内说明执行

- 从源码运行（开发者 / 调试）

  ```bash
  # 安装依赖
  pip install -r requirements.txt
  
  # 运行应用
  python run.py
  ```

使用指南
--------

基本流程：

1. 启动应用：`python run.py` 或运行打包后的二进制
2. 安装系统语言包（按提示执行需要的命令）
3. 安装/复制字体到指定目录
4. 生成复制游戏启动属性（Proton 启动参数）

主要功能
--------

- 简单的 GUI 向导，按步骤完成本地化配置
- 自动下载并安装字体到系统字体目录
- 生成/应用 Proton 启动参数以修复游戏显示问题
- 支持批量处理与日志输出，便于调试与回滚
- 可打包为独立可执行文件（PyInstaller）

系统要求
--------

- 目标平台：SteamDeck / SteamOS（基于 Arch Linux）
- Python 3.7+
- 需要 root 权限以执行系统级字体安装或修改（在 SteamOS 上可能需使用 `steamos-readonly`）
- 依赖见 `requirements.txt`

从源码构建（开发者）
-------------------

```bash
# 安装依赖
pip install -r requirements.txt

# 运行单元测试
pytest -v --tb=short

# 构建可执行（仅 Linux）
./build_pyinstaller.sh release
# 或直接：
BUILD_TYPE=release pyinstaller --clean steamdeck_galgame.spec
```

项目结构
-------

```
steamdeck-galgame/
├── run.py                  # 应用入口
├── src/
│   ├── gui/                # Tkinter GUI
│   ├── core/               # 核心逻辑与安装器
│   │   ├── installers/     # 各类安装器实现（ABC 模式）
│   │   └── downloader/     # Release 与资源下载器
│   ├── utils/              # 工具函数
│   └── config/             # 配置管理
├── tests/                  # 单元测试
└── doc/                    # 文档
```

许可证
----

本项目采用 MIT 许可证
