# GUI Implementation Plan

## 📋 概述

此文檔概述了將現有 CLI 界面轉換為 GUI 界面的實作計劃。GUI 將提供更友好的使用者體驗，同時保持與現有架構的完全相容性。

## 🎯 功能需求

### 核心功能
1. **自動登入**：啟動時自動使用上次的登入資訊
2. **自動載入 Register Item**：記住並載入上次選擇的交易商品
3. **預設 Order Account**：自動選擇第一個可用帳戶
4. **交易條件設定**：提供友好的界面設定交易參數
5. **狀態顯示**：右上角顯示選擇的 register item index
6. **系統監控**：即時顯示各組件狀態

## 🏗️ 技術架構

### GUI 框架選擇
推薦使用 **PyQt6** 或 **Tkinter**：
- **PyQt6**：功能豐富、現代化 UI、支援複雜佈局
- **Tkinter**：Python 內建、輕量級、易於部署

### 架構整合
```
┌─────────────────────────────────────────────────────┐
│                    GUI Application                   │
│  ┌─────────────────────────────────────────────┐   │
│  │              Main Window                      │   │
│  │  ┌─────────┐ ┌──────────┐ ┌──────────────┐ │   │
│  │  │ Login   │ │ Register │ │   System     │ │   │
│  │  │ Panel   │ │  Items   │ │   Monitor    │ │   │
│  │  └─────────┘ └──────────┘ └──────────────┘ │   │
│  │  ┌─────────────────────────────────────────┐│   │
│  │  │        Trading Conditions Panel         ││   │
│  │  └─────────────────────────────────────────┘│   │
│  └─────────────────────────────────────────────┘   │
│                         ↓                            │
│  ┌─────────────────────────────────────────────┐   │
│  │         ApplicationBootstrapper              │   │
│  │              ServiceContainer                │   │
│  │              SystemManager                   │   │
│  └─────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────┘
```

## 📦 實作細節

### 1. 主視窗佈局
```python
class MainWindow:
    def __init__(self):
        # 頂部工具列
        - 登入狀態指示器
        - Register Item 顯示 (右上角)
        - 系統狀態指示燈
        
        # 主要內容區域
        - 左側：控制面板
          - 登入/登出
          - Register Items 選擇
          - Order Account 選擇
        - 中間：交易條件設定
          - 動作 (買/賣)
          - 目標價格
          - 轉折點
          - 數量
          - 停利/停損
        - 右側：系統監控
          - 組件狀態 (Gateway, Strategy, Order Executor)
          - 市場數據即時顯示
          - 交易記錄
```

### 2. 自動化功能實作

#### 自動登入
```python
# 使用 SessionRepository 儲存和載入登入資訊
def auto_login(self):
    last_session = self.session_repository.get_last_valid_session()
    if last_session and not last_session.is_expired():
        # 使用 UserLoginUseCase 自動登入
        self.login_use_case.execute(last_session.credentials)
```

#### 記住 Register Items
```python
# 使用 UserPreferencesRepository 儲存選擇
def save_register_items(self, items):
    preferences = {
        'register_items': items,
        'last_selected': datetime.now().isoformat()
    }
    self.preferences_repository.save(preferences)
```

### 3. 交易條件設定界面

#### 表單元件
- **動作選擇**：RadioButton (買/賣)
- **價格輸入**：SpinBox 或 LineEdit
- **數量設定**：SpinBox
- **進階選項**：可折疊面板
  - 停利設定
  - 停損設定
  - 跟隨條件

#### 驗證邏輯
```python
def validate_condition(self):
    # 使用現有的 validation 邏輯
    # 即時顯示錯誤訊息
    # 防止無效輸入
```

### 4. 系統監控面板

