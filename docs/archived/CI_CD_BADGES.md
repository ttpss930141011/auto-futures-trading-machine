# CI/CD Badges Setup Guide

本項目使用 GitHub Actions 自動生成 test coverage 和 pylint 分數的 badges。

## 🎯 Badges 概覽

我們的項目包含以下 badges：

- **Coverage Badge**: 顯示測試覆蓋率百分比
- **Pylint Badge**: 顯示代碼品質分數 (只檢查 Error 和 Warning)
- **CI Status Badge**: 顯示 GitHub Actions CI 狀態
- **Python Version Badge**: 顯示支援的 Python 版本
- **License Badge**: 顯示項目授權

## 📊 Badge 分數標準

### Pylint 分數顏色：
- 🟢 **9.0+ / 10**: Bright Green (優秀)
- 🟢 **8.0+ / 10**: Green (良好)
- 🟡 **7.0+ / 10**: Yellow Green (尚可)
- 🟡 **6.0+ / 10**: Yellow (需改善)
- 🟠 **5.0+ / 10**: Orange (差)
- 🔴 **< 5.0 / 10**: Red (非常差)

### Coverage 百分比顏色：
- 🟢 **90%+**: Bright Green (優秀)
- 🟢 **80%+**: Green (良好)
- 🟡 **70%+**: Yellow Green (尚可)
- 🟡 **60%+**: Yellow (需改善)
- 🟠 **50%+**: Orange (差)
- 🔴 **< 50%**: Red (非常差)

## 🔧 本地測試

要在本地生成 badges：

```bash
# 安裝依賴
poetry install --with dev

# 生成 badges
poetry run python scripts/generate_badges.py
```

這會在 `.github/badges/` 目錄下生成：
- `pylint.json` - Pylint 分數 badge 數據
- `coverage.json` - Coverage 百分比 badge 數據

## 🚀 GitHub Actions Workflows

### 主要 CI Workflow (`.github/workflows/ci.yml`)
- 在每次 push 和 pull request 時觸發
- 運行測試並生成 coverage 報告
- 運行 pylint 檢查
- 生成並更新 badge 文件

### Badge 更新 Workflow (`.github/workflows/badges.yml`)
- 專門用於更新 badges
- 可手動觸發或每週日自動執行
- 使用 `scripts/generate_badges.py` 腳本

## 📝 Badge URLs

在 README.md 中使用的 badge URLs：

```markdown
<!-- Coverage Badge -->
![Coverage](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/ttpss930141011/auto-futures-trading-machine/refactor-exchange-api-service-container/.github/badges/coverage.json)

<!-- Pylint Badge -->
![Pylint](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/ttpss930141011/auto-futures-trading-machine/refactor-exchange-api-service-container/.github/badges/pylint.json)

<!-- CI Status Badge -->
![CI Status](https://github.com/ttpss930141011/auto-futures-trading-machine/workflows/CI/badge.svg)
```

## 🛠️ 配置文件

### Coverage 配置
- `.coveragerc` - 傳統 coverage 配置
- `pyproject.toml` - 現代化配置 (tool.coverage 部分)

### Pytest 配置
- `pytest.ini` - Pytest 基本配置
- `pyproject.toml` - 可選的 pytest 配置位置

## 🔄 自動更新機制

Badges 會在以下情況自動更新：
1. 每次 push 到主要分支 (main, develop, refactor-exchange-api-service-container)
2. 每週日自動執行
3. 手動觸發 "Update Badges" workflow

## 🎨 自訂化

要修改 badge 顏色閾值，編輯 `scripts/generate_badges.py` 中的 `get_color()` 函數。

要添加新的 badges，可以：
1. 修改 `generate_badges.py` 腳本
2. 更新 GitHub Actions workflows
3. 在 README.md 中添加新的 badge URLs

## 📚 參考資源

- [Shields.io](https://shields.io/) - Badge 服務
- [Coverage.py](https://coverage.readthedocs.io/) - Python coverage 工具
- [Pylint](https://pylint.pycqa.org/) - Python code analysis
- [GitHub Actions](https://docs.github.com/en/actions) - CI/CD 平台