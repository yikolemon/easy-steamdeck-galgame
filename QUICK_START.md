# ⚡ 快速开始指南（1 分钟版）

> 你在 Windows 开发，GitHub Actions 自动打包！

## 3 步发布流程

### 1️⃣ 开发代码（在 Windows）
```bash
python run.py
python test_all.py
git add .
git commit -m "feat: your feature"
git push origin master
```

### 2️⃣ 创建版本（标签）
```bash
git tag -a v1.1.0 -m "Release v1.1.0"
git push origin v1.1.0
```

### 3️⃣ 等待自动完成 ☕
- GitHub Actions 自动构建
- 自动生成 AppImage + tar.gz
- 自动创建 Release
- 5-10 分钟完成

## 查看结果
- GitHub → Releases → 下载 AppImage 或 tar.gz

---

## 常用命令

```bash
# 查看状态
git status

# 查看历史
git log --oneline -5

# 推送代码
git push origin master

# 查看标签
git tag -l

# 删除标签（需要重建时）
git tag -d v1.1.0
git push origin --delete v1.1.0
```

---

## 工作流文件位置

- `.github/workflows/build.yml` - 主打包工作流
- `.github/workflows/test.yml` - 测试工作流

## 详细文档

- `WINDOWS_DEVELOPER_GUIDE.md` - Windows 完整指南
- `GITHUB_ACTIONS_GUIDE.md` - GitHub Actions 详细说明
- `README_CN.md` - 简体中文项目说明

---

**就这么简单！**
