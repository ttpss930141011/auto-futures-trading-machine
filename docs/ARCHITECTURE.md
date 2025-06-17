# 🏗️ Auto Futures Trading Machine - Architecture Guide

## 📋 Table of Contents
1. [System Overview](#system-overview)
2. [Application Startup Flow](#application-startup-flow)
3. [Class Responsibilities](#class-responsibilities)
4. [Data Flow Diagrams](#data-flow-diagrams)
5. [Component Interaction](#component-interaction)
6. [OOP Design Principles](#oop-design-principles)

---

## System Overview

This is a multi-process automated futures trading system that uses Clean Architecture design principles. The system consists of three main processes:

```
┌─────────────────────────────────────────────────────────┐
│                    🖥️  Main Process                     │
│                      (app.py)                          │
│  ┌─────────────────┐  ┌─────────────────┐              │
│  │ CLIApplication  │  │ SystemManager   │              │
│  │                 │  │                 │              │
│  │ ├─ User Interface│  │ ├─ Lifecycle Mgmt│              │
│  │ ├─ Menu System   │  │ ├─ Component Coord│              │
│  │ └─ Command Proc  │  │ └─ Status Monitor│              │
│  └─────────────────┘  └─────────────────┘              │
│           │                      │                     │
│           │              ┌─────────────────┐            │
│           └──────────────│ MarketDataGateway │          │
│                          │ + DllGatewayServer │         │
│                          └─────────────────┘            │
└─────────────────────────────────────────────────────────┘
                              │
                              │ ZMQ Communication
                              │
         ┌────────────────────┼────────────────────┐
         │                   │                    │
         ▼                   ▼                    ▼
┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐
│  📊 Strategy    │ │  📈 Market Data │ │  💼 Order       │
│    Process      │ │    Flow         │ │   Executor      │
│                 │ │                 │ │   Process       │
│ ├─ Technical Analysis │ ├─ Real-time Quotes │ ├─ Order Execution │
│ ├─ Signal Generation  │ ├─ Price Broadcast  │ ├─ Risk Control    │
│ └─ Strategy Logic     │ └─ Data Distribution│ └─ Execution Confirm│
└─────────────────┘ └─────────────────┘ └─────────────────┘
```

---

## Application Startup Flow

### 1️⃣ **Application Initialization Phase**

```mermaid
graph TD
    A[app.py Start] --> B[CLIApplication.__init__]
    B --> C[ApplicationBootstrapper Creation]
    C --> D[ApplicationBootstrapper.bootstrap]
    
    D --> E[_create_required_directories]
    D --> F[_initialize_core_components]
    D --> G[validate_configuration]
    D --> H[create_service_container]
    D --> I[_create_system_manager]
    
    F --> F1[LoggerDefault Creation]
    F --> F2[Config Loading]
    F --> F3[PFCFApi Initialization]
    
    H --> H1[Repository Creation]
    H --> H2[Use Cases Creation]
    H --> H3[Controllers Creation]
    
    I --> I1[SystemManager Assembly]
    I --> I2[Dependency Injection Complete]
```

### 2️⃣ **System Manager Assembly Process**

```mermaid
graph TB
    subgraph "ApplicationBootstrapper.bootstrap()"
        A[Create Required Directories<br/>tmp/pids, logs, src/data] --> B[Initialize Core Components]
        B --> B1[LoggerDefault]
        B --> B2[Config + Environment Validation]
        B --> B3[PFCFApi]
        
        B1 --> C[Configuration Validation]
        B2 --> C
        B3 --> C
        
        C --> D[Create ServiceContainer]
        D --> D1[SessionJsonFileRepository]
        D --> D2[ConditionJsonFileRepository]
        D --> D3[Dependency Injection Container Assembly]
        
        D3 --> E[Create SystemManager]
        E --> E1[DllGatewayServer]
        E --> E2[PortCheckerService]
        E --> E3[MarketDataGatewayService]
        E --> E4[ProcessManagerService]
        E --> E5[StatusChecker]
        
        E1 --> F[SystemManager Complete]
        E2 --> F
        E3 --> F
        E4 --> F
        E5 --> F
    end
```

### 3️⃣ **ServiceContainer Dependency Injection Architecture**

```mermaid
classDiagram
    class ServiceContainer {
        +LoggerInterface logger
        +Config config
        +SessionRepositoryInterface session_repository
        +ConditionRepositoryInterface condition_repository
        +PFCFApi exchange_api
        +exchange_client()
        +exchange_trade()
        +exchange_decimal()
    }
    
    class ApplicationBootstrapper {
        +bootstrap() BootstrapResult
        +create_service_container() ServiceContainer
        +validate_configuration() ValidationResult
        -_create_required_directories()
        -_initialize_core_components()
        -_create_system_manager()
    }
    
    ApplicationBootstrapper --> ServiceContainer
    ServiceContainer --> LoggerDefault
    ServiceContainer --> Config
    ServiceContainer --> SessionJsonFileRepository
    ServiceContainer --> ConditionJsonFileRepository
    ServiceContainer --> PFCFApi
```

---

## Class Responsibilities

### 🎯 **Main Classes and Responsibilities**

#### **Application Layer**

```
CLIApplication
├── 🎮 Responsibility: Application lifecycle management
├── 📝 Functions: 
│   ├─ Start and shutdown application
│   ├─ Exception handling and graceful exit
│   └─ User interface coordination
└── 🔗 Dependencies: ApplicationBootstrapper, SystemManager
```

```
ApplicationBootstrapper  
├── 🏗️ Responsibility: Dependency injection and initialization
├── 📝 Functions:
│   ├─ Create all service instances
│   ├─ Configuration validation
│   ├─ Service container assembly
│   └─ SystemManager construction
└── 🔗 Dependencies: Config, Logger, PFCFApi
```

#### **Infrastructure Layer**

```
ApplicationBootstrapper
├── 🏗️ Responsibility: Application initialization and dependency injection
├── 📝 Functions:
│   ├─ Create required directories (tmp/pids, logs, data)
│   ├─ Initialize core components (Logger, Config, PFCFApi)
│   ├─ Configuration validation (env vars, DLL Gateway settings)
│   ├─ ServiceContainer assembly
│   └─ SystemManager construction
└── 🔗 Manages: Entire application startup process
```

```
ServiceContainer
├── 🎯 Responsibility: Centralized dependency management
├── 📝 Functions:
│   ├─ Dependency injection container
│   ├─ Service instance management
│   ├─ Unified interface access
│   └─ Exchange API proxy
└── 🔗 Manages:
    ├─ LoggerInterface
    ├─ Config
    ├─ SessionRepository
    ├─ ConditionRepository
    └─ PFCFApi (exchange_client, exchange_trade, exchange_decimal)
```

```
SystemManager
├── 🎛️ Responsibility: System component lifecycle management
├── 📝 Functions:
│   ├─ Start/stop trading system
│   ├─ Component status monitoring (ComponentStatus enum)
│   ├─ Health checks (SystemHealth)
│   ├─ System restart and error recovery
│   └─ Runtime tracking
└── 🔗 Manages:
    ├─ MarketDataGatewayService
    ├─ DllGatewayServer  
    ├─ ProcessManagerService
    ├─ PortCheckerService
    └─ StatusChecker
```

##### **Gateway Services Layer**

```
MarketDataGatewayService
├── 📊 Responsibility: Market data infrastructure management
├── 📝 Functions:
│   ├─ ZMQ Publisher initialization and lifecycle
│   ├─ PFCF API callback connection
│   ├─ Real-time quote broadcasting (port 5555)
│   ├─ Data flow management and error handling
│   └─ Gateway status monitoring
└── 🔗 Dependencies: Config, Logger, PFCFApi
```

```
PortCheckerService
├── 🔍 Responsibility: Network port availability validation
├── 📝 Functions:
│   ├─ ZMQ port checking (5555, 5556, 5557)
│   ├─ Port conflict detection
│   ├─ Network resource validation
│   └─ Pre-startup checks
└── 🔗 Dependencies: Config, Logger
```

```
ProcessManagerService
├── ⚙️ Responsibility: Child process lifecycle management
├── 📝 Functions:
│   ├─ PID file management (tmp/pids/)
│   ├─ Process startup and shutdown
│   ├─ Path resolution and validation
│   ├─ Graceful shutdown mechanism
│   └─ Process status tracking
└── 🔗 Dependencies: Config, Logger
```

```
MarketDataGatewayService
├── 📊 Responsibility: Market data publishing
├── 📝 Functions:
│   ├─ ZMQ Publisher initialization
│   ├─ PFCF API callback connection
│   ├─ Real-time quote broadcasting
│   └─ Data flow management
└── 🔗 Dependencies: ZmqPublisher, TickProducer, PFCFApi
```

```
DllGatewayServer
├── 💼 Responsibility: Order execution server
├── 📝 Functions:
│   ├─ ZMQ REQ/REP server
│   ├─ Order request processing
│   ├─ PFCF DLL invocation
│   └─ Execution result response
└── 🔗 Dependencies: PFCFApi, ZMQ REP Socket
```

#### **Business Logic Layer (Interactor Layer)**

```
Use Cases (Various business use cases)
├── 🎯 Responsibility: Business logic encapsulation
├── 📝 Functions:
│   ├─ Business rule execution
│   ├─ Data validation
│   ├─ Error handling
│   └─ Result return
└── 🔗 Dependencies: Entities, Repositories, Services
```

---

## Data Flow Diagrams

### 📈 **Market Data Flow**

```mermaid
sequenceDiagram
    participant PFCF as PFCF Exchange
    participant API as PFCFApi
    participant MDG as MarketDataGatewayService
    participant ZMQ as ZMQ Publisher
    participant Strategy as Strategy Process
    
    PFCF->>API: Real-time quote callback
    API->>MDG: OnTickDataTrade event
    MDG->>ZMQ: Publish market data
    ZMQ->>Strategy: Broadcast to strategy process
    Strategy->>Strategy: Technical analysis and signal generation
```

### 💰 **Order Execution Flow**

```mermaid
sequenceDiagram
    participant Strategy as Strategy Process
    participant Signal as Signal Queue
    participant OrderExec as Order Executor
    participant DGS as DllGatewayServer
    participant PFCF as PFCF Exchange
    
    Strategy->>Signal: Push trading signal
    Signal->>OrderExec: Signal pulled
    OrderExec->>DGS: Send order request (ZMQ REQ)
    DGS->>PFCF: Call DLL to execute order
    PFCF->>DGS: Return execution result
    DGS->>OrderExec: Respond with result (ZMQ REP)
```

### 🔄 **Complete Trading Cycle**

```mermaid
graph TD
    A[PFCF Exchange] --> B[PFCFApi receives quotes]
    B --> C[MarketDataGatewayService]
    C --> D[ZMQ Publisher broadcast]
    D --> E[Strategy Process receives]
    E --> F[Technical analysis]
    F --> G{Generate signal?}
    G -->|Yes| H[Push to Signal Queue]
    G -->|No| E
    H --> I[Order Executor pulls]
    I --> J[Send to DllGatewayServer]
    J --> K[Call PFCF DLL]
    K --> L[Order execution]
    L --> A
```

---

## Component Interaction

### 🎛️ **SystemManager Management Scope and Status Management**

```mermaid
graph TB
    subgraph "ApplicationBootstrapper Initialization"
        AB[ApplicationBootstrapper]
        AB --> SC_CREATE[Create ServiceContainer]
        SC_CREATE --> SM_CREATE[Create SystemManager]
    end
    
    subgraph "SystemManager Jurisdiction"
        SM[SystemManager<br/>📊 ComponentStatus Management]
        
        subgraph "Gateway Components"
            MDG[MarketDataGatewayService<br/>Market Data Gateway<br/>🟢 RUNNING]
            DGS[DllGatewayServer<br/>Order Execution Server<br/>🟢 RUNNING]
        end
        
        subgraph "Support Services"
            PC[PortCheckerService<br/>Port Checking<br/>✅ Pre-check]
            PM[ProcessManagerService<br/>Process Management<br/>📁 PID Management]
            SC[StatusChecker<br/>Status Checking<br/>💚 Health Monitoring]
        end
        
        SM --> |Status Tracking| MDG
        SM --> |Lifecycle| DGS
        SM --> |Pre-check| PC
        SM --> |Process Control| PM
        SM --> |Health Check| SC
    end
    
    subgraph "External Processes (PID Management)"
        SP[Strategy Process<br/>📈 Strategy Process<br/>🆔 strategy.pid]
        OE[Order Executor<br/>💼 Order Execution Process<br/>🆔 order_executor.pid]
    end
    
    SM_CREATE --> SM
    MDG -.->|ZMQ PUB:5555| SP
    SP -.->|ZMQ PUSH:5556| OE
    OE -.->|ZMQ REQ:5557| DGS
    PM -.->|PID Files| SP
    PM -.->|PID Files| OE
```

### 🔄 **Component Status Management**

```mermaid
stateDiagram-v2
    [*] --> STOPPED
    STOPPED --> STARTING : start_component()
    STARTING --> RUNNING : Startup successful
    STARTING --> ERROR : Startup failed
    RUNNING --> STOPPING : stop_component()
    STOPPING --> STOPPED : Stop successful
    STOPPING --> ERROR : Stop failed
    ERROR --> STARTING : restart_component()
    ERROR --> STOPPED : force_stop()
    
    note right of RUNNING
        SystemHealth tracking:
        - uptime_seconds
        - last_check_timestamp
        - component status map
    end note
```

### 🏛️ **Clean Architecture Layers with ServiceContainer Integration**

```mermaid
graph TB
    subgraph "🖥️ Presentation Layer"
        CLI[CLIApplication]
        Controllers[Controllers]
        Views[Views]
        Presenters[Presenters]
    end
    
    subgraph "💼 Application Layer"
        Bootstrap[ApplicationBootstrapper<br/>🏗️ Dependency Injection Coordinator]
        SC[ServiceContainer<br/>🎯 Dependency Management Center]
        UseCases[Use Cases]
    end
    
    subgraph "🎯 Domain Layer"
        Entities[Entities]
        ValueObjects[Value Objects]
        DomainServices[Domain Services]
    end
    
    subgraph "🔧 Infrastructure Layer"
        subgraph "Gateway Services Layer"
            MDG[MarketDataGatewayService]
            PCS[PortCheckerService]
            GIS[GatewayInitializerService]
        end
        
        subgraph "Core Services"
            SystemMgr[SystemManager<br/>📊 Status Management]
            DllGateway[DllGatewayServer]
            ProcessMgr[ProcessManagerService<br/>📁 PID Management]
            StatusCheck[StatusChecker<br/>💚 Health Checking]
        end
        
        Repos[Repositories]
        ZMQ[ZMQ Messaging]
        PFCF[PFCF Client]
    end
    
    CLI --> Bootstrap
    Bootstrap --> SC
    SC --> |Inject Dependencies| Controllers
    SC --> |Inject Dependencies| UseCases
    SC --> |Inject Dependencies| SystemMgr
    
    Controllers --> UseCases
    UseCases --> Entities
    UseCases --> Repos
    
    SystemMgr --> MDG
    SystemMgr --> DllGateway
    SystemMgr --> ProcessMgr
    SystemMgr --> StatusCheck
    SystemMgr --> PCS
    
    SC -.->|Provide Dependencies| Repos
    SC -.->|Provide Dependencies| PFCF
```

---

## OOP Design Principles

### 🎯 **SOLID Principles Application**

#### **S - Single Responsibility Principle**
- ✅ `MarketDataGatewayService`: Only responsible for market data publishing
- ✅ `DllGatewayServer`: Only responsible for order execution
- ✅ `SystemManager`: Only responsible for component lifecycle management

#### **O - Open/Closed Principle**
- ✅ Uses interfaces to define contracts (`MarketDataGatewayServiceInterface`)
- ✅ Can extend new trading strategies without modifying existing code

#### **L - Liskov Substitution Principle**
- ✅ All services implement corresponding interfaces
- ✅ Can easily substitute different implementations

#### **I - Interface Segregation Principle**
- ✅ Separates interfaces for different responsibilities
- ✅ Clients only depend on interfaces they need

#### **D - Dependency Inversion Principle**
- ✅ High-level modules (Use Cases) don't depend on low-level modules (Infrastructure)
- ✅ Both depend on abstractions (Interfaces)

### 🔄 **Design Patterns Application**

#### **Repository Pattern**
```python
# Abstract
SessionRepositoryInterface
# Implementation
SessionInMemoryRepository
SessionJsonFileRepository
```

#### **Dependency Injection Pattern**
```python
# ApplicationBootstrapper assembles all dependencies
system_manager = SystemManager(
    logger=logger,
    market_data_gateway=market_data_gateway,
    dll_gateway_server=dll_gateway_server,
    # ...other dependencies
)
```

#### **Observer Pattern**
```python
# PFCF API callback mechanism
exchange_client.DQuoteLib.OnTickDataTrade += tick_producer.handle_tick_data
```

#### **Command Pattern**
```python
# Use Cases encapsulate business operations
class SendMarketOrderUseCase:
    def execute(self, input_dto: SendMarketOrderInputDto) -> SendMarketOrderOutputDto
```

#### **Service Container Pattern**
```python
# ServiceContainer centrally manages all dependencies
class ServiceContainer:
    def __init__(self, logger, config, session_repository, condition_repository, exchange_api):
        self.logger = logger
        self.config = config
        # ... other dependency injection
```

#### **Bootstrap Pattern**
```python
# ApplicationBootstrapper coordinates initialization flow
class ApplicationBootstrapper:
    def bootstrap(self) -> BootstrapResult:
        # 1. Create directories
        # 2. Initialize core components
        # 3. Configuration validation
        # 4. Create service container
        # 5. Assemble system manager
```

#### **State Management Pattern**
```python
# ComponentStatus enum manages component states
class ComponentStatus(Enum):
    STOPPED = "stopped"
    STARTING = "starting"
    RUNNING = "running"
    STOPPING = "stopping"
    ERROR = "error"
```

---

## 🎯 **Summary**

This architecture's core advantages:

1. **🔧 Modular Design**: Each class has clear responsibilities
2. **🔄 Testability**: Dependency injection makes unit testing easy
3. **📈 Extensibility**: Following SOLID principles makes adding new features easy
4. **🛡️ Maintainability**: Clean Architecture keeps code structure clear
5. **⚡ High Performance**: Multi-process design bypasses Python GIL limitations

Through this documentation, developers can:
- Quickly understand the overall system architecture
- Find specific classes that need modification
- Understand how data flows through the system
- Master component interaction relationships

---

*For more detailed information, see:*
- [ServiceContainer Architecture Update](./SERVICECONTAINER_ARCHITECTURE_UPDATE.md)
- [Class Design Guide](./CLASS_DESIGN_GUIDE.md)
- [Detailed Flow Diagrams](./DETAILED_FLOW_DIAGRAMS.md)