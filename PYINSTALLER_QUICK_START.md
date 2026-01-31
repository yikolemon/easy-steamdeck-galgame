# ⚡ PyInstaller 快速开始（3 分钟版）

## 核心概念

**PyInstaller** = Python 应用 → 单个可执行文件

**好处**：
- ✅ 用户无需安装 Python
- ✅ 用户无需 pip install
- ✅ 直接双击运行

---

## 三种分发方式对比

| 方式 | 文件 | 用户需要 | 易用性 |
|------|------|--------|-------|
| **PyInstaller** ⭐ | 单个可执行文件 | 无 | 最简单 |
| AppImage | 单个 .AppImage | 无 | 简单 |
| Python 脚本 | .py + requirements.txt | Python 3.7+ + pip | 复杂 |

---

## SteamDeck 上使用

### 方式 1: 最简单（推荐）

```bash
# 1. 下载可执行文件
# GitHub → Releases → steamdeck-galgame

# 2. 给予执行权限
chmod +x steamdeck-galgame

# 3. 运行
./steamdeck-galgame
```

### 方式 2: 放到应用菜单

```bash
# 1. 放到应用目录
mkdir -p ~/.local/share/applications

# 2. 创建快捷方式
cat > ~/.local/share/applications/steamdeck-galgame.desktop << 'EOF'
[Desktop Entry]
Version=1.0
Type=Application
Name=SteamDeck Galgame Config
Exec=/path/to/steamdeck-galgame
Terminal=true
