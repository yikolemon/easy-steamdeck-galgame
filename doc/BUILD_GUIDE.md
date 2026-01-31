# Debug & Release Build Guide

## 📋 概述

此项目现支持两种构建模式，通过 `BUILD_TYPE` 环境变量控制：

| 版本 | 模式 | 日志级别 | 用途 |
|------|------|--------|------|
| **release** | 生产版本 | INFO | 日常使用，性能优化 |
| **debug** | 开发版本 | DEBUG | 故障排查，开发调试 |

---

## 🔧 本地构建

### 前置要求
```bash
pip install -r requirements.txt
pip install pyinstaller
```

### 方法 1: 构建单个版本

#### 构建 Release（推荐用于分发）
```bash
./build_pyinstaller.sh release
# 输出: dist/steamdeck-galgame-release
```

#### 构建 Debug（用于故障排查）
```bash
./build_pyinstaller.sh debug
# 输出: dist/steamdeck-galgame-debug
```

### 方法 2: 同时构建两个版本
```bash
./build_pyinstaller.sh all
# 输出:
#   dist/steamdeck-galgame-release
#   dist/steamdeck-galgame-debug
```

### 方法 3: 使用 PyInstaller 直接构建

#### Release 构建
```bash
export BUILD_TYPE=release
pyinstaller --clean steamdeck_galgame.spec
```

#### Debug 构建
```bash
export BUILD_TYPE=debug
pyinstaller --clean steamdeck_galgame.spec
```

---

## 🚀 GitHub Actions 自动构建

### 触发条件
- 推送到 `master` 分支
- 创建 `v*` 标签（自动创建 Release）
- 手动触发 (`workflow_dispatch`)

### 构建流程

1. **矩阵构建**：同时构建 debug 和 release 版本
   - 并行构建（加快速度）
   - 每个版本单独验证

2. **发布流程**（仅在创建标签时）：
   - 下载所有构建产物
   - 创建 GitHub Release
   - 上传两个版本的可执行文件和 tar.gz

### Release 页面内容

发布时会包含：
- `steamdeck-galgame-release` - Release 可执行文件
- `steamdeck-galgame-debug` - Debug 可执行文件
- 对应的 `.tar.gz` 压缩包

---

## 📦 输出文件结构

```
dist/
├── steamdeck-galgame-release      # Release 版本可执行文件
├── steamdeck-galgame-release.tar.gz
├── steamdeck-galgame-debug        # Debug 版本可执行文件
└── steamdeck-galgame-debug.tar.gz
```

---

## 🎯 日志行为差异

### Release 版本（INFO 级别）
```
2025-01-31 18:30:45 - INFO - Starting application
2025-01-31 18:30:46 - WARNING - Low disk space
```

### Debug 版本（DEBUG 级别）
```
2025-01-31 18:30:45 - INFO - Starting application
2025-01-31 18:30:45 - DEBUG - Loading config from /etc/config.yaml
2025-01-31 18:30:45 - DEBUG - Initializing TUI...
2025-01-31 18:30:46 - WARNING - Low disk space
2025-01-31 18:30:46 - DEBUG - Disk check: 2.5GB available
```

---

## 💻 在 SteamDeck 上使用

### Release 版本（推荐）
```bash
scp dist/steamdeck-galgame-release deck@steamdeck:~/
ssh deck@steamdeck
chmod +x ~/steamdeck-galgame-release
./steamdeck-galgame-release
```

### Debug 版本（用于故障排查）
```bash
./steamdeck-galgame-debug  # 显示所有调试信息
```

---

## 🔍 构建配置文件

### `run.py` - 应用入口
```python
build_type = os.environ.get('BUILD_TYPE', 'release').lower()
log_level = logging.DEBUG if build_type == 'debug' else logging.INFO
logging.basicConfig(level=log_level, ...)
```

### `steamdeck_galgame.spec` - PyInstaller 配置
```python
build_type = os.environ.get('BUILD_TYPE', 'release').lower()
exe_name = 'steamdeck-galgame-debug' if build_type == 'debug' else 'steamdeck-galgame-release'
```

### `build_pyinstaller.sh` - 构建脚本
支持 `debug`, `release`, `all` 三种模式

### `.github/workflows/build-pyinstaller.yml` - CI/CD 工作流
矩阵构建 debug 和 release，创建标签时自动发布

---

## ✅ 验证构建

### 检查可执行文件
```bash
file dist/steamdeck-galgame-release
file dist/steamdeck-galgame-debug
```

### 运行可执行文件（本地测试）
```bash
# Release - 正常输出
./dist/steamdeck-galgame-release

# Debug - 详细日志输出
./dist/steamdeck-galgame-debug
```

### 比较文件大小
```bash
ls -lh dist/steamdeck-galgame-*
```

---

## 🐛 故障排查

### 如果构建失败

1. 检查依赖是否已安装
   ```bash
   pip list | grep pyinstaller
   ```

2. 清理旧构建
   ```bash
   rm -rf build dist __pycache__
   ```

3. 重新运行构建
   ```bash
   ./build_pyinstaller.sh debug
   ```

### 获取详细的构建日志

使用 `--debug` 选项运行 PyInstaller（如需要）：
```bash
BUILD_TYPE=debug pyinstaller --debug=imports steamdeck_galgame.spec
```

---

## 📚 相关文件

- `run.py` - 应用入口，负责日志配置
- `steamdeck_galgame.spec` - PyInstaller 规范文件
- `build_pyinstaller.sh` - 本地构建脚本
- `.github/workflows/build-pyinstaller.yml` - CI/CD 工作流

---

## 🎉 完成！

现在您可以：
- ✅ 构建 debug 版本用于故障排查
- ✅ 构建 release 版本用于分发
- ✅ GitHub Actions 自动构建两个版本
- ✅ 在 SteamDeck 上选择合适的版本运行

