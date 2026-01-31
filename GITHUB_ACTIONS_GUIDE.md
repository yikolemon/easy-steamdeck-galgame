# GitHub Actions 自动打包指南

## 概述

本项目已配置 GitHub Actions 自动打包工作流，支持以下功能：

- ✅ **自动打包**：推送代码时自动构建
- ✅ **自动发布**：标签 push 时自动创建 Release
- ✅ **自动测试**：PR 和 push 时运行测试
- ✅ **构建产物保存**：30 天内保留构建输出

---

## 工作流说明

### 1. `build.yml` - 主打包流程

**触发条件**：
- 推送 `v*` 标签时（例如 `v1.1.0`）
- 推送到 `master` 分支时
- 手动触发（workflow_dispatch）

**输出**：
- `dist/steamdeck-galgame-*-x86_64.AppImage` - AppImage 可执行文件
- `dist/steamdeck-galgame-*.tar.gz` - 源代码压缩包
- `RELEASE_NOTES.md` - 自动生成的发布说明

**工作步骤**：
1. ✅ 检出代码
2. ✅ 设置 Python 3.10
3. ✅ 安装系统依赖
4. ✅ 下载 appimagetool
5. ✅ 测试导入和打包准备
6. ✅ 构建 AppImage
7. ✅ 自动创建 Release（如果是标签推送）
8. ✅ 上传构建产物（30 天）

### 2. `test.yml` - 测试流程

**触发条件**：
- PR 到 `master` 分支
- 推送到 `master` 分支

**执行内容**：
- 检查 Python 语法
- 测试模块导入
- 运行单元测试
- 验证打包准备状态

---

## 📋 使用方法

### 方式 1: 自动发布（推荐）

1. **本地创建标签**
   ```bash
   git tag -a v1.1.0 -m "Release v1.1.0 with AppImage packaging"
   ```

2. **推送标签到 GitHub**
   ```bash
   git push origin v1.1.0
   ```

3. **等待 GitHub Actions 完成**
   - 访问 GitHub → Actions 标签页查看进度
   - 等待工作流完成（通常 5-10 分钟）

4. **自动创建 Release**
   - Release 自动创建在 https://github.com/YOUR_REPO/releases
   - AppImage 和 tar.gz 自动上传

### 方式 2: 手动触发构建

1. **访问 GitHub 网页界面**
   - 进入 Actions 标签
   - 找到 "Build and Release" 工作流
   - 点击 "Run workflow"

2. **选择分支**（默认 master）

3. **启动构建**
   - 点击绿色的 "Run workflow" 按钮

### 方式 3: 推送代码时自动构建

每次推送到 `master` 都会自动构建：

```bash
git push origin master
```

构建产物会上传到 Artifacts（可下载 30 天）。

---

## 🔍 监控构建进度

### 1. 在 GitHub 网页查看

1. 进入项目页面
2. 点击 "Actions" 标签
3. 选择最新的工作流运行
4. 实时查看执行进度

### 2. 查看日志

- 点击任何步骤查看详细日志
- 搜索 "Error" 或 "Warning" 快速定位问题

### 3. 下载构建产物

- 工作流完成后，点击 "Artifacts"
- 下载 `build-output` 文件夹
- 包含 AppImage 和 Release Notes

---

## 📦 Release 文件说明

### AppImage 文件

**文件名**：`steamdeck-galgame-VERSION-x86_64.AppImage`

**大小**：~100-150 MB

**特点**：
- ✅ 单文件可执行
- ✅ 无需安装依赖
- ✅ 包含完整 Python 环境
- ✅ 跨 Linux 发行版兼容

**使用**：
```bash
# 下载后
chmod +x steamdeck-galgame-1.1.0-x86_64.AppImage
./steamdeck-galgame-1.1.0-x86_64.AppImage
```

### tar.gz 文件

**文件名**：`steamdeck-galgame-VERSION.tar.gz`

**大小**：~10-20 MB

**特点**：
- ✅ 源代码压缩包
- ✅ 体积小
- ✅ 可在任何环境解压

**使用**：
```bash
tar -xzf steamdeck-galgame-1.1.0.tar.gz
cd steamdeck-galgame-1.1.0
pip install -r requirements.txt
python3 run.py
```

---

## ⚙️ 配置详情

### 环境

- **操作系统**：Ubuntu Latest
- **Python 版本**：3.10
- **构建时间**：约 5-10 分钟

### 安装的系统依赖

```
build-essential       # C 编译工具
python3-dev          # Python 开发文件
python3-venv         # Python 虚拟环境
libfuse2             # AppImage 运行时
desktop-file-utils   # .desktop 文件验证
appstream            # 应用元数据验证
squashfs-tools       # 压缩工具
```

### Python 依赖

