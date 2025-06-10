# 🔌 Process Communication Patterns

> *Overview of how different processes exchange data*

## 1. PUB/SUB (Publish-Subscribe)

```
Gateway (PUB) --ticks--> Strategy (SUB)
```
- **Purpose**: Broadcast market tick events to one or many strategy processes.
- **Benefits**: Loose coupling, multiple subscribers, no blocking on publisher.
- **Usage**: `ZmqPublisher` binds to `tcp://*:5555`; `ZmqSubscriber` connects.

## 2. PUSH/PULL

```
Strategy (PUSH) --signals--> Executor (PULL)
```
- **Purpose**: Queue trading signals for the order executor, load balancing across executors.
- **Benefits**: Built-in queuing, fair distribution, simple flow control.
- **Usage**: `ZmqPusher` connects to `tcp://localhost:5556`; `ZmqPuller` binds.

## 3. REQ/REP (Request-Reply)

```
Executor (REQ) --order--> Gateway Server (REP)
```
- **Purpose**: Send synchronous order requests to the centralized DLL Gateway.
- **Benefits**: Guaranteed correlation of request/response, simple error handling.
- **Usage**: `ZmqClient` (REQ) connects to `tcp://localhost:5557`; `ZmqServer` (REP) binds.

## 4. Process Lifecycle Management

- **Startup**: `ApplicationBootstrapper` launches gateway, strategy, executor as separate processes.
- **Health Checks**: `SystemManager.get_system_health()` polls each component.
- **Shutdown**: Graceful termination signals sent to each process, ensuring cleanup.

## 📊 Diagram

```mermaid
graph TB
    subgraph Gateway Process
        GW_PUB[TickPublisher(pub:5555)]
        GW_REP[OrderServer(rep:5557)]
    end
    subgraph Strategy Process
        ST_SUB[TickSubscriber]
        ST_PUSH[SignalPusher(push:5556)]
    end
    subgraph Executor Process
        EX_PULL[SignalPuller]
        EX_REQ[OrderClient]
    end

    GW_PUB --> ST_SUB
    ST_PUSH --> EX_PULL
    EX_REQ --> GW_REP
```

## 🚀 Why These Patterns?

- **Decoupling**: Each role (market data, strategy, execution) runs independently.
- **Scalability**: Spin up multiple strategy or executor processes without code changes.
- **Resilience**: A crashed strategy doesn't bring down the gateway or executor.
- **Performance**: ZeroMQ's efficient transport avoids Python GIL bottlenecks.

---

*These patterns form the backbone of our event-driven, multi-process trading system.* 