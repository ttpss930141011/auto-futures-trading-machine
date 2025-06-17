# ZeroMQ Selection and Architecture Decisions in This Project

This document details why ZeroMQ was chosen for the "Auto Futures Trading Machine" project, the communication patterns used, data flow, and the reasoning behind these decisions.

---

## 1. Factors for Choosing ZeroMQ

1. **High Performance and Low Latency**
   - ZeroMQ uses non-blocking I/O and event-driven design, suitable for high-frequency market data and real-time trading signal transmission.

2. **Multi-Process/Cross-Machine Communication**
   - The project operates with three independent processes (Gateway, Strategy, Order Executor), and ZeroMQ natively supports multi-process and distributed deployment.

3. **Decoupling and Scalability**
   - Each component only depends on pure Socket interfaces, not directly bound to each other's code, achieving loose coupling.

4. **Mature Ecosystem**
   - ZeroMQ has an active community, comprehensive documentation, and wide language bindings with complete support for Python's `pyzmq`.

5. **Clean Architecture Compliance**
   - Communication details are abstracted in the infrastructure layer, allowing upper UseCase/Domain layers to focus on business logic.

---

## 2. ZeroMQ Communication Patterns

| Pattern     | Roles               | Purpose                        | Example Port |
| ----------- | ------------------- | ------------------------------ | ------------ |
| PUB/SUB     | Gateway → Strategy  | Broadcast market TickEvent     | 5555         |
| PUSH/PULL   | Strategy → OrderExecutor | Transmit TradingSignal    | 5556         |

- **PUB/SUB**: Gateway (`TickProducer`) broadcasts market data via PUB, allowing multiple Strategies to subscribe synchronously.
- **PUSH/PULL**: Multiple Strategies can PUSH signals in parallel to the same PULL, with OrderExecutor responsible for pulling and executing orders.

---

## 3. Data Flow

```plaintext
Exchange API
   │
   ▼
RunGatewayUseCase (TickProducer)
   │ serialize(TickEvent)
   ├─→ PUB socket (tcp://*:5555)
   ▼
Strategy Process (ZmqSubscriber)
   │ deserialize → TickEvent
   ├─→ SupportResistanceStrategy decision
   │    │
   │    └─ If conditions met, serialize(TradingSignal)
   └─→ PUSH socket (tcp://localhost:5556)
       │
       ▼
OrderExecutor Process (ZmqPuller)
   │ deserialize → TradingSignal
   ├─→ OrderExecutor.process_received_signal()
   │    └─ SendMarketOrderUseCase place order
   ▼
Exchange API (order execution)
```  

---

## 4. Decision Rationale

1. **Parallelism**
   - Distributed across multiple OS processes, bypassing Python GIL, fully utilizing multi-core CPUs.

2. **Backpressure & Buffering**
   - ZeroMQ has built-in high water mark (HWM) mechanism, PUB/SUB and PUSH/PULL can set LINGER, HWM to control message buffering.

3. **Fault Tolerance and Monitoring**
   - Component crashes only affect their own process, main program can restart via PID and heartbeat detection.

4. **Horizontal Scalability**
   - Future horizontal scaling of multiple Strategy or OrderExecutor instances, ZeroMQ provides built-in load balancing.

---

## 5. Advantages and Considerations

- **Advantages**:
  - Low latency, high performance, easy to scale, error isolation, code decoupling.

- **Considerations**:
  - Need to manage multi-process lifecycle, logging, and monitoring.
  - ZeroMQ itself doesn't persist messages, requiring retry or persistence implementation at higher layers.

---

## 6. Future Extensions

1. **Multi-Strategy**: Support multiple Strategy Processes for horizontal scaling.
2. **Cross-Host**: Deploy different components on different hosts or containers, forming a microservices architecture.
3. **Complex Patterns**: Such as ROUTER/DEALER for dynamic routing and load balancing.
4. **Monitoring and Health Checks**: Introduce Heartbeat, Prometheus metrics, Supervisor auto-restart.
5. **Message Persistence**: Combine with Kafka or Redis Stream for trading signal guarantee.