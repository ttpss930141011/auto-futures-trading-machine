# 🚀 AllInOneController Startup Process & Data Flow Guide

## 📋 Overview

**AllInOneController** is the unified entry point for the futures trading system, responsible for validating prerequisites and starting the entire distributed trading architecture.

## 🎯 Core Responsibilities

1. **Prerequisites Validation** - Ensure the system can start safely
2. **Distributed Component Coordination** - Launch multi-process architecture through SystemManager
3. **User Feedback** - Provide clear startup status and error information

## 🔍 Detailed Initialization Process

### Phase 1: Prerequisites Check

```mermaid
flowchart TD
    A[AllInOneController.execute] --> B{User logged in?}
    B -->|No| C[Show error: Please login first]
    B -->|Yes| D[ApplicationStartupStatusUseCase.execute]
    D --> E{Product registered?}
    E -->|No| F[Show error: Please register product first]
    E -->|Yes| G{Account selected?}
    G -->|No| H[Show error: Please select trading account]
    G -->|Yes| I{Trading conditions defined?}
    I -->|No| J[Show error: Please define trading conditions]
    I -->|Yes| K[Prerequisites passed]
```

#### Check Items Details

| Check Item | Implementation Location | Failure Impact |
|------------|------------------------|----------------|
| `logged_in` | SessionRepository.is_user_logged_in() | Cannot access PFCF API |
| `item_registered` | StatusChecker via Use Case check | No market data available |
| `order_account_selected` | StatusChecker account configuration check | Cannot execute orders |
| `has_conditions` | StatusChecker trading conditions check | Strategy cannot run |

### Phase 2: System Component Startup

```mermaid
sequenceDiagram
    participant AC as AllInOneController
    participant SM as SystemManager
    participant MG as MarketDataGateway
    participant DG as DllGatewayServer
    participant PM as ProcessManager
    
    AC->>SM: start_trading_system()
    
    Note over SM: Gateway Startup (Highest Priority)
    SM->>SM: _start_gateway()
    SM->>SM: check_port_availability()
    SM->>MG: initialize_market_data_publisher()
    Note right of MG: Create ZMQ Publisher (5555)<br/>Create TickProducer
    SM->>MG: connect_exchange_callbacks()
    Note right of MG: Register PFCF OnTickDataTrade<br/>Connect to TickProducer
    SM->>DG: start()
    Note right of DG: Start ZMQ REP Server (5557)<br/>Begin listening for order requests
    
    Note over SM: Strategy Process Startup
    SM->>PM: start_strategy_process()
    Note right of PM: Execute run_strategy.py<br/>Connect ZMQ SUB (5555)<br/>Start support/resistance strategy
    
    Note over SM: Order Executor Process Startup
    SM->>PM: start_order_executor_process()
    Note right of PM: Execute run_order_executor_gateway.py<br/>Connect ZMQ PULL (5556)<br/>Connect ZMQ REQ (5557)
    
    SM-->>AC: SystemStartupResult
    AC->>AC: _display_startup_results()
```

## 🌐 Distributed Architecture & Data Flow

### Three-Process Architecture Overview

```mermaid
graph TB
    subgraph "Main Process (app.py)"
        CLI["CLIApplication<br/>📱 User Interface<br/>Thread: Main"]
        DGS["DllGatewayServer<br/>🔄 Port 5557 ZMQ REP<br/>Thread: Background"]
        MDP["MarketDataPublisher<br/>📡 Port 5555 ZMQ PUB<br/>Thread: ZMQ"]
        TP["TickProducer<br/>🔄 Data Converter<br/>Thread: PFCF Callback"]
        PFCF["PFCF API<br/>💼 DLL Client<br/>Thread: Main"]
    end
    
    subgraph "Strategy Process (run_strategy.py)"
        SS["StrategySubscriber<br/>📡 ZMQ SUB: 5555<br/>Process: Separate"]
        SRS["SupportResistanceStrategy<br/>🧠 Trading Algorithm<br/>Process: Separate"]
        SP["SignalPublisher<br/>📤 ZMQ PUSH: 5556<br/>Process: Separate"]
    end
    
    subgraph "Order Executor Process (run_order_executor_gateway.py)"
        SR["SignalReceiver<br/>📥 ZMQ PULL: 5556<br/>Process: Separate"]
        GC["DllGatewayClient<br/>📞 ZMQ REQ: 5557<br/>Process: Separate"]
    end
    
    PFCF -->|OnTickDataTrade| TP
    TP -->|serialize TickEvent| MDP
    MDP -->|TICK_TOPIC| SS
    SS -->|Tick Data| SRS
    SRS -->|TradingSignal| SP
    SP -->|serialize Signal| SR
    SR -->|OrderRequest| GC
    GC -->|send_order| DGS
    DGS -->|DLL Call| PFCF
```

### Key Component Functionality Details

#### 🔧 TickProducer (Market Data Converter)

**Location**: `src/infrastructure/pfcf_client/tick_producer.py`

**Core Functions**:
- Receive PFCF API `OnTickDataTrade` callbacks
- Convert raw data to standardized `Tick` and `TickEvent` objects
- Serialize data using msgpack
- Broadcast through ZMQ Publisher to port 5555

```python
def handle_tick_data(self, commodity_id, match_price, ...):
    # 1. Data cleaning and conversion
    price_value = float(match_price)
    tick = Tick(commodity_id=commodity_id.upper(), match_price=price_value)
    
    # 2. Create event
    tick_event = TickEvent(datetime.now(), tick)
    
    # 3. Serialize and publish
    serialized_event = serialize(tick_event)
    self.tick_publisher.publish(TICK_TOPIC, serialized_event)
```

#### 💼 DllGatewayServer (Order Execution Gateway)

**Location**: `src/infrastructure/services/dll_gateway_server.py`

**Core Functions**:
- Listen for ZMQ REP requests on port 5557
- Centralized PFCF DLL access ensuring thread safety
- Supported operations: `send_order`, `get_positions`, `health_check`

```python
def _process_request(self, raw_request):
    request_data = json.loads(raw_request.decode('utf-8'))
    operation = request_data.get("operation")
    
    if operation == "send_order":
        return self._handle_send_order(request_data)
    elif operation == "get_positions":
        return self._handle_get_positions(request_data)
    elif operation == "health_check":
        return self._handle_health_check()
```

## 📊 Data Flow Sequence Diagram

### Complete Trading Lifecycle

```mermaid
sequenceDiagram
    participant Exchange as Taiwan Futures Exchange
    participant PFCF as PFCF API<br/>(Main Process)
    participant TP as TickProducer<br/>(Main Process)
    participant ZMQ1 as ZMQ Publisher<br/>Port 5555<br/>(Main Process)
    participant Strategy as Strategy Process<br/>(Separate Process)
    participant ZMQ2 as ZMQ Signal<br/>Port 5556<br/>(Strategy Process)
    participant OrderExec as Order Executor Process<br/>(Separate Process)
    participant ZMQ3 as ZMQ Request<br/>Port 5557<br/>(Order Executor)
    participant DGS as DllGatewayServer<br/>(Main Process)
    
    Note over Exchange, DGS: Market Data Flow (Millisecond Level)
    Exchange->>PFCF: Real-time price data
    PFCF->>TP: OnTickDataTrade callback
    TP->>TP: Create TickEvent
    TP->>ZMQ1: publish(TICK_TOPIC, data)
    ZMQ1->>Strategy: broadcast tick data
    
    Note over Strategy: Strategy Analysis (< 5ms)
    Strategy->>Strategy: Support/resistance analysis
    Strategy->>Strategy: Generate trading signal
    Strategy->>ZMQ2: PUSH TradingSignal
    
    Note over OrderExec, DGS: Order Execution Flow (< 10ms)
    ZMQ2->>OrderExec: PULL TradingSignal
    OrderExec->>OrderExec: Build OrderRequest
    OrderExec->>ZMQ3: REQ send_order
    ZMQ3->>DGS: Forward order request
    DGS->>PFCF: DLL.Order() call
    PFCF->>Exchange: Order submission
    Exchange-->>PFCF: Execution report
    PFCF-->>DGS: OrderResult
    DGS-->>ZMQ3: Return execution result
    ZMQ3-->>OrderExec: REP response
```

## ⚡ Performance Characteristics

### Latency Metrics

| Stage | Target Latency | Key Factors |
|-------|----------------|-------------|
| Tick Processing | < 1ms | ZMQ + msgpack serialization |
| Strategy Decision | < 5ms | Support/resistance algorithm optimization |
| Order Execution | < 10ms | DLL Gateway + network |

### ZMQ Communication Patterns

| Port | Pattern | Purpose | Characteristics |
|------|---------|---------|----------------|
| 5555 | PUB/SUB | Market data broadcast | High throughput, unidirectional |
| 5556 | PUSH/PULL | Trading signal transmission | Load balancing, reliable |
| 5557 | REQ/REP | Order execution requests | Synchronous, with response |

## 🔧 Failure Handling Mechanisms

### Component Startup Failure

```mermaid
flowchart TD
    A[Component startup failed] --> B{Is Gateway?}
    B -->|Yes| C[Check port occupancy<br/>Reinitialize ZMQ<br/>Reconnect PFCF API]
    B -->|No| D{Is Strategy?}
    D -->|Yes| E[Check ZMQ connection<br/>Restart strategy process]
    D -->|No| F[Order Executor issue<br/>Check Gateway connection]
    
    C --> G[Automatic retry mechanism]
    E --> G
    F --> G
    
    G --> H{Retry successful?}
    H -->|Yes| I[Resume normal operation]
    H -->|No| J[Log error<br/>Notify user]
```

### Runtime Error Recovery

| Error Type | Detection Method | Recovery Strategy |
|------------|------------------|-------------------|
| ZMQ connection interruption | Heartbeat check | Automatic reconnection |
| PFCF API disconnection | Callback stopped | Re-login |
| Process crash | Process monitoring | Automatic restart |
| Memory leak | Resource monitoring | Periodic restart |

## 🎯 Key Design Decisions

### Why Use Multi-Process?

1. **Bypass Python GIL** - Achieve true parallel processing
2. **Fault Isolation** - Single process crash doesn't affect other components
3. **Resource Separation** - Different components can be independently optimized
4. **Security Isolation** - Only main process holds PFCF credentials

### Why Use DLL Gateway?

1. **Centralized Security** - Single process manages DLL access
2. **Thread Safety** - Avoid multi-threaded DLL call issues
3. **Connection Pooling** - Efficiently manage PFCF connections
4. **Unified Error Handling** - Centralized error handling and logging

### ProcessManagerService Functionality Clarification

**Actually Used Methods**:
- `start_strategy()`: Start `run_strategy.py` as independent process ✅ **In Use**
- `start_order_executor()`: Start `run_order_executor_gateway.py` as independent process ✅ **In Use**
- `cleanup_processes()`: Clean up all processes and threads ✅ **In Use**

**Cleaned Dead Code**:
- `start_gateway_thread(gateway_runner)`: ✅ **Removed from Interface and implementation classes**
- `gateway_thread` and `gateway_running` attributes: ✅ **Completely removed**

**Cleanup Result**: All unused gateway thread related code has been safely removed, making the system more concise and clear.

## 💡 Usage Guide

### Normal Startup Process

1. Login to system (Option 1)
2. Register product (Option 3)  
3. Select trading account (Option 5)
4. Create trading conditions (Option 4)
5. One-click startup (Option 10) ← **AllInOneController**

### Post-Startup Status Check

- **Gateway**: `✓ Running` - Market data and order execution services running
- **Strategy**: `✓ Running` - Support/resistance strategy analyzing market
- **Order Executor**: `✓ Running` - Automatic order execution ready

### Troubleshooting

| Status Display | Possible Cause | Solution |
|----------------|----------------|----------|
| Gateway `✗ Error` | Port occupied | Check other applications, restart system |
| Strategy `✗ Stopped` | ZMQ connection failed | Confirm Gateway running, check firewall |
| Order Executor `✗ Error` | Gateway unreachable | Restart Gateway, check port 5557 |

---

## 📋 Architecture Description

*This architecture achieves the performance requirements of high-frequency trading systems while maintaining the flexibility and maintainability of Python development.*

### ⚠️ Important Limitations

**Broker Dependency**: This system is highly coupled with Taiwan Unified Futures (PFCF) DLL. If you need to migrate to other brokers, please refer to the [DLL Porting Guide](../architecture/DLL_PORTING_GUIDE.md).