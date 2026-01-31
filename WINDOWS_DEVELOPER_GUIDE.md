# Windows 开发者快速指南

> 专为 Windows 开发环境设计的快速上手指南

## 🎯 核心优势

现在你可以完全在 Windows 上开发，**无需 Linux 环境**！

✅ 所有代码在 Windows 编辑和测试  
✅ 推送代码自动在 GitHub Actions (Linux) 上打包  
✅ AppImage 自动生成和发布  
✅ 零 Linux 知识要求  

---

## 🚀 快速开始（5 分钟）

### 1. 首次开发环境设置

```bash
# 1. 克隆项目
git clone https://github.com/YOUR_USERNAME/steamdeck-galgame.git
cd steamdeck-galgame

# 2. 创建虚拟环境
python -m venv venv
venv\Scripts\activate

# 3. 安装依赖
pip install -r requirements.txt

# 完成！
```

### 2. 日常开发流程

```bash
# 开发代码...
# 编辑文件

# 测试本地功能
python run.py          # 测试 TUI
python run.py --gui    # 测试 GUI

# 提交更改
git add .
git commit -m "feature: xxx"
git push origin master
```

### 3. 发布新版本

```bash
# 1. 创建版本标签
git tag -a v1.1.0 -m "Release v1.1.0 - Add TUI and Linux packaging"

# 2. 推送标签
git push origin v1.1.0

# 3. 等待... ☕
# GitHub Actions 会自动：
#   ✓ 在 Linux 上构建 AppImage
#   ✓ 生成 tar.gz
#   ✓ 创建 GitHub Release
#   ✓ 上传文件

# 4. 检查 Release
# 在 GitHub Releases 页面查看：
# https://github.com/YOUR_USERNAME/steamdeck-galgame/releases
```

---

## 📋 完整开发工作流

### 开发阶段

```bash
# 1. 获取最新代码
git pull origin master

# 2. 创建功能分支（可选）
git checkout -b feature/new-feature

# 3. 编辑文件
# ... 在 IDE 中编辑 ...

# 4. 测试功能
python test_import.py      # 检查导入
python test_all.py         # 运行所有测试
python run.py              # 测试 TUI
python run.py --gui        # 测试 GUI
```

### 提交和推送

```bash
# 1. 查看变更
git status

# 2. 添加更改
git add .

# 3. 提交更改
git commit -m "feat: 新功能说明"

# 4. 推送到 GitHub
git push origin master
# 或推送到功能分支
git push origin feature/new-feature
```

### 创建发布版本

```bash
# 1. 确保代码在 master
git checkout master
git pull origin master

# 2. 创建标签
git tag -a v1.2.0 -m "Release v1.2.0 description"

# 3. 推送标签
git push origin v1.2.0

# 4. 监控构建
# → GitHub 网页 → Actions 标签页

# 5. 发布完成
# → GitHub 网页 → Releases 标签页 → 找到新版本
```

---

## 🛠️ 常见任务

### 修复 Bug

```bash
# 1. 创建 bug fix 分支
git checkout -b fix/bug-description

# 2. 修改代码

# 3. 测试修复
python test_all.py

# 4. 提交修复
git add .
git commit -m "fix: bug description"
git push origin fix/bug-description

# 5. 创建 Pull Request（在 GitHub 网页）
# → Pull requests → New pull request
# → 选择 fix/bug-description 到 master
```

### 添加新功能

```bash
# 1. 创建功能分支
git checkout -b feature/feature-name

# 2. 编写代码（参考 TUI_IMPLEMENTATION.md）

# 3. 添加测试

# 4. 提交更改
git add .
git commit -m "feat: feature description"
git push origin feature/feature-name

# 5. 创建 Pull Request 待审查
```

### 回滚更改

```bash
# 1. 查看历史
git log --oneline

# 2. 回滚最后一次提交（未推送）
git reset --soft HEAD~1

# 3. 回滚已推送的提交
git revert HEAD
git push origin master
```

---

## 📊 环境要求

### Windows

✅ Windows 10/11  
✅ Git for Windows  
✅ Python 3.7+  
✅ 文本编辑器或 IDE（VSCode、PyCharm 等）  

### 安装检查

```bash
# 检查 Python
python --version
# 应该显示：Python 3.7.x 或更新

# 检查 Git
git --version
# 应该显示：git version 2.x.x

# 安装虚拟环境
python -m venv --help
# 应该显示帮助信息
```

---

## 🔐 安全提示

### 不要提交的文件

这些文件应该在 `.gitignore` 中（已配置）：

```
venv/
__pycache__/
*.pyc
.env
*.egg-info/
dist/
build/
```

验证：
```bash
# 查看 .gitignore
cat .gitignore
```

### 敏感信息

如果涉及 API 密钥、密码等：

```bash
# 1. 永远不要提交到 git
# 2. 使用环境变量
# 3. 在 README 中说明配置方式
```

---

## 📡 GitHub Actions 自动构建

### 工作流说明

