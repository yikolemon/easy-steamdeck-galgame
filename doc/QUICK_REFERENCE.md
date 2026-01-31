# 🚀 Quick Reference - Debug/Release Builds

## 本地构建

```bash
# Release 版本（推荐分发）
./build_pyinstaller.sh release

# Debug 版本（用于故障排查）
./build_pyinstaller.sh debug

# 同时构建两个版本
./build_pyinstaller.sh all
```

## 输出文件

```
dist/
├── steamdeck-galgame-release      # 生产版本（INFO 日志）
└── steamdeck-galgame-debug        # 开发版本（DEBUG 日志）
```

## GitHub Actions

- ✅ 自动在两个模式下构建
- ✅ 创建标签时自动发布到 Release 页面
- ✅ 两个版本都可在 Release 中下载

## 环境变量

```bash
# 设置构建类型（应用程序级别）
export BUILD_TYPE=debug    # 启用 DEBUG 日志
export BUILD_TYPE=release  # 启用 INFO 日志（默认）
```

## 在 SteamDeck 上运行

```bash
# Release - 日常使用（推荐）
./steamdeck-galgame-release

# Debug - 查看详细日志
./steamdeck-galgame-debug
```

## 文件差异

| 方面 | Release | Debug |
|------|---------|-------|
| 日志级别 | INFO | DEBUG |
| 输出详细度 | 最少 | 完整 |
| 性能 | 最优 | 略低 |
| 文件名 | `-release` | `-debug` |
| 推荐用途 | 日常使用 | 故障排查 |

---

💡 **Tip**: 如遇问题，使用 debug 版本获取详细信息！
