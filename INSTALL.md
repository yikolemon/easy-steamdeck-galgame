# Flatpak 安装和使用指南

## 🚀 快速开始（2 步）

### 步骤 1：安装

在 SteamDeck 上打开 Konsole（终端），运行：

```bash
flatpak install flathub io.github.steamdeck_galgame
```

首次使用时会自动添加 Flathub 仓库。

### 步骤 2：运行

```bash
flatpak run io.github.steamdeck_galgame
```

或者在应用菜单中找 "SteamDeck GAL 中文环境配置"。

## 📋 功能使用

### 功能 1：安装中文 Locale

1. 打开工具
2. 点击"📝 中文 Locale"标签
3. 点击"▶ 执行"
4. 等待完成

⏱️ 耗时：1-2 分钟

### 功能 2：安装中文字体

1. 点击"🔤 中文字体"标签
2. 点击"📁 选择字体包"
3. 选择 `GAL_Fonts_Minimal.zip`
4. 点击"▶ 执行"
5. 等待完成

⏱️ 耗时：1-5 分钟（取决于字体数量）

**注意**：需要字体包 `GAL_Fonts_Minimal.zip` 与工具在同一目录

### 功能 3：配置游戏中文

1. 点击"🎮 游戏启动选项"标签
2. 点击"📋 复制命令"
3. 打开 Steam 游戏属性
4. 进入"启动选项"
5. 粘贴命令
6. 保存

完成后重启游戏即可使用中文。

## ⚙️ 系统要求

- SteamOS 3.0+
- Flatpak（通常已预装）
- 网络连接

## 🆘 故障排除

### 问题：Flatpak 未安装

SteamDeck 上通常已预装 Flatpak。如需安装：

```bash
sudo pacman -S flatpak
```

### 问题：字体不显示

1. 确保选择了正确的字体包
2. 重启 SteamDeck
3. 重新执行功能 2

### 问题：游戏仍是英文

检查：
- [ ] 功能 1 已执行
- [ ] 功能 2 已执行
- [ ] 游戏启动选项设置正确
- [ ] 游戏本身有中文本地化

## 🔄 更新

```bash
flatpak update io.github.steamdeck_galgame
```

## 🗑️ 卸载

```bash
flatpak remove io.github.steamdeck_galgame
```

**注意**：卸载工具不会移除已安装的 Locale 和字体。

## 💡 提示

- Locale 和字体只需安装一次，永久有效
- 每添加新游戏时，从功能 3 复制启动命令
- 工具界面完全中文化，易于使用

## 📞 需要帮助？

- 查看 README.md 了解详情
- 检查日志信息诊断问题

---

**祝你使用愉快！** 🎮🇨🇳

v1.0.0 | 2026-01-31