| 文件 | 触发 | 功能 |
|------|------|------|
| `build.yml` | 标签推送或 master 推送 | 构建 AppImage 和发布 |
| `test.yml` | PR 或 master 推送 | 运行测试 |
| `ci.yml` | 各种事件 | 持续集成 |

### 监控构建

1. **推送代码**
   ```bash
   git push origin v1.1.0
   ```

2. **打开 GitHub 网页**
   - 进入项目 → Actions 标签
   - 查看 "Build and Release" 工作流
   - 实时查看进度

3. **构建完成**
   - 工作流显示 ✅
   - 进入 Releases 标签查看新版本
   - 下载 AppImage 或 tar.gz

### 常见问题

**Q: 构建失败了怎么办？**
- 点击失败的工作流查看日志
- 搜索 "Error" 找到错误信息
- 常见原因：依赖缺失、文件权限问题

**Q: 如何重新构建？**
- 删除标签：`git push origin --delete v1.1.0`
- 重新创建：`git tag -a v1.1.0 -m "..."`
- 重新推送：`git push origin v1.1.0`

**Q: 多久完成？**
- 通常 5-10 分钟
- 下载 appimagetool 可能需要 1-2 分钟

---

## 📚 文档导航

| 文档 | 内容 |
|------|------|
| `README.md` | 项目概述 |
| `GITHUB_ACTIONS_GUIDE.md` | Actions 详细指南 |
| `TUI_USAGE.md` | TUI 使用说明 |
| `TUI_IMPLEMENTATION.md` | TUI 开发指南 |
| `LINUX_PACKAGING.md` | 打包详细说明 |
| `NEXT_STEPS.md` | 后续工作建议 |

---

## 🎓 学习资源

### Git 教程

- [Git 官方文档](https://git-scm.com/doc)
- [GitHub 官方指南](https://docs.github.com)

### Python 教程

- [Python 官方文档](https://docs.python.org/3/)
- [Rich 库文档](https://rich.readthedocs.io/)

### GitHub Actions 教程

- [GitHub Actions 官方文档](https://docs.github.com/en/actions)
- [Actions 最佳实践](https://github.com/actions)

---

## 💬 获取帮助

### 调试 Python 错误

```bash
# 1. 运行代码看错误
python run.py

# 2. 搜索错误信息
# Google: python ImportError: No module named 'xxx'

# 3. 检查依赖
pip list
pip install -r requirements.txt

# 4. 重新创建虚拟环境
deactivate
rmdir venv  # Windows
rm -rf venv # Linux/Mac
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

### 调试 Git 错误

```bash
# 1. 查看状态
git status

# 2. 查看日志
git log --oneline -10

# 3. 查看远程
git remote -v
```

### 查看 Actions 日志

1. GitHub 网页 → Actions 标签
2. 找到失败的工作流
3. 点击步骤查看详细日志

---

## 🎯 推荐工作流

### 每天的开发

```bash
# 早上
git pull origin master
# 编写代码

# 中途
python run.py
python run.py --gui

# 提交
git add .
git commit -m "wip: 功能进行中"
git push origin master

# 或者创建功能分支
git checkout -b feature/xxx
git add .
git commit -m "feat: xxx"
git push origin feature/xxx
```

### 发布周期

```bash
# 每周/月发布一次
git checkout master
git pull origin master

# 确保所有测试通过
python test_all.py

# 创建 Release
git tag -a v1.x.y -m "Release v1.x.y - description"
git push origin v1.x.y

# 等待自动构建和发布
```

---

## ✅ 快速检查清单

发布前检查：

- [ ] 代码在 Windows 上测试通过
  ```bash
  python run.py
  python run.py --gui
  python test_all.py
  ```

- [ ] 所有更改已提交
  ```bash
  git status  # 应该显示 "nothing to commit"
  ```

- [ ] 标签名称正确（v 开头）
  ```bash
  git tag -l
  ```

- [ ] 推送代码
  ```bash
  git push origin master
  git push origin v1.x.y
  ```

- [ ] 监控 Actions
  - GitHub Actions 标签页查看进度

- [ ] 验证 Release
  - GitHub Releases 标签页查看文件

---

## 🚀 快速命令参考

```bash
# 开发
python run.py
python test_all.py

# 提交
git add .
git commit -m "message"
git push origin master

# 发布
git tag -a v1.1.0 -m "message"
git push origin v1.1.0

# 查询
git status
git log --oneline -5
git tag -l
```

---

## 🎉 恭喜！

现在你拥有完整的开发到发布工作流：

1. ✅ 在 Windows 上开发
2. ✅ 本地测试功能
3. ✅ Git 推送代码
4. ✅ GitHub Actions 自动打包
5. ✅ 自动创建 Release
6. ✅ 用户下载 AppImage

**零 Linux 操作，零 AppImage 手动构建！** 🎊

---

**版本**：v1.0  
**更新日期**：2026-01-31  
**适用于**：Windows 10/11 开发者
