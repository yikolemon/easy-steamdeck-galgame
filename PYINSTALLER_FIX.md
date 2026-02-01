# PyInstaller Rich Unicode 问题修复

## 问题描述
打包后的可执行文件在 SteamDeck 上运行时出现错误：
```
错误: 无法导入 TUI 模块: No module named 'rich._unicode_data.unicode17-0-0'
```

## 根本原因
PyInstaller 在打包 `rich` 库时，没有正确收集 Unicode 数据文件 (`rich._unicode_data`)，导致 TUI 界面无法正常渲染中文字符。

## 解决方案

### 1. 修改 `steamdeck_galgame.spec`

在 **第 27 行** 添加了显式的 Unicode 数据收集：
```python
# Collect rich unicode data specifically (required for TUI rendering)
datas += collect_data_files('rich._unicode_data')
```

在 **第 43-44 行** 的 `hiddenimports` 中添加：
```python
'rich._unicode_data',
'rich._unicode_data.unicode17-0-0',
```

### 2. 修改 `.github/workflows/build-pyinstaller.yml`

在 **第 42 行** 添加了强制重装 `rich` 的步骤：
```yaml
# 确保 rich 及其所有数据文件都已正确安装
pip install --upgrade --force-reinstall rich
```

## 修改后的完整配置

### steamdeck_galgame.spec (关键部分)
```python
datas = []

# Collect requests data files
datas += collect_data_files('requests')
# Collect rich data files (important for unicode/styling)
datas += collect_data_files('rich')
# Collect rich unicode data specifically (required for TUI rendering)
datas += collect_data_files('rich._unicode_data')

a = Analysis(
    ['run.py'],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=[
        'src',
        'src.tui',
        'src.core',
        'src.core.downloader',
        'src.core.installers',
        'src.utils',
        'requests',
        'rich',
        'rich._unicode_data',
        'rich._unicode_data.unicode17-0-0',
    ],
    # ...
)
```

### GitHub Actions (关键部分)
```yaml
- name: Install Python dependencies
  run: |
    python -m pip install --upgrade pip
    pip install -r requirements.txt
    pip install pyinstaller
    # 确保 rich 及其所有数据文件都已正确安装
    pip install --upgrade --force-reinstall rich
```

## 验证

推送代码后，GitHub Actions 会自动构建新的可执行文件。下载后在 SteamDeck 上测试：

```bash
chmod +x steamdeck-galgame-release
./steamdeck-galgame-release
```

应该能够正常显示 TUI 界面和中文字符，不再出现 Unicode 模块缺失的错误。

## 相关文件
- `steamdeck_galgame.spec` - PyInstaller 打包配置
- `.github/workflows/build-pyinstaller.yml` - GitHub Actions 构建配置

## 技术细节
- **rich 版本**: >= 10.0.0
- **Python 版本**: 3.10
- **PyInstaller**: 最新版本
- **目标平台**: Linux (SteamDeck)
