# 🔄 Auto Futures Trading Machine - 詳細流程圖

## 📋 目錄
1. [應用程式啟動詳細流程](#應用程式啟動詳細流程)
2. [All-In-One 初始化流程](#all-in-one-初始化流程)
3. [市場數據處理流程](#市場數據處理流程)
4. [訂單執行完整流程](#訂單執行完整流程)
5. [SystemManager 狀態管理](#systemmanager-狀態管理)

---

## 應用程式啟動詳細流程

### 🚀 **從 app.py 到運行的完整路徑**

```mermaid
sequenceDiagram
    participant Main as app.py::main()
    participant Bootstrap as ApplicationBootstrapper
    participant CLI as CLIApplication
    participant SM as SystemManager
    participant Container as ServiceContainer
    
    Note over Main: 程式入口點
    Main->>Bootstrap: 創建 ApplicationBootstrapper()
    Main->>Bootstrap: bootstrap()
    
    Note over Bootstrap: 依賴注入階段
    Bootstrap->>Bootstrap: _create_required_directories()
    Bootstrap->>Bootstrap: _initialize_core_components()
    Note right of Bootstrap: 創建 Logger, Config, PFCFApi
    
    Bootstrap->>Bootstrap: validate_configuration()
    Note right of Bootstrap: 驗證配置文件和環境變數
    
    Bootstrap->>Container: create_service_container()
    Note right of Container: 創建所有 Repositories<br/>和 Use Cases
    
    Bootstrap->>SM: _create_system_manager()
    Note right of SM: 組裝 SystemManager<br/>和所有基礎設施服務
    
    Bootstrap-->>Main: BootstrapResult(success=True)
    
    Note over Main: 啟動 CLI 應用程式
    Main->>CLI: CLIApplication(system_manager, service_container)
    Main->>CLI: run()
    
    Note over CLI: 進入主菜單循環
    CLI->>CLI: _display_main_menu()
    CLI->>CLI: _handle_user_choice()
```

### 🏗️ **ApplicationBootstrapper 內部詳細流程**

```mermaid
graph TD
    A[ApplicationBootstrapper.bootstrap] --> B[_create_required_directories]
    B --> C[_initialize_core_components]
    C --> D[validate_configuration]
    D --> E[create_service_container]
    E --> F[_create_system_manager]
    
    subgraph "_initialize_core_components 細節"
        C1[創建 LoggerDefault] --> C2[載入 Config]
        C2 --> C3[初始化 PFCFApi]
        C3 --> C4[設定 self._logger, self._config, self._exchange_api]
    end
    
    subgraph "create_service_container 細節"
        E1[創建 Repositories] --> E2[創建 Use Cases]
        E2 --> E3[創建 Controllers]
        E3 --> E4[創建 Presenters]
        E4 --> E5[創建 Views]
        E5 --> E6[組裝 ServiceContainer]
    end
    
    subgraph "_create_system_manager 細節"
        F1[創建 DllGatewayServer] --> F2[創建 PortCheckerService]
        F2 --> F3[創建 MarketDataGatewayService]
        F3 --> F4[創建 ProcessManagerService]
        F4 --> F5[創建 StatusChecker]
        F5 --> F6[組裝 SystemManager]
    end
    
    C --> C1
    E --> E1
    F --> F1
```

---

## All-In-One 初始化流程

### 🎯 **當用戶選擇選項 10 (All-In-One) 時**

```mermaid
sequenceDiagram
    participant User as 用戶
    participant CLI as CLIApplication
    participant Controller as AllInOneController
    participant SM as SystemManager
    participant MDG as MarketDataGatewayService
    participant DGS as DllGatewayServer
    participant PM as ProcessManagerService
    
    User->>CLI: 選擇選項 10
    CLI->>Controller: execute()
    
    Note over Controller: 前置條件檢查
    Controller->>Controller: _check_prerequisites()
    Note right of Controller: 檢查用戶登入狀態<br/>檢查必要配置
    
    Controller->>SM: start_trading_system()
    
    Note over SM: 系統啟動序列
    SM->>SM: _start_gateway()
    
    Note over SM: Gateway 啟動步驟
    SM->>SM: _port_checker.check_port_availability()
    Note right of SM: 檢查 ZMQ 端口 5555, 5556, 5557
    
    SM->>MDG: initialize_market_data_publisher()
    Note right of MDG: 創建 ZMQ Publisher<br/>創建 TickProducer
    
    SM->>MDG: connect_exchange_callbacks()
    Note right of MDG: 連接 PFCF API 回調<br/>OnTickDataTrade += handle_tick_data
    
    SM->>DGS: start()
    Note right of DGS: 啟動 ZMQ REP 服務器<br/>監聽端口 5557
    
    SM->>SM: _start_strategy()
    SM->>PM: 啟動策略進程
    Note right of PM: 執行 run_strategy.py
    
    SM->>SM: _start_order_executor()
    SM->>PM: 啟動訂單執行進程
    Note right of PM: 執行 run_order_executor_gateway.py
    
    SM-->>Controller: SystemStartupResult(success=True)
    Controller-->>User: 顯示啟動成功訊息
    
    Note over User: 系統現在完全運行<br/>三個進程都在工作
```

### 🔧 **SystemManager.start_trading_system() 內部邏輯**

```mermaid
graph TD
    A[start_trading_system] --> B{檢查組件狀態}
    B --> C[設定 gateway = STARTING]
    C --> D[_start_gateway]
    
    D --> E{Gateway 啟動成功?}
    E -->|否| F[設定 gateway = ERROR]
    F --> G[返回失敗結果]
    
    E -->|是| H[等待 3 秒讓 Gateway 穩定]
    H --> I[設定 strategy = STARTING]
    I --> J[_start_strategy]
    
    J --> K{Strategy 啟動成功?}
    K -->|否| L[設定 strategy = ERROR]
    L --> M[返回部分成功結果]
    
    K -->|是| N[設定 order_executor = STARTING]
    N --> O[_start_order_executor]
    
    O --> P{Order Executor 啟動成功?}
    P -->|否| Q[設定 order_executor = ERROR]
    Q --> R[返回部分成功結果]
    
    P -->|是| S[記錄啟動時間]
    S --> T[設定所有組件 = RUNNING]
    T --> U[返回完全成功結果]
```

---

## 市場數據處理流程

### 📊 **從 PFCF 交易所到策略進程的數據流**

```mermaid
sequenceDiagram
    participant Exchange as PFCF 交易所
    participant API as PFCFApi.client
    participant Callback as OnTickDataTrade 回調
    participant Producer as TickProducer
    participant Publisher as ZmqPublisher
    participant Strategy as Strategy Process
    participant Analyzer as Technical Analyzer
    
    Note over Exchange: 市場價格變動
    Exchange->>API: 推送即時報價
    API->>Callback: 觸發 OnTickDataTrade 事件
    
    Note over Callback: PFCF 格式的 Tick 數據
    Callback->>Producer: handle_tick_data(tick_data)
    
    Note over Producer: 數據轉換和包裝
    Producer->>Producer: 轉換為 TickEvent 格式
    Producer->>Publisher: publish_tick_event(tick_event)
    
    Note over Publisher: ZMQ 廣播
    Publisher->>Strategy: 發佈到端口 5555 (PUB/SUB)
    
    Note over Strategy: 策略進程處理
    Strategy->>Strategy: 接收並解序列化 TickEvent
    Strategy->>Analyzer: 執行技術分析
    
    Note over Analyzer: Support/Resistance 分析
    Analyzer->>Analyzer: 計算支撐阻力位
    Analyzer->>Analyzer: 判斷突破信號
    
    Analyzer-->>Strategy: 返回分析結果
    Strategy->>Strategy: 根據分析結果決定是否下單
```

### 📈 **TickProducer 內部處理機制**

```mermaid
graph TD
    A[PFCF Tick Data 進入] --> B[handle_tick_data]
    B --> C{數據格式驗證}
    C -->|無效| D[記錄錯誤並丟棄]
    C -->|有效| E[轉換為 TickEvent 格式]
    
    E --> F[添加時間戳]
    F --> G[序列化為 JSON/MessagePack]
    G --> H[ZmqPublisher.publish]
    
    H --> I[ZMQ Socket 發送]
    I --> J[廣播給所有訂閱者]
    
    subgraph "TickEvent 結構"
        K[symbol: 商品代號]
        L[price: 價格]
        M[volume: 成交量]
        N[timestamp: 時間戳]
        O[bid/ask: 買賣價]
    end
    
    E --> K
    E --> L
    E --> M
    E --> N
    E --> O
```

---

## 訂單執行完整流程

### 💰 **從策略信號到訂單執行的完整路徑**

```mermaid
sequenceDiagram
    participant Strategy as Strategy Process
    participant SignalQueue as ZMQ PUSH Queue
    participant OrderExec as Order Executor Process
    participant Gateway as DllGatewayServer
    participant API as PFCFApi
    participant Exchange as PFCF 交易所
    
    Note over Strategy: 技術分析完成，產生信號
    Strategy->>Strategy: 創建 TradingSignal
    Strategy->>SignalQueue: 推送信號 (PUSH to port 5556)
    
    Note over OrderExec: 訂單執行進程監聽信號
    SignalQueue->>OrderExec: 拉取信號 (PULL from port 5556)
    OrderExec->>OrderExec: 驗證信號格式
    
    Note over OrderExec: 風險控制檢查
    OrderExec->>OrderExec: 檢查倉位限制
    OrderExec->>OrderExec: 檢查資金充足性
    
    OrderExec->>Gateway: 發送訂單請求 (ZMQ REQ to port 5557)
    Note right of Gateway: REQ 包含:<br/>operation: "send_order"<br/>parameters: 訂單參數
    
    Note over Gateway: DLL Gateway 處理
    Gateway->>Gateway: 解析訂單請求
    Gateway->>Gateway: 轉換為 PFCF 格式
    
    Gateway->>API: 調用 DTradeLib.Order()
    API->>Exchange: 發送訂單到交易所
    
    Note over Exchange: 交易所處理訂單
    Exchange-->>API: 返回執行結果
    API-->>Gateway: OrderResult 物件
    
    Gateway->>Gateway: 轉換為統一格式
    Gateway-->>OrderExec: 回應執行結果 (ZMQ REP)
    
    Note over OrderExec: 處理執行結果
    OrderExec->>OrderExec: 記錄交易日誌
    OrderExec->>OrderExec: 更新倉位狀態
    OrderExec->>OrderExec: 風險監控
```

### 🎯 **TradingSignal 和 OrderRequest 轉換過程**

```mermaid
graph TD
    A[Strategy 產生 TradingSignal] --> B[包含策略決策信息]
    B --> C[symbol, direction, confidence, timestamp]
    
    C --> D[OrderExecutor 接收]
    D --> E[轉換為 OrderRequest]
    
    E --> F[添加交易參數]
    F --> G[order_account, price, quantity]
    F --> H[order_type, time_in_force]
    F --> I[open_close, day_trade]
    
    G --> J[發送給 DllGatewayServer]
    H --> J
    I --> J
    
    J --> K[轉換為 PFCF 格式]
    K --> L[調用 exchange_client.Order()]
    
    subgraph "PFCF DLL 格式"
        M[OrderObject]
        N[ACTNO: 帳號]
        O[PRODUCTID: 商品]
        P[BS: 買賣別]
        Q[PRICE: 價格]
        R[ORDERQTY: 數量]
    end
    
    K --> M
    M --> N
    M --> O
    M --> P
    M --> Q
    M --> R
```

---

## SystemManager 狀態管理

### 🎛️ **組件狀態轉換圖**

```mermaid
stateDiagram-v2
    [*] --> STOPPED: 初始狀態
    
    STOPPED --> STARTING: start_trading_system()
    STARTING --> RUNNING: 啟動成功
    STARTING --> ERROR: 啟動失敗
    
    RUNNING --> STOPPING: stop_trading_system()
    STOPPING --> STOPPED: 關閉完成
    
    ERROR --> STARTING: restart_component()
    RUNNING --> STARTING: restart_component()
    
    note right of STARTING
        執行初始化步驟:
        1. 檢查端口
        2. 初始化組件
        3. 連接回調
        4. 啟動服務
    end note
    
    note right of RUNNING
        正常運行狀態:
        - 接收市場數據
        - 處理交易信號
        - 執行訂單
        - 健康監控
    end note
    
    note right of STOPPING
        優雅關閉順序:
        1. Order Executor
        2. Strategy
        3. Gateway (最後)
    end note
```

### 🔄 **SystemManager.get_system_health() 檢查流程**

```mermaid
graph TD
    A[get_system_health 被調用] --> B[檢查啟動時間]
    B --> C[計算運行時間]
    C --> D[檢查所有組件狀態]
    
    D --> E{所有組件都是 RUNNING?}
    E -->|是| F[is_healthy = True]
    E -->|否| G[is_healthy = False]
    
    F --> H[創建 SystemHealth 物件]
    G --> H
    
    H --> I[包含組件狀態字典]
    I --> J[包含運行時間]
    J --> K[包含檢查時間戳]
    K --> L[返回健康狀態報告]
    
    subgraph "組件狀態字典"
        M["gateway": ComponentStatus]
        N["strategy": ComponentStatus] 
        O["order_executor": ComponentStatus]
    end
    
    I --> M
    I --> N
    I --> O
```

### 📊 **SystemManager 依賴關係圖**

```mermaid
graph TB
    subgraph "SystemManager 構造函數依賴"
        SM[SystemManager]
        
        SM --> Logger[LoggerDefault<br/>日誌記錄]
        SM --> DGS[DllGatewayServer<br/>訂單執行服務器]
        SM --> PC[PortCheckerService<br/>端口可用性檢查]
        SM --> MDG[MarketDataGatewayService<br/>市場數據網關]
        SM --> PM[ProcessManagerService<br/>進程管理]
        SM --> SC[StatusChecker<br/>狀態檢查器]
    end
    
    subgraph "MarketDataGatewayService 依賴"
        MDG --> Config1[Config<br/>配置]
        MDG --> Logger1[LoggerInterface<br/>日誌]
        MDG --> PFCF1[PFCFApi<br/>交易所API]
    end
    
    subgraph "DllGatewayServer 依賴"
        DGS --> Config2[Config<br/>配置]
        DGS --> Logger2[LoggerInterface<br/>日誌] 
        DGS --> PFCF2[PFCFApi<br/>交易所API]
    end
    
    subgraph "外部進程 (SystemManager 管理但不直接依賴)"
        ExtProc[外部進程]
        Strategy[Strategy Process<br/>run_strategy.py]
        OrderExec[Order Executor<br/>run_order_executor_gateway.py]
    end
    
    PM -.-> Strategy
    PM -.-> OrderExec
```

---

## 🎯 **關鍵洞察**

### 💡 **設計亮點**

1. **分離關注點**: MarketDataGatewayService 和 DllGatewayServer 各司其職
2. **狀態管理**: SystemManager 統一管理所有組件的生命週期
3. **錯誤處理**: 組件啟動失敗時，系統可以部分運行或優雅降級
4. **可觀測性**: 詳細的狀態追蹤和健康檢查機制

### ⚠️ **潛在改進點**

1. **硬編碼延遲**: `time.sleep(3)` 等待 Gateway 初始化缺乏靈活性
2. **錯誤恢復**: 組件失敗後的自動重試機制
3. **監控增強**: 更詳細的性能指標和監控數據
4. **配置熱重載**: 運行時修改配置的能力

這些流程圖幫助開發者：
- 🎯 **精確定位問題**: 知道在哪個步驟可能出錯
- 🔧 **指導開發**: 了解添加新功能時的插入點
- 📊 **性能優化**: 識別瓶頸和優化機會
- 🛡️ **故障排除**: 快速診斷系統問題