# Linux AppImage 打包指南

## 📦 概述

本项目已配置为可打包成 **AppImage** 格式，这是一种通用的 Linux 应用分发方式。AppImage 具有以下优点：

- ✅ 单文件可执行，无需安装
- ✅ 跨 Linux 发行版兼容
- ✅ 包含所有依赖，开箱即用
- ✅ 便携，可从 USB 驱动器运行
- ✅ 适合 SteamDeck 和其他 Linux 系统

## 🛠️ 前置要求

### 系统要求

```bash
# Ubuntu/Debian
sudo apt-get install python3 python3-pip python3-venv

# Fedora/RHEL
sudo dnf install python3 python3-pip

# Arch/SteamOS
sudo pacman -S python python-pip

# Alpine
apk add python3 py3-pip
```

### 打包工具（可选）

为了创建优化的 AppImage，推荐安装以下工具之一：

```bash
# 方案 1: appimage-builder（推荐）
pip install appimage-builder

# 方案 2: linuxdeploy
wget https://github.com/linuxdeploy/linuxdeploy/releases/download/continuous/linuxdeploy-x86_64.AppImage
chmod +x linuxdeploy-x86_64.AppImage

# 方案 3: appimagetool
wget https://github.com/AppImage/AppImageKit/releases/download/13/appimagetool-x86_64.AppImage
chmod +x appimagetool-x86_64.AppImage
```

## 🚀 快速开始

### 方式 1: 使用便捷脚本（推荐）

```bash
# 构建 Linux 包（自动选择最佳方案）
chmod +x build_linux_package.sh
./build_linux_package.sh
```

这个脚本会：
1. 检查系统依赖
2. 创建 AppDir 目录结构
3. 设置 Python 虚拟环境
4. 安装所有 Python 依赖
5. 创建 AppImage（如果可用）
6. 备选创建便携式压缩包

### 方式 2: 手动构建

```bash
# 1. 创建 AppDir 目录结构
mkdir -p AppDir/app
cp -r src AppDir/app/
cp run.py requirements.txt AppDir/app/
cp -r data AppDir/app/

# 2. 设置 Python 虚拟环境
python3 -m venv AppDir/app/venv
AppDir/app/venv/bin/pip install -r AppDir/app/requirements.txt

# 3. 创建 AppRun 脚本
cat > AppDir/AppRun << 'EOF'
#!/bin/bash
APPDIR="$(cd "$(dirname "$0")" && pwd)"
export PYTHONHOME="${APPDIR}/app/venv"
export PYTHONPATH="${APPDIR}/app:${PYTHONPATH}"
exec "${APPDIR}/app/venv/bin/python3" "${APPDIR}/app/run.py" --tui "$@"
EOF
chmod +x AppDir/AppRun

# 4. 复制 .desktop 文件
cp io.github.steamdeck_galgame.desktop AppDir/

# 5. 复制图标
mkdir -p AppDir/usr/share/icons/hicolor/scalable/apps/
cp data/icons/io.github.steamdeck_galgame.svg AppDir/usr/share/icons/hicolor/scalable/apps/

# 6. 使用 appimagetool 创建 AppImage
appimagetool AppDir steamdeck-galgame-1.0.0-x86_64.AppImage
```

## 📋 输出文件

打包成功后，你将获得以下文件：

### AppImage 文件
```
dist/steamdeck-galgame-1.0.0-x86_64.AppImage
```

- 单个可执行文件
- 大约 100-150 MB（取决于依赖）
- 无需安装，双击即可运行

### 便携式压缩包
```
dist/steamdeck-galgame-1.0.0-portable.tar.gz
```

- 压缩后约 20-30 MB
- 解压后可运行

## 💻 使用方式

### 直接运行

```bash
# 使 AppImage 可执行
chmod +x steamdeck-galgame-1.0.0-x86_64.AppImage

# 运行
./steamdeck-galgame-1.0.0-x86_64.AppImage
```

### 系统范围安装

```bash
# 复制到系统路径
sudo cp steamdeck-galgame-1.0.0-x86_64.AppImage /usr/local/bin/steamdeck-galgame
sudo chmod +x /usr/local/bin/steamdeck-galgame

# 现在可以从任何地方运行
steamdeck-galgame
```

### 创建桌面快捷方式

```bash
# 复制到应用菜单
mkdir -p ~/.local/share/applications
cp io.github.steamdeck_galgame.desktop ~/.local/share/applications/

# 编辑 .desktop 文件，更新 Exec 路径
sed -i 's|Exec=.*|Exec=/path/to/steamdeck-galgame-1.0.0-x86_64.AppImage|' \
    ~/.local/share/applications/io.github.steamdeck_galgame.desktop
```

### 在 SteamDeck 中使用

#### 方法 1：添加为非 Steam 游戏