从 `requirements.txt` 自动安装：
- `requests>=2.25.0` - HTTP 库
- `rich>=10.0.0` - TUI 美化库

---

## 🐛 故障排除

### Issue 1: AppImage 构建失败

**症状**：
```
Error: appimagetool not found
```

**解决**：
- 检查网络连接
- 查看 "Download appimagetool" 步骤的日志
- AppImage 下载通常需要 1-2 分钟

### Issue 2: 打包检查失败

**症状**：
```
Error: Missing required files
```

**解决**：
- 确保 `src/` 目录结构完整
- 检查 `build_linux_package.sh` 脚本权限
- 重新 push 代码触发重建

### Issue 3: 模块导入错误

**症状**：
```
ModuleNotFoundError: No module named 'xxx'
```

**解决**：
- 检查 `requirements.txt` 是否完整
- 确保所有新依赖都已添加
- 本地运行 `python test_import.py` 验证

### Issue 4: Release 未自动创建

**症状**：
- 标签推送了但没有创建 Release

**解决**：
1. 确保标签名称是 `v*` 格式（例如 `v1.1.0`）
2. 检查工作流日志是否有权限错误
3. 手动创建 Release 并上传文件

---

## 📊 构建历史查询

### 查看所有构建

```bash
# 在项目根目录运行
git log --oneline --all --grep="GitHub Actions"
```

### 查看特定版本的构建

访问 GitHub Release 页面：
```
https://github.com/YOUR_USERNAME/steamdeck-galgame/releases
```

### 下载历史版本

1. 访问 Release 页面
2. 找到需要的版本
3. 下载对应的 AppImage 或 tar.gz

---

## 🚀 最佳实践

### 1. 版本号管理

使用 semantic versioning：
```bash
git tag -a v1.0.0 -m "Initial release"
git tag -a v1.1.0 -m "Add TUI support"
git tag -a v1.1.1 -m "Bug fix"
git push origin --tags
```

### 2. Release Notes

自动生成的 Release Notes 包含：
- 功能说明
- 安装方式
- 使用说明

可在 GitHub Release 页面编辑添加更多内容。

### 3. 定期测试

每次推送前在本地测试：
```bash
python3 run.py          # 测试 TUI
python3 run.py --gui    # 测试 GUI
python test_all.py      # 运行测试
bash check_packaging.sh # 检查打包
```

### 4. 监控构建

设置 GitHub 通知：
- 访问 Settings → Notifications
- 启用 "Workflow runs" 通知
- 构建完成时会收到邮件通知

---

## 🔐 安全性

### GitHub Token

- 使用 `secrets.GITHUB_TOKEN` 自动获取
- 仅在官方 Action 中使用
- 自动包含必要的权限

### 代码安全

- 所有代码在 GitHub 的沙箱环境中执行
- 不存储任何敏感信息
- Release 文件公开但可版本控制

---

## 💡 扩展功能

### 1. 添加 Docker 支持

可以添加工作流自动构建 Docker 镜像：
```yaml
- name: Build Docker image
  run: docker build -t steamdeck-galgame .
```

### 2. 上传到其他平台

可以添加工作流上传到：
- Itch.io
- Flathub
- AUR (Arch Linux)

### 3. 性能测试

可以添加工作流运行性能测试：
```yaml
- name: Run performance tests
  run: python -m pytest tests/performance/
```

### 4. 代码覆盖率

可以添加工作流生成覆盖率报告：
```yaml
- name: Generate coverage
  run: coverage run -m pytest
```

---

## 📞 快速命令参考

```bash
# 创建版本标签
git tag -a v1.1.0 -m "Release message"

# 推送标签（触发打包）
git push origin v1.1.0

# 推送所有标签
git push origin --tags

# 查看本地标签
git tag -l

# 删除本地标签
git tag -d v1.1.0

# 删除远程标签
git push origin --delete v1.1.0

# 查看标签详情
git show v1.1.0
```

---

## 📈 预期效果

### 首次运行

1. ✅ Actions 自动执行
2. ✅ 生成 AppImage（~150 MB）
3. ✅ 生成 tar.gz（~15 MB）
4. ✅ 自动创建 Release
5. ✅ 文件自动上传

### 后续使用

每次标签推送都会自动重复上述过程，无需手动操作。

---

## 🎯 下一步

1. **推送代码** - 当前更改已包含工作流配置
   ```bash
   git push origin master
   ```

2. **创建第一个 Release**
   ```bash
   git tag -a v1.1.0 -m "Complete TUI and Linux packaging"
   git push origin v1.1.0
   ```

3. **监控构建** - 在 GitHub Actions 页面查看进度

4. **验证 Release** - 在 Releases 页面下载文件验证

---

**版本**：v1.0  
**最后更新**：2026-01-31  
**状态**：✅ 完整配置，生产就绪