#### 組件狀態顯示
```python
class ComponentStatusWidget:
    def __init__(self, component_name):
        self.status_label = QLabel()
        self.uptime_label = QLabel()
        self.health_indicator = HealthIndicator()
        
    def update_status(self, status: ComponentStatus):
        # 更新顯示
        # 使用顏色指示狀態
        # GREEN: RUNNING
        # YELLOW: STARTING/STOPPING
        # RED: ERROR/STOPPED
```

#### 即時數據顯示
- 使用 QTimer 定期更新
- 訂閱 ZeroMQ 市場數據
- 顯示最新報價和成交量

## 🔄 資料流程

### 啟動流程
```
1. GUI 啟動
   ↓
2. ApplicationBootstrapper.bootstrap()
   ↓
3. 自動登入 (如果有儲存的 session)
   ↓
4. 載入使用者偏好設定
   ↓
5. 自動選擇 Register Items
   ↓
6. 預設選擇第一個 Order Account
   ↓
7. 顯示主界面，等待使用者操作
```

### 交易啟動流程
```
1. 使用者設定交易條件
   ↓
2. 點擊「啟動交易」按鈕
   ↓
3. ApplicationStartupStatusUseCase 檢查前置條件
   ↓
4. SystemManager.start() 啟動所有組件
   ↓
5. GUI 即時更新組件狀態
   ↓
6. 開始顯示市場數據和交易信號
```

## 💾 資料儲存

### 使用者偏好設定
```json
{
  "last_login": {
    "username": "encrypted_username",
    "environment": "test",
    "timestamp": "2025-01-01T10:00:00"
  },
  "register_items": ["TXF", "MXF"],
  "default_order_account": 0,
  "ui_preferences": {
    "theme": "dark",
    "window_size": [1200, 800],
    "panel_visibility": {
      "market_data": true,
      "trading_log": true
    }
  }
}
```

## 🚀 實作步驟

### Phase 1: 基礎 GUI 框架
1. 建立 GUI 專案結構
2. 實作主視窗和基本佈局
3. 整合 ApplicationBootstrapper

### Phase 2: 核心功能整合
1. 實作登入界面和自動登入
2. 整合 Register Items 選擇
3. 實作 Order Account 選擇
4. 建立交易條件設定表單

### Phase 3: 系統監控和控制
1. 實作組件狀態顯示
2. 整合 SystemManager 控制
3. 添加即時市場數據顯示

### Phase 4: 進階功能
1. 實作使用者偏好設定儲存
2. 添加主題切換
3. 實作交易記錄查看
4. 添加圖表顯示功能

## 📁 建議的檔案結構

```
src/
├── gui/
│   ├── __init__.py
│   ├── main_window.py          # 主視窗
│   ├── widgets/                # 自定義元件
│   │   ├── __init__.py
│   │   ├── login_widget.py
│   │   ├── register_items_widget.py
│   │   ├── conditions_widget.py
│   │   ├── system_monitor_widget.py
│   │   └── market_data_widget.py
│   ├── controllers/            # GUI 控制器
│   │   ├── __init__.py
│   │   └── gui_controller.py
│   ├── utils/                  # GUI 工具
│   │   ├── __init__.py
│   │   ├── validators.py
│   │   └── formatters.py
│   └── resources/              # 圖片、樣式等資源
│       ├── icons/
│       └── styles/
└── app_gui.py                  # GUI 應用程式入口
```

## 🔧 技術考量

### 執行緒管理
- GUI 在主執行緒運行
- 使用 QThread 或 threading 處理長時間操作
- 避免阻塞 GUI 響應

### 錯誤處理
- 使用對話框顯示錯誤
- 記錄詳細錯誤日誌
- 提供錯誤恢復選項

### 效能優化
- 限制市場數據更新頻率
- 使用虛擬化技術顯示大量數據
- 實作延遲載入

## 📝 總結

此 GUI 實作將大幅提升使用者體驗，同時保持與現有架構的完全相容性。通過重用現有的 use cases 和 service container，我們可以確保業務邏輯的一致性，同時提供更直觀的操作界面。