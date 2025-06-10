# Auto Futures Trading Machine - Architecture Overview

## 🏗️ System Architecture (Current Implementation)

The system uses a **DLL Gateway Architecture** with enhanced security, centralized exchange access, and multi-process communication via ZeroMQ.

## 📊 Visual Architecture

```
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                                    MAIN PROCESS (app.py)                                   │
│ ┌─────────────────────────────────────────────────────────────────────────────────────┐ │
│ │                              CLI Interface & Core Services                          │ │
│ │  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐                      │ │
│ │  │ AllInOneController│  │ UserLoginController│  │ Various Controllers │                      │ │
│ │  └─────────────────┘  └─────────────────┘  └─────────────────┘                      │ │
│ └─────────────────────────────────────────────────────────────────────────────────────┘ │
│ ┌─────────────────────────────────────────────────────────────────────────────────────┐ │
│ │                            DLL Gateway Server                                       │ │
│ │  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐                      │ │
│ │  │ PFCF API Client │  │ Exchange DLL    │  │ ZMQ REP Server  │                      │ │
│ │  │ (Single Instance)│  │ (Centralized)   │  │ (Port 5557)     │                      │ │
│ │  └─────────────────┘  └─────────────────┘  └─────────────────┘                      │ │
│ └─────────────────────────────────────────────────────────────────────────────────────┘ │
│ ┌─────────────────────────────────────────────────────────────────────────────────────┐ │
│ │                           Gateway Use Case                                          │ │
│ │  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐                      │ │
│ │  │ TickProducer    │  │ RunGatewayUseCase│ │ ZMQ PUB Socket  │                      │ │
│ │  │ (Market Data)   │  │ (Orchestrator)   │  │ (Port 5555)     │                      │ │
│ │  └─────────────────┘  └─────────────────┘  └─────────────────┘                      │ │
│ └─────────────────────────────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────────────────────────┘
                                            │
                                            │ ZMQ Communication
                                            │ (Secure & Reliable)
┌───────────────────────────────────────────┼───────────────────────────────────────────────┐
│                                           │                                               │
│                                           ▼                                               │
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                                 STRATEGY PROCESS                                           │
│ ┌─────────────────────────────────────────────────────────────────────────────────────┐ │
│ │                            Market Data Processing                                   │ │
│ │  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐                      │ │
│ │  │ ZMQ SUB Socket  │  │ TickEvent       │  │ SupportResistance│                      │ │
│ │  │ (Port 5555)     │  │ Deserializer    │  │ Strategy         │                      │ │
│ │  └─────────────────┘  └─────────────────┘  └─────────────────┘                      │ │
│ └─────────────────────────────────────────────────────────────────────────────────────┘ │
│ ┌─────────────────────────────────────────────────────────────────────────────────────┐ │
│ │                            Signal Generation                                        │ │
│ │  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐                      │ │
│ │  │ Condition       │  │ TradingSignal   │  │ ZMQ PUSH Socket │                      │ │
│ │  │ Repository      │  │ Generator       │  │ (Port 5556)     │                      │ │
│ │  └─────────────────┘  └─────────────────┘  └─────────────────┘                      │ │
│ └─────────────────────────────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────────────────────────┘
                                            │
                                            │ Trading Signals
                                            │ (ZMQ PUSH/PULL)
                                            ▼
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                              ORDER EXECUTOR PROCESS                                        │
│ ┌─────────────────────────────────────────────────────────────────────────────────────┐ │
│ │                            Signal Processing                                        │ │
│ │  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐                      │ │
│ │  │ ZMQ PULL Socket │  │ TradingSignal   │  │ OrderExecutor   │                      │ │
│ │  │ (Port 5556)     │  │ Deserializer    │  │ Gateway         │                      │ │
│ │  └─────────────────┘  └─────────────────┘  └─────────────────┘                      │ │
│ └─────────────────────────────────────────────────────────────────────────────────────┘ │
│ ┌─────────────────────────────────────────────────────────────────────────────────────┐ │
│ │                           Gateway Communication                                     │ │
│ │  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐                      │ │
│ │  │ DLL Gateway     │  │ SendMarketOrder │  │ ZMQ REQ Client  │                      │ │
│ │  │ Client          │  │ DTO Creation    │  │ (Port 5557)     │                      │ │
│ │  └─────────────────┘  └─────────────────┘  └─────────────────┘                      │ │
│ └─────────────────────────────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────────────────────────┘
                                            │
                                            │ Order Execution Requests
                                            │ (Secure REQ/REP)
                                            ▼
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                              🏛️ EXCHANGE API                                              │
│                        (PFCF - Polaris Futures Capital Future)                           │
└─────────────────────────────────────────────────────────────────────────────────────────┘
```

## 🔄 Data Flow Overview

### 1. Market Data Flow (Real-time)
```
Exchange API → DLL Gateway Server → TickProducer → ZMQ PUB → Strategy Process
```

### 2. Trading Signal Flow
```
Strategy Process → Condition Analysis → TradingSignal → ZMQ PUSH → Order Executor
```

### 3. Order Execution Flow (DLL Gateway)
```
Order Executor → DLL Gateway Client → ZMQ REQ → DLL Gateway Server → Exchange API
```

## 🏗️ Key Architectural Components

### **Main Process (app.py)**
- **Purpose**: Hosts CLI interface and centralized DLL Gateway Server
- **Components**:
  - CLI Controllers (User interaction)
  - DLL Gateway Server (Centralized exchange access)
  - RunGatewayUseCase (Market data publishing)
- **Ports**: 
  - `5555` (ZMQ PUB for market data)
  - `5557` (ZMQ REP for order execution)

### **Strategy Process** 
- **Purpose**: Processes market data and generates trading signals
- **Input**: TickEvents from Gateway (via ZMQ SUB)
- **Output**: TradingSignals to OrderExecutor (via ZMQ PUSH)
- **Logic**: SupportResistanceStrategy with configurable conditions

### **Order Executor Process**
- **Purpose**: Executes trading orders through DLL Gateway
- **Input**: TradingSignals from Strategy (via ZMQ PULL)
- **Output**: Order execution via DLL Gateway Client
- **Security**: No direct DLL access - all orders through gateway

## 🛡️ Security & Reliability Features

### **DLL Gateway Architecture Benefits**
- ✅ **Single DLL Instance**: Eliminates duplicate event issues
- ✅ **Centralized Security**: No credentials in child processes  
- ✅ **Process Isolation**: Strategy and OrderExecutor in separate processes
- ✅ **Automatic Recovery**: Gateway client handles connection failures
- ✅ **Zero User Impact**: Same CLI workflow, enhanced backend

### **Communication Security**
- **ZeroMQ Patterns**: PUB/SUB, PUSH/PULL, REQ/REP
- **Serialization**: msgpack with custom handlers
- **Error Handling**: Automatic retry with exponential backoff
- **Timeout Management**: Configurable timeouts for all operations

## 🚀 User Workflow (Unchanged)

The DLL Gateway architecture maintains the exact same user experience:

```bash
python app.py
# 1. Login (Option 1)
# 2. Register Item (Option 3) 
# 3. Create Condition (Option 4)
# 4. Select Order Account (Option 5)
# 5. Start All-in-One System (Option 10)
```

When Option 10 is selected:
1. ✅ Verifies all prerequisites
2. ✅ Starts DLL Gateway Server in main process
3. ✅ Launches Strategy process with ZMQ communication
4. ✅ Launches Order Executor process with Gateway client
5. ✅ Returns to CLI menu while components run in background
6. ✅ Automatic cleanup on application exit

## 📋 Technology Stack

- **Language**: Python 3.12+
- **Communication**: ZeroMQ (high-performance messaging)
- **Architecture**: Clean Architecture with SOLID principles
- **Testing**: pytest with 229 comprehensive tests
- **Serialization**: msgpack for efficient data transfer
- **Exchange API**: PFCF (Polaris Futures Capital Future)

## 📊 Comparison: Main Branch vs Development Branch

| Aspect | Main Branch | Development Branch (Current) |
|--------|-------------|------------------------------|
| **DLL Access** | Multiple instances | Single centralized instance |
| **Security** | Credentials in child processes | No credentials in child processes |
| **Event Duplication** | Possible duplicate events | Eliminated through gateway |
| **Process Architecture** | Multi-process with direct DLL | Multi-process with gateway proxy |
| **User Workflow** | CLI menu system | **Identical** CLI menu system |
| **Reliability** | Direct API calls | Gateway with retry/recovery |
| **Testing** | Comprehensive | **Enhanced** with gateway tests |

## 🎯 Benefits of Current Architecture

1. **Enhanced Security**: Credentials never leave main process
2. **Improved Reliability**: Single DLL instance prevents conflicts
3. **Better Scalability**: Gateway can handle multiple order executors
4. **Easier Testing**: Clear separation of concerns
5. **Production Ready**: Comprehensive error handling and recovery
6. **Zero Migration Cost**: Same user interface and workflow

This architecture represents a significant advancement in trading system design while maintaining complete backward compatibility with the user experience.