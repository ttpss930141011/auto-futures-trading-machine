# 🏗️ Auto Futures Trading Machine - 架構詳解

## 📋 目錄
1. [系統總覽](#系統總覽)
2. [app.py 啟動流程](#apppy-啟動流程)
3. [類別職責分工](#類別職責分工)
4. [數據流向圖](#數據流向圖)
5. [組件交互圖](#組件交互圖)
6. [OOP 設計原則](#oop-設計原則)

---

## 系統總覽

這是一個多進程的期貨自動交易系統，採用 Clean Architecture 設計，主要分為三個進程：

```
┌─────────────────────────────────────────────────────────┐
│                    🖥️  Main Process                     │
│                      (app.py)                          │
│  ┌─────────────────┐  ┌─────────────────┐              │
│  │ CLIApplication  │  │ SystemManager   │              │
│  │                 │  │                 │              │
│  │ ├─ 用戶界面       │  │ ├─ 生命週期管理   │              │
│  │ ├─ 菜單系統       │  │ ├─ 組件協調      │              │
│  │ └─ 指令處理       │  │ └─ 狀態監控      │              │
│  └─────────────────┘  └─────────────────┘              │
│           │                      │                     │
│           │              ┌─────────────────┐            │
│           └──────────────│ MarketDataGateway │          │
│                          │ + DllGatewayServer │         │
│                          └─────────────────┘            │
└─────────────────────────────────────────────────────────┘
                              │
                              │ ZMQ 通信
                              │
         ┌────────────────────┼────────────────────┐
         │                   │                    │
         ▼                   ▼                    ▼
┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐
│  📊 Strategy    │ │  📈 Market Data │ │  💼 Order       │
│    Process      │ │    Flow         │ │   Executor      │
│                 │ │                 │ │   Process       │
│ ├─ 技術分析      │ │ ├─ 即時報價      │ │ ├─ 訂單執行      │
│ ├─ 信號生成      │ │ ├─ 價格廣播      │ │ ├─ 風險控制      │
│ └─ 策略邏輯      │ │ └─ 數據分發      │ │ └─ 執行確認      │
└─────────────────┘ └─────────────────┘ └─────────────────┘
```

---

## app.py 啟動流程

### 1️⃣ **應用程式初始化階段**

```mermaid
graph TD
    A[app.py 啟動] --> B[CLIApplication.__init__]
    B --> C[ApplicationBootstrapper 創建]
    C --> D[ApplicationBootstrapper.bootstrap]
    
    D --> E[_create_required_directories]
    D --> F[_initialize_core_components]
    D --> G[validate_configuration]
    D --> H[create_service_container]
    D --> I[_create_system_manager]
    
    F --> F1[LoggerDefault 創建]
    F --> F2[Config 載入]
    F --> F3[PFCFApi 初始化]
    
    H --> H1[各種 Repository 創建]
    H --> H2[Use Cases 創建]
    H --> H3[Controllers 創建]
    
    I --> I1[SystemManager 組裝]
    I --> I2[依賴注入完成]
```

### 2️⃣ **系統管理器組裝過程**

```mermaid
graph LR
    subgraph "ApplicationBootstrapper._create_system_manager()"
        A[創建基礎服務] --> B[DllGatewayServer]
        A --> C[PortCheckerService]
        A --> D[MarketDataGatewayService]
        A --> E[ProcessManagerService]
        A --> F[StatusChecker]
        
        B --> G[SystemManager 組裝]
        C --> G
        D --> G
        E --> G
        F --> G
    end
```

---

## 類別職責分工

### 🎯 **主要類別與職責**

#### **應用程式層 (Application Layer)**

```
CLIApplication
├── 🎮 職責: 應用程式生命週期管理
├── 📝 功能: 
│   ├─ 啟動和關閉應用程式
│   ├─ 例外處理和優雅退出
│   └─ 用戶界面協調
└── 🔗 依賴: ApplicationBootstrapper, SystemManager
```

```
ApplicationBootstrapper  
├── 🏗️ 職責: 依賴注入和初始化
├── 📝 功能:
│   ├─ 創建所有服務實例
│   ├─ 配置驗證
│   ├─ 服務容器組裝
│   └─ SystemManager 建構
└── 🔗 依賴: Config, Logger, PFCFApi
```

#### **基礎設施層 (Infrastructure Layer)**

```
SystemManager
├── 🎛️ 職責: 系統組件生命週期管理
├── 📝 功能:
│   ├─ 啟動/停止交易系統
│   ├─ 組件狀態監控
│   ├─ 健康檢查
│   └─ 組件重啟
└── 🔗 管理:
    ├─ MarketDataGatewayService
    ├─ DllGatewayServer  
    ├─ ProcessManagerService
    └─ PortCheckerService
```

```
MarketDataGatewayService
├── 📊 職責: 市場數據基礎設施
├── 📝 功能:
│   ├─ ZMQ Publisher 初始化
│   ├─ PFCF API 回調連接
│   ├─ 即時報價廣播
│   └─ 數據流管理
└── 🔗 依賴: ZmqPublisher, TickProducer, PFCFApi
```

```
DllGatewayServer
├── 💼 職責: 訂單執行服務器
├── 📝 功能:
│   ├─ ZMQ REQ/REP 服務器
│   ├─ 訂單請求處理
│   ├─ PFCF DLL 調用
│   └─ 執行結果回應
└── 🔗 依賴: PFCFApi, ZMQ REP Socket
```

#### **業務邏輯層 (Interactor Layer)**

```
Use Cases (各種業務用例)
├── 🎯 職責: 業務邏輯封裝
├── 📝 功能:
│   ├─ 業務規則執行
│   ├─ 數據驗證
│   ├─ 錯誤處理
│   └─ 結果回傳
└── 🔗 依賴: Entities, Repositories, Services
```

---

## 數據流向圖

### 📈 **市場數據流向**

```mermaid
sequenceDiagram
    participant PFCF as PFCF Exchange
    participant API as PFCFApi
    participant MDG as MarketDataGatewayService
    participant ZMQ as ZMQ Publisher
    participant Strategy as Strategy Process
    
    PFCF->>API: 即時報價回調
    API->>MDG: OnTickDataTrade 事件
    MDG->>ZMQ: 發佈市場數據
    ZMQ->>Strategy: 廣播給策略進程
    Strategy->>Strategy: 技術分析和信號生成
```

### 💰 **訂單執行流向**

```mermaid
sequenceDiagram
    participant Strategy as Strategy Process
    participant Signal as Signal Queue
    participant OrderExec as Order Executor
    participant DGS as DllGatewayServer
    participant PFCF as PFCF Exchange
    
    Strategy->>Signal: 推送交易信號
    Signal->>OrderExec: 信號被拉取
    OrderExec->>DGS: 發送訂單請求 (ZMQ REQ)
    DGS->>PFCF: 調用 DLL 執行訂單
    PFCF->>DGS: 返回執行結果
    DGS->>OrderExec: 回應結果 (ZMQ REP)
```

### 🔄 **完整交易週期**

```mermaid
graph TD
    A[PFCF 交易所] --> B[PFCFApi 接收報價]
    B --> C[MarketDataGatewayService]
    C --> D[ZMQ Publisher 廣播]
    D --> E[Strategy Process 接收]
    E --> F[技術分析]
    F --> G{生成信號?}
    G -->|是| H[推送到 Signal Queue]
    G -->|否| E
    H --> I[Order Executor 拉取]
    I --> J[發送到 DllGatewayServer]
    J --> K[調用 PFCF DLL]
    K --> L[訂單執行]
    L --> A
```

---

## 組件交互圖

### 🎛️ **SystemManager 的管理範圍**

```mermaid
graph TB
    subgraph "SystemManager 管轄"
        SM[SystemManager<br/>系統管理器]
        
        subgraph "Gateway 組件"
            MDG[MarketDataGatewayService<br/>市場數據網關]
            DGS[DllGatewayServer<br/>訂單執行服務器]
        end
        
        subgraph "支援服務"
            PC[PortCheckerService<br/>端口檢查]
            PM[ProcessManagerService<br/>進程管理]
            SC[StatusChecker<br/>狀態檢查]
        end
        
        SM --> MDG
        SM --> DGS
        SM --> PC
        SM --> PM
        SM --> SC
    end
    
    subgraph "外部進程"
        SP[Strategy Process<br/>策略進程]
        OE[Order Executor<br/>訂單執行進程]
    end
    
    MDG -.->|ZMQ PUB| SP
    SP -.->|ZMQ PUSH| OE
    OE -.->|ZMQ REQ| DGS
```

### 🏛️ **Clean Architecture 層次**

```mermaid
graph TB
    subgraph "🖥️ Presentation Layer"
        CLI[CLIApplication]
        Controllers[Controllers]
        Views[Views]
        Presenters[Presenters]
    end
    
    subgraph "💼 Application Layer"
        Bootstrap[ApplicationBootstrapper]
        UseCases[Use Cases]
    end
    
    subgraph "🎯 Domain Layer"
        Entities[Entities]
        ValueObjects[Value Objects]
        DomainServices[Domain Services]
    end
    
    subgraph "🔧 Infrastructure Layer"
        SystemMgr[SystemManager]
        MarketData[MarketDataGatewayService]
        DllGateway[DllGatewayServer]
        Repos[Repositories]
        ZMQ[ZMQ Messaging]
        PFCF[PFCF Client]
    end
    
    CLI --> Bootstrap
    Controllers --> UseCases
    UseCases --> Entities
    UseCases --> Repos
    SystemMgr --> MarketData
    SystemMgr --> DllGateway
```

---

## OOP 設計原則

### 🎯 **SOLID 原則應用**

#### **S - Single Responsibility Principle (單一職責)**
- ✅ `MarketDataGatewayService`: 只負責市場數據發佈
- ✅ `DllGatewayServer`: 只負責訂單執行
- ✅ `SystemManager`: 只負責組件生命週期管理

#### **O - Open/Closed Principle (開放封閉)**
- ✅ 使用 Interface 定義契約 (`MarketDataGatewayServiceInterface`)
- ✅ 可擴展新的交易策略而不修改現有代碼

#### **L - Liskov Substitution Principle (里氏替換)**
- ✅ 所有服務都實現對應的 Interface
- ✅ 可以輕鬆替換不同的實現

#### **I - Interface Segregation Principle (接口隔離)**
- ✅ 分離不同職責的接口
- ✅ 客戶端只依賴需要的接口

#### **D - Dependency Inversion Principle (依賴反轉)**
- ✅ 高層模組 (Use Cases) 不依賴低層模組 (Infrastructure)
- ✅ 都依賴於抽象 (Interfaces)

### 🔄 **設計模式應用**

#### **Repository Pattern (倉庫模式)**
```python
# 抽象
SessionRepositoryInterface
# 實現
SessionInMemoryRepository
SessionJsonFileRepository
```

#### **Dependency Injection (依賴注入)**
```python
# ApplicationBootstrapper 負責組裝所有依賴
system_manager = SystemManager(
    logger=logger,
    market_data_gateway=market_data_gateway,
    dll_gateway_server=dll_gateway_server,
    # ...其他依賴
)
```

#### **Observer Pattern (觀察者模式)**
```python
# PFCF API 回調機制
exchange_client.DQuoteLib.OnTickDataTrade += tick_producer.handle_tick_data
```

#### **Command Pattern (命令模式)**
```python
# Use Cases 封裝業務操作
class SendMarketOrderUseCase:
    def execute(self, input_dto: SendMarketOrderInputDto) -> SendMarketOrderOutputDto
```

---

## 🎯 **總結**

這個架構的核心優勢：

1. **🔧 模組化設計**: 每個類別都有明確的職責
2. **🔄 可測試性**: 依賴注入讓單元測試變得容易
3. **📈 可擴展性**: 遵循 SOLID 原則，易於擴展新功能
4. **🛡️ 可維護性**: Clean Architecture 讓代碼結構清晰
5. **⚡ 高性能**: 多進程設計繞過 Python GIL 限制

通過這個文檔，開發者可以：
- 快速理解系統整體架構
- 找到需要修改的具體類別
- 了解數據如何在系統中流動
- 掌握各組件的交互關係