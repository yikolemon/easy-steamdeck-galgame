# SteamDeck 中文环境配置工具

为 SteamDeck 配置中文游戏环境的工具。

## 快速开始

### 运行应用

```bash
python3 run.py
```

## 打包成 SteamDeck 可执行文件

### 方式 1: 简单打包

```bash
bash build_pyinstaller.sh
# 输出: dist/steamdeck-galgame
```

### 方式 2: 交叉编译（支持多架构）

```bash
bash build_pyinstaller_crossplatform.sh        # 本机编译
bash build_pyinstaller_crossplatform.sh x86_64 # 为 SteamDeck 编译
```

## SteamDeck 上使用

下载可执行文件后：

```bash
chmod +x steamdeck-galgame
./steamdeck-galgame
```

无需 Python 和任何依赖！

## 项目结构

```
src/
├── tui/               # TUI 界面
├── ui/                # GUI 界面  
├── core/              # 核心业务逻辑
└── utils/             # 工具函数
```

## 许可证

MIT
