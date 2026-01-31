# SteamDeck 中文环境配置工具 - 完整中文文档

🎮 为 SteamDeck 配置中文游戏环境  
✅ TUI + GUI 双界面 | 🐧 Linux AppImage 打包 | 🤖 GitHub Actions 自动构建

## 快速导航

- **[Windows 开发者快速开始](WINDOWS_DEVELOPER_GUIDE.md)** - 5分钟上手
- **[TUI 使用指南](TUI_USAGE.md)** - 如何使用界面
- **[GitHub Actions 自动构建](GITHUB_ACTIONS_GUIDE.md)** - 无需 Linux 打包

## 核心功能

✅ 中文 Locale 安装  
✅ 中文字体自动安装  
✅ 游戏启动配置  
✅ TUI 终端界面（无 GUI 依赖）  
✅ GUI 图形界面（可选）  
✅ Linux AppImage 打包  
✅ GitHub Actions 自动构建  

## 使用方式

### 方式 1: TUI（推荐 SteamDeck）
```bash
python3 run.py
```

### 方式 2: GUI
```bash
python3 run.py --gui
```

### 方式 3: AppImage（无需 Python）
```bash
chmod +x steamdeck-galgame-*.AppImage
./steamdeck-galgame-*.AppImage
```

## Windows 开发流程

1. **开发和测试**（在 Windows 上）
   ```bash
   python run.py
   python test_all.py
   git add .
   git commit -m "feat: xxx"
   git push origin master
   ```

2. **发布新版本**
   ```bash
   git tag -a v1.1.0 -m "Release message"
   git push origin v1.1.0
   ```

3. **自动完成**
   - GitHub Actions 自动构建 AppImage
   - 自动创建 Release
   - 自动上传文件

## 项目完成度

| 功能 | 状态 |
|------|------|
| TUI 应用 | ✅ 完成 |
| GUI 应用 | ✅ 完成 |
| AppImage 打包 | ✅ 完成 |
| GitHub Actions | ✅ 完成 |
| 文档 | ✅ 完善 |

## 关键文件

- `WINDOWS_DEVELOPER_GUIDE.md` - Windows 开发者指南
- `GITHUB_ACTIONS_GUIDE.md` - GitHub Actions 详细说明
- `TUI_USAGE.md` - TUI 使用指南
- `LINUX_PACKAGING.md` - Linux 打包指南
- `PROJECT_STATUS.md` - 项目状态报告
- `NEXT_STEPS.md` - 后续工作建议

## 版本

v1.1.0 | ✅ 生产就绪 | 2026-01-31
