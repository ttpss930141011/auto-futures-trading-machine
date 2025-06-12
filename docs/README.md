# 📚 文檔目錄

## 🎯 主要文檔 (專案根目錄)

### 🏛️ 系統架構
- **[ARCHITECTURE.md](../ARCHITECTURE.md)** - 完整系統概述與視覺圖表
- **[CLAUDE.md](../CLAUDE.md)** - 開發者指令與基本指令

### 📖 快速開始
- **[README.md](../README.md)** - 專案概述與學習路徑

---

## 📁 docs/ 資料夾結構

### 🏗️ architecture/
系統架構相關的詳細文檔

- **[DETAILED_FLOW_DIAGRAMS.md](architecture/DETAILED_FLOW_DIAGRAMS.md)** - 詳細流程圖與時序圖
- **[CLASS_DESIGN_GUIDE.md](architecture/CLASS_DESIGN_GUIDE.md)** - 類別設計指南與 SOLID 原則

### 📋 guides/
使用指南和操作手冊

- **[ALLINONE_CONTROLLER_GUIDE.md](guides/ALLINONE_CONTROLLER_GUIDE.md)** - AllInOneController 啟動流程詳解

### 🔧 technical/
技術深度解析

- **[WHY_ZEROMQ.md](technical/WHY_ZEROMQ.md)** - ZeroMQ 選擇理由與消息模式
- **[HFT_CONCEPTS.md](technical/HFT_CONCEPTS.md)** - 高頻交易概念應用
- **[PROCESS_COMMUNICATION.md](technical/PROCESS_COMMUNICATION.md)** - 進程間通信模式

### 🚀 getting-started/
新手入門教程

- **[INSTALLATION.md](getting-started/INSTALLATION.md)** - 詳細安裝指南
- **[QUICK_START.md](getting-started/QUICK_START.md)** - 5分鐘快速開始
- **[FIRST_TRADE.md](getting-started/FIRST_TRADE.md)** - 第一筆自動交易教程

### 📊 guides/
進階使用指南

- **[BACKTESTING.md](guides/BACKTESTING.md)** - 回測系統指南
- **[MONITORING.md](guides/MONITORING.md)** - 系統監控配置

### 📚 stories/
開發故事與決策過程

- **[DESIGN_DECISIONS.md](stories/DESIGN_DECISIONS.md)** - 重要設計決策記錄
- **[LESSONS_LEARNED.md](stories/LESSONS_LEARNED.md)** - 開發過程經驗總結

### 🗺️ decisions/
架構決策記錄 (ADR)

- **[001-use-zeromq-for-ipc.md](decisions/001-use-zeromq-for-ipc.md)** - 選擇 ZeroMQ 的決策
- **[004-dll-gateway-centralization.md](decisions/004-dll-gateway-centralization.md)** - DLL Gateway 集中化
- 其他 ADR 文檔...

### 🔧 api/
API 文檔

- **[README.md](api/README.md)** - 組件 API 概述

### 🗃️ archived/
歷史文檔存檔

- **已廢棄或過時的文檔** - 保留作為歷史參考，不應用於當前開發

---

## 🎓 推薦學習順序

### 🔰 新手開發者
1. [README.md](../README.md) - 了解專案概述
2. [ARCHITECTURE.md](../ARCHITECTURE.md) - 理解系統架構
3. [getting-started/INSTALLATION.md](getting-started/INSTALLATION.md) - 環境設置
4. [getting-started/QUICK_START.md](getting-started/QUICK_START.md) - 快速開始

### 👨‍💻 有經驗開發者
1. [ARCHITECTURE.md](../ARCHITECTURE.md) - 系統概述
2. [architecture/CLASS_DESIGN_GUIDE.md](architecture/CLASS_DESIGN_GUIDE.md) - 設計模式
3. [architecture/DETAILED_FLOW_DIAGRAMS.md](architecture/DETAILED_FLOW_DIAGRAMS.md) - 詳細流程
4. [guides/ALLINONE_CONTROLLER_GUIDE.md](guides/ALLINONE_CONTROLLER_GUIDE.md) - 啟動機制

### 🏗️ 架構設計者
1. [decisions/](decisions/) - 查看所有 ADR
2. [technical/WHY_ZEROMQ.md](technical/WHY_ZEROMQ.md) - 技術選型
3. [stories/DESIGN_DECISIONS.md](stories/DESIGN_DECISIONS.md) - 設計理念
4. [stories/LESSONS_LEARNED.md](stories/LESSONS_LEARNED.md) - 經驗總結

---

## ⚠️ 重要提醒

- **已歸檔文檔**: `archived/` 資料夾中的文檔已過時，請勿參考
- **文檔同步**: 修改代碼時請同步更新相關文檔
- **圖表格式**: 所有圖表使用 Mermaid 格式，便於維護和版本控制
- **超連結驗證**: 定期檢查文檔間的超連結是否有效

---

*最後更新: 2024年12月*