# SteamDeck 中文环境配置工具

🎮 为 SteamDeck 配置中文游戏环境的工具

通过这个工具，你可以：
- 为系统安装中文语言支持（locale）
- 为游戏安装中文字体
- 配置游戏中文启动环境

## 🚀 快速安装

### 通过 Flatpak 安装（推荐）

```bash
flatpak install flathub io.github.steamdeck_galgame
flatpak run io.github.steamdeck_galgame
```

### 或从源代码运行

```bash
python3 main.py
```

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
- Tkinter
- 100MB 磁盘空间

## 使用方法

### 第一步：安装 Locale
1. 打开工具
2. 点击"📝 中文 Locale"
3. 点击"▶ 执行"
4. 等待完成

### 第二步：安装字体
1. 点击"🔤 中文字体"
2. 选择字体包（GAL_Fonts_Minimal.zip）
3. 点击"▶ 执行"
4. 等待完成

### 第三步：配置游戏
1. 在 Steam 游戏属性中找到"启动选项"
2. 从工具复制中文启动命令
3. 粘贴到启动选项
4. 保存

## 许可证

MIT License

## 版本

v1.0.0
