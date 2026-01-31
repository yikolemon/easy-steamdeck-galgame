.PHONY: help run test install-dev clean lint format flatpak-build flatpak-install

help:
	@echo "SteamDeck GAL Game - 中文环境配置工具"
	@echo ""
	@echo "可用命令："
	@echo "  make run             - 运行应用"
	@echo "  make test            - 运行测试"
	@echo "  make test-ui         - 运行 UI 测试（需要显示器）"
	@echo "  make lint            - 代码检查"
	@echo "  make format          - 代码格式化"
	@echo "  make install-dev     - 安装开发依赖"
	@echo "  make clean           - 清理临时文件"
	@echo "  make docs            - 生成文档"
	@echo ""
	@echo "Flatpak 相关："
	@echo "  make flatpak-build   - 构建 Flatpak 安装包"
	@echo "  make flatpak-install - 安装构建的 Flatpak"
	@echo "  make flatpak-clean   - 清理 Flatpak 构建文件"

run:
	python3 run.py

test:
	python3 tests/test_logic.py

test-ui:
	python3 -m pytest tests/ -v

install-dev:
	pip install -r requirements-dev.txt

lint:
	@echo "检查代码质量..."
	@which flake8 > /dev/null && flake8 src tests || echo "需要: pip install flake8"
	@which mypy > /dev/null && mypy src || echo "需要: pip install mypy"

format:
	@echo "格式化代码..."
	@which black > /dev/null && black src tests || echo "需要: pip install black"
	@which isort > /dev/null && isort src tests || echo "需要: pip install isort"

clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	rm -rf dist/ build/ *.egg-info/
	rm -rf .pytest_cache/ .mypy_cache/
	rm -rf htmlcov/ .coverage

docs:
	@echo "项目文档已在 STRUCTURE.md 中"
	@echo "查看: README.md 和 STRUCTURE.md"

flatpak-build:
	@echo "🔨 构建 Flatpak 安装包..."
	@bash build-flatpak.sh

flatpak-install: flatpak-build
	@echo "📦 安装 Flatpak..."
	@if [ -f io.github.steamdeck_galgame.flatpak ]; then \
		flatpak install io.github.steamdeck_galgame.flatpak; \
	else \
		echo "❌ Flatpak 文件不存在"; \
	fi

flatpak-clean:
	rm -rf flatpak-build flatpak-repo
	rm -f io.github.steamdeck_galgame.flatpak build-metadata.json
	@echo "✅ Flatpak 构建文件已清理"