1. 打开 Steam
2. 点击"添加游戏" → "添加非 Steam 游戏"
3. 浏览到 AppImage 文件
4. 点击"添加"
5. 在 Steam 库中找到该应用

#### 方法 2：从终端运行

1. 连接到 SteamDeck
2. 运行 AppImage：
   ```bash
   ./steamdeck-galgame-1.0.0-x86_64.AppImage
   ```

#### 方法 3：创建启动脚本

```bash
#!/bin/bash
cd /path/to/appimage/directory
./steamdeck-galgame-1.0.0-x86_64.AppImage "$@"
```

然后在 Steam 中添加这个脚本。

## 🔍 文件内容

AppImage 包含以下内容：

```
steamdeck-galgame-1.0.0-x86_64.AppImage
├── AppRun                              # 启动脚本
├── app/
│   ├── src/                           # 应用源代码
│   ├── run.py                         # 主程序
│   ├── requirements.txt               # 依赖列表
│   ├── data/                          # 数据文件（图标等）
│   └── venv/                          # Python 虚拟环境
│       ├── bin/python3                # Python 可执行文件
│       ├── lib/python3.*/site-packages/ # 已安装的包
│       └── ...
├── usr/share/icons/                  # 应用图标
└── *.desktop                          # 应用菜单项
```

## 🔧 高级用法

### 自定义打包

可以通过编辑 `AppImageBuilder.yml` 或 `build_linux_package.sh` 来自定义打包：

#### 添加额外的系统库

```bash
# 在 AppDir 中添加库
mkdir -p AppDir/lib
cp /path/to/library.so AppDir/lib/
```

#### 减小文件大小

```bash
# 删除不必要的文件
find AppDir -name "*.pyc" -delete
find AppDir -name "*.pyo" -delete
find AppDir -name "__pycache__" -type d -exec rm -rf {} +
find AppDir -name "*.dist-info" -type d -exec rm -rf {} +
```

#### 添加版本检查和更新

AppImage 支持 zsync 增量更新。编辑 `AppImageBuilder.yml`：

```yaml
AppImage:
  update-information: gh-releases-zsync|username|repo|latest|*.AppImage.zsync
```

## 🐛 故障排除

### AppImage 无法运行

```bash
# 确保 FUSE 已安装
sudo apt-get install libfuse2  # Ubuntu/Debian
sudo dnf install fuse          # Fedora

# 或者使用 --appimage-extract 模式
./steamdeck-galgame-1.0.0-x86_64.AppImage --appimage-extract
./squashfs-root/AppRun
```

### Python 依赖缺失

```bash
# 确保所有依赖都已安装
./steamdeck-galgame-1.0.0-x86_64.AppImage --help

# 如果有错误，检查虚拟环境
AppDir/app/venv/bin/pip list
```

### 权限问题

在 SteamDeck 上，可能需要特殊权限：

```bash
# 如果需要 sudo 权限运行
sudo ./steamdeck-galgame-1.0.0-x86_64.AppImage

# 或配置 sudoers
sudo visudo
# 添加一行: user ALL=(ALL) NOPASSWD: /path/to/steamdeck-galgame-1.0.0-x86_64.AppImage
```

## 📊 兼容性

### 支持的 Linux 发行版

| 发行版 | 版本 | 状态 |
|------|------|------|
| Ubuntu | 18.04+ | ✅ 支持 |
| Debian | 10+ | ✅ 支持 |
| Fedora | 30+ | ✅ 支持 |
| RHEL | 8+ | ✅ 支持 |
| Arch | 最新 | ✅ 支持 |
| SteamOS | 3.0+ | ✅ 支持 |
| Linux Mint | 19+ | ✅ 支持 |
| Elementary OS | 5+ | ✅ 支持 |
| openSUSE | Leap 15+ | ✅ 支持 |

### 系统要求

- **架构**: x86_64（64位）
- **glibc**: 2.29+ 或兼容版本
- **FUSE**: 2.x 或 3.x（可选，可使用提取模式）
- **磁盘空间**: 至少 200 MB（解压后约 150-200 MB）

## 📚 参考资源

- [AppImage 官方文档](https://docs.appimage.org/)
- [AppImage 规范](https://appimage.org/)
- [linuxdeploy](https://github.com/linuxdeploy/linuxdeploy)
- [AppImageKit](https://github.com/AppImage/AppImageKit)

## 🎯 下一步

1. **运行打包脚本**：
   ```bash
   ./build_linux_package.sh
   ```

2. **测试 AppImage**：
   ```bash
   ./dist/steamdeck-galgame-1.0.0-x86_64.AppImage
   ```

3. **上传到 GitHub Release**（可选）

4. **在 SteamDeck 中测试**

---

**版本**: 1.0.0  
**最后更新**: 2026-01-31  
**作者**: SteamDeck GAL Config 项目
