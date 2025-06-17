# 🔄 Auto Futures Trading Machine - Detailed Flow Diagrams

## 📋 Table of Contents
1. [Application Startup Detailed Flow](#application-startup-detailed-flow)
2. [All-In-One Initialization Flow](#all-in-one-initialization-flow)
3. [Market Data Processing Flow](#market-data-processing-flow)
4. [Order Execution Complete Flow](#order-execution-complete-flow)
5. [SystemManager State Management](#systemmanager-state-management)

---

## Application Startup Detailed Flow

### 🚀 **Complete Path from app.py to Running**

```mermaid
sequenceDiagram
    participant Main as app.py::main()
    participant Bootstrap as ApplicationBootstrapper
    participant CLI as CLIApplication
    participant SM as SystemManager
    participant Container as ServiceContainer
    
    Note over Main: Program entry point
    Main->>Bootstrap: Create ApplicationBootstrapper()
    Main->>Bootstrap: bootstrap()
    
    Note over Bootstrap: Dependency injection phase
    Bootstrap->>Bootstrap: _create_required_directories()
    Bootstrap->>Bootstrap: _initialize_core_components()
    Note right of Bootstrap: Create Logger, Config, PFCFApi
    
    Bootstrap->>Bootstrap: validate_configuration()
    Note right of Bootstrap: Validate config files and env variables
    
    Bootstrap->>Container: create_service_container()
    Note right of Container: Create all Repositories<br/>and Use Cases
    
    Bootstrap->>SM: _create_system_manager()
    Note right of SM: Assemble SystemManager<br/>and all infrastructure services
    
    Bootstrap-->>Main: BootstrapResult(success=True)
    
    Note over Main: Start CLI application
    Main->>CLI: CLIApplication(system_manager, service_container)
    Main->>CLI: run()
    
    Note over CLI: Enter main menu loop
    CLI->>CLI: _display_main_menu()
    CLI->>CLI: _handle_user_choice()
```

### 🏗️ **ApplicationBootstrapper Internal Detailed Flow**

```mermaid
graph TD
    A[ApplicationBootstrapper.bootstrap] --> B[_create_required_directories]
    B --> C[_initialize_core_components]
    C --> D[validate_configuration]
    D --> E[create_service_container]
    E --> F[_create_system_manager]
    
    subgraph "_initialize_core_components Details"
        C1[Create LoggerDefault] --> C2[Load Config]
        C2 --> C3[Initialize PFCFApi]
        C3 --> C4[Set self._logger, self._config, self._exchange_api]
    end
    
    subgraph "create_service_container Details"
        E1[Create Repositories] --> E2[Create Use Cases]
        E2 --> E3[Create Controllers]
        E3 --> E4[Create Presenters]
        E4 --> E5[Create Views]
        E5 --> E6[Assemble ServiceContainer]
    end
    
    subgraph "_create_system_manager Details"
        F1[Create DllGatewayServer] --> F2[Create PortCheckerService]
        F2 --> F3[Create MarketDataGatewayService]
        F3 --> F4[Create ProcessManagerService]
        F4 --> F5[Create StatusChecker]
        F5 --> F6[Assemble SystemManager]
    end
    
    C --> C1
    E --> E1
    F --> F1
```

---

## All-In-One Initialization Flow

### 🎯 **When User Selects Option 10 (All-In-One)**

```mermaid
sequenceDiagram
    participant User as User
    participant CLI as CLIApplication
    participant Controller as AllInOneController
    participant SM as SystemManager
    participant MDG as MarketDataGatewayService
    participant DGS as DllGatewayServer
    participant PM as ProcessManagerService
    
    User->>CLI: Select option 10
    CLI->>Controller: execute()
    
    Note over Controller: Prerequisites check
    Controller->>Controller: _check_prerequisites()
    Note right of Controller: Check user login status<br/>Check necessary configuration
    
    Controller->>SM: start_trading_system()
    
    Note over SM: System startup sequence
    SM->>SM: _start_gateway()
    
    Note over SM: Gateway startup steps
    SM->>SM: _port_checker.check_port_availability()
    Note right of SM: Check ZMQ ports 5555, 5556, 5557
    
    SM->>MDG: initialize_market_data_publisher()
    Note right of MDG: Create ZMQ Publisher<br/>Create TickProducer
    
    SM->>MDG: connect_exchange_callbacks()
    Note right of MDG: Connect PFCF API callbacks<br/>OnTickDataTrade += handle_tick_data
    
    SM->>DGS: start()
    Note right of DGS: Start ZMQ REP server<br/>Listen on port 5557
    
    SM->>SM: _start_strategy()
    SM->>PM: Start strategy process
    Note right of PM: Execute run_strategy.py
    
    SM->>SM: _start_order_executor()
    SM->>PM: Start order executor process
    Note right of PM: Execute run_order_executor_gateway.py
    
    SM-->>Controller: SystemStartupResult(success=True)
    Controller-->>User: Display startup success message
    
    Note over User: System now fully running<br/>All three processes working
```

### 🔧 **SystemManager.start_trading_system() Internal Logic**

```mermaid
graph TD
    A[start_trading_system] --> B{Check component status}
    B --> C[Set gateway = STARTING]
    C --> D[_start_gateway]
    
    D --> E{Gateway startup success?}
    E -->|No| F[Set gateway = ERROR]
    F --> G[Return failure result]
    
    E -->|Yes| H[Wait 3 seconds for Gateway stability]
    H --> I[Set strategy = STARTING]
    I --> J[_start_strategy]
    
    J --> K{Strategy startup success?}
    K -->|No| L[Set strategy = ERROR]
    L --> M[Return partial success result]
    
    K -->|Yes| N[Set order_executor = STARTING]
    N --> O[_start_order_executor]
    
    O --> P{Order Executor startup success?}
    P -->|No| Q[Set order_executor = ERROR]
    Q --> R[Return partial success result]
    
    P -->|Yes| S[Record startup time]
    S --> T[Set all components = RUNNING]
    T --> U[Return complete success result]
```

---

## Market Data Processing Flow

### 📊 **Data Flow from PFCF Exchange to Strategy Process**

```mermaid
sequenceDiagram
    participant Exchange as PFCF Exchange
    participant API as PFCFApi.client
    participant Callback as OnTickDataTrade Callback
    participant Producer as TickProducer
    participant Publisher as ZmqPublisher
    participant Strategy as Strategy Process
    participant Analyzer as Technical Analyzer
    
    Note over Exchange: Market price changes
    Exchange->>API: Push real-time quotes
    API->>Callback: Trigger OnTickDataTrade event
    
    Note over Callback: PFCF format Tick data
    Callback->>Producer: handle_tick_data(tick_data)
    
    Note over Producer: Data conversion and packaging
    Producer->>Producer: Convert to TickEvent format
    Producer->>Publisher: publish_tick_event(tick_event)
    
    Note over Publisher: ZMQ broadcast
    Publisher->>Strategy: Publish to port 5555 (PUB/SUB)
    
    Note over Strategy: Strategy process handling
    Strategy->>Strategy: Receive and deserialize TickEvent
    Strategy->>Analyzer: Execute technical analysis
    
    Note over Analyzer: Support/Resistance analysis
    Analyzer->>Analyzer: Calculate support/resistance levels
    Analyzer->>Analyzer: Determine breakout signals
    
    Analyzer-->>Strategy: Return analysis results
    Strategy->>Strategy: Decide whether to place order based on analysis
```

### 📈 **TickProducer Internal Processing Mechanism**

```mermaid
graph TD
    A[PFCF Tick Data Entry] --> B[handle_tick_data]
    B --> C{Data format validation}
    C -->|Invalid| D[Log error and discard]
    C -->|Valid| E[Convert to TickEvent format]
    
    E --> F[Add timestamp]
    F --> G[Serialize to JSON/MessagePack]
    G --> H[ZmqPublisher.publish]
    
    H --> I[ZMQ Socket send]
    I --> J[Broadcast to all subscribers]
    
    subgraph "TickEvent Structure"
        K[symbol: Product code]
        L[price: Price]
        M[volume: Volume]
        N[timestamp: Timestamp]
        O[bid/ask: Bid/Ask prices]
    end
    
    E --> K
    E --> L
    E --> M
    E --> N
    E --> O
```

---

## Order Execution Complete Flow

### 💰 **Complete Path from Strategy Signal to Order Execution**

```mermaid
sequenceDiagram
    participant Strategy as Strategy Process
    participant SignalQueue as ZMQ PUSH Queue
    participant OrderExec as Order Executor Process
    participant Gateway as DllGatewayServer
    participant API as PFCFApi
    participant Exchange as PFCF Exchange
    
    Note over Strategy: Technical analysis completed, generate signal
    Strategy->>Strategy: Create TradingSignal
    Strategy->>SignalQueue: Push signal (PUSH to port 5556)
    
    Note over OrderExec: Order executor process listening for signals
    SignalQueue->>OrderExec: Pull signal (PULL from port 5556)
    OrderExec->>OrderExec: Validate signal format
    
    Note over OrderExec: Risk control checks
    OrderExec->>OrderExec: Check position limits
    OrderExec->>OrderExec: Check capital adequacy
    
    OrderExec->>Gateway: Send order request (ZMQ REQ to port 5557)
    Note right of Gateway: REQ contains:<br/>operation: "send_order"<br/>parameters: order parameters
    
    Note over Gateway: DLL Gateway processing
    Gateway->>Gateway: Parse order request
    Gateway->>Gateway: Convert to PFCF format
    
    Gateway->>API: Call DTradeLib.Order()
    API->>Exchange: Send order to exchange
    
    Note over Exchange: Exchange processes order
    Exchange-->>API: Return execution result
    API-->>Gateway: OrderResult object
    
    Gateway->>Gateway: Convert to unified format
    Gateway-->>OrderExec: Reply execution result (ZMQ REP)
    
    Note over OrderExec: Process execution result
    OrderExec->>OrderExec: Log transaction
    OrderExec->>OrderExec: Update position status
    OrderExec->>OrderExec: Risk monitoring
```

### 🎯 **TradingSignal to OrderRequest Conversion Process**

```mermaid
graph TD
    A[Strategy generates TradingSignal] --> B[Contains strategic decision info]
    B --> C[symbol, direction, confidence, timestamp]
    
    C --> D[OrderExecutor receives]
    D --> E[Convert to OrderRequest]
    
    E --> F[Add trading parameters]
    F --> G[order_account, price, quantity]
    F --> H[order_type, time_in_force]
    F --> I[open_close, day_trade]
    
    G --> J[Send to DllGatewayServer]
    H --> J
    I --> J
    
    J --> K[Convert to PFCF format]
    K --> L["Call exchange_client.Order()"]
    
    subgraph "PFCF DLL Format"
        M[OrderObject]
        N[ACTNO: Account]
        O[PRODUCTID: Product]
        P[BS: Buy/Sell]
        Q[PRICE: Price]
        R[ORDERQTY: Quantity]
    end
    
    K --> M
    M --> N
    M --> O
    M --> P
    M --> Q
    M --> R
```

---

## SystemManager State Management

### 🎛️ **Component State Transition Diagram**

```mermaid
stateDiagram-v2
    [*] --> STOPPED: Initial state
    
    STOPPED --> STARTING: start_trading_system()
    STARTING --> RUNNING: Startup success
    STARTING --> ERROR: Startup failure
    
    RUNNING --> STOPPING: stop_trading_system()
    STOPPING --> STOPPED: Shutdown complete
    
    ERROR --> STARTING: restart_component()
    RUNNING --> STARTING: restart_component()
    
    note right of STARTING
        Execute initialization steps:
        1. Check ports
        2. Initialize components
        3. Connect callbacks
        4. Start services
    end note
    
    note right of RUNNING
        Normal running state:
        - Receive market data
        - Process trading signals
        - Execute orders
        - Health monitoring
    end note
    
    note right of STOPPING
        Graceful shutdown order:
        1. Order Executor
        2. Strategy
        3. Gateway (last)
    end note
```

### 🔄 **SystemManager.get_system_health() Check Flow**

```mermaid
graph TD
    A[get_system_health called] --> B[Check startup time]
    B --> C[Calculate uptime]
    C --> D[Check all component status]
    
    D --> E{All components RUNNING?}
    E -->|Yes| F[is_healthy = True]
    E -->|No| G[is_healthy = False]
    
    F --> H[Create SystemHealth object]
    G --> H
    
    H --> I[Include component status dict]
    I --> J[Include uptime]
    J --> K[Include check timestamp]
    K --> L[Return health status report]
    
    subgraph "Component Status Dictionary"
        M["gateway": ComponentStatus]
        N["strategy": ComponentStatus] 
        O["order_executor": ComponentStatus]
    end
    
    I --> M
    I --> N
    I --> O
```

### 📊 **SystemManager Dependency Diagram**

```mermaid
graph TB
    subgraph "SystemManager Constructor Dependencies"
        SM[SystemManager]
        
        SM --> Logger[LoggerDefault<br/>Logging]
        SM --> DGS[DllGatewayServer<br/>Order Execution Server]
        SM --> PC[PortCheckerService<br/>Port Availability Check]
        SM --> MDG[MarketDataGatewayService<br/>Market Data Gateway]
        SM --> PM[ProcessManagerService<br/>Process Management]
        SM --> SC[StatusChecker<br/>Status Checker]
    end
    
    subgraph "MarketDataGatewayService Dependencies"
        MDG --> Config1[Config<br/>Configuration]
        MDG --> Logger1[LoggerInterface<br/>Logger]
        MDG --> PFCF1[PFCFApi<br/>Exchange API]
    end
    
    subgraph "DllGatewayServer Dependencies"
        DGS --> Config2[Config<br/>Configuration]
        DGS --> Logger2[LoggerInterface<br/>Logger] 
        DGS --> PFCF2[PFCFApi<br/>Exchange API]
    end
    
    subgraph "External Processes (Managed by SystemManager but not direct dependencies)"
        ExtProc[External Processes]
        Strategy[Strategy Process<br/>run_strategy.py]
        OrderExec[Order Executor<br/>run_order_executor_gateway.py]
    end
    
    PM -.-> Strategy
    PM -.-> OrderExec
```

---

## 🎯 **Key Insights**

### 💡 **Design Highlights**

1. **Separation of Concerns**: MarketDataGatewayService and DllGatewayServer each have their own responsibilities
2. **State Management**: SystemManager uniformly manages lifecycle of all components
3. **Error Handling**: System can run partially or degrade gracefully when component startup fails
4. **Observability**: Detailed state tracking and health check mechanisms

### ⚠️ **Potential Improvements**

1. **Hardcoded Delays**: `time.sleep(3)` waiting for Gateway initialization lacks flexibility
2. **Error Recovery**: Automatic retry mechanism after component failure
3. **Enhanced Monitoring**: More detailed performance metrics and monitoring data
4. **Configuration Hot Reload**: Ability to modify configuration at runtime

These flow diagrams help developers:
- 🎯 **Pinpoint Issues**: Know where errors might occur at each step
- 🔧 **Guide Development**: Understand insertion points when adding new features
- 📊 **Performance Optimization**: Identify bottlenecks and optimization opportunities
- 🛡️ **Troubleshooting**: Quickly diagnose system problems