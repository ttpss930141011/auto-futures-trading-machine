# 🧭 Design Decisions

> *Why we chose certain technologies and patterns*

## 1. ZeroMQ for IPC

- **Why**: Python's GIL limits threading; separate processes communicate efficiently.
- **Chosen Patterns**:
  - **PUB/SUB** for market data (one-to-many).
  - **PUSH/PULL** for trading signals (load balancing).
  - **REQ/REP** for synchronous order execution (reliable request/response).
- **Alternative**: RabbitMQ (higher latency, broker needed). Redis Pub/Sub (requires Redis server).

## 2. Event-Driven Architecture

- **Why**: React to market events in real time, decouple components.
- **Practiced With**: tick → `TickEvent` → strategy → `TradingSignal` → executor → `OrderEvent`.
- **Benefit**: Scalability, resilience, clear data flow.

## 3. Clean Architecture

- **Why**: Enforce separation of concerns and testability.
- **Layers**:
  1. **Presentation**: CLI controllers
  2. **Application**: use cases, bootstrapper
  3. **Domain**: business logic, DTOs
  4. **Infrastructure**: ZeroMQ, file repos, DLL Gateway

## 4. SystemManager Pattern

- **Why**: Centralize infrastructure lifecycle (start, stop, health check).
- **Benefit**: Removes global variables, encapsulates setup/cleanup logic.

## 5. DTOs and Result Objects

- **Why**: Avoid multiple return values and unclear contracts.
- **Example**: `SystemStartupResult`, `ProcessResult`.

## 6. MessagePack Serialization

- **Why**: Faster and smaller than JSON; no broker.
- **Custom Types**: datetime, enums handled with custom handlers.

## 7. Simplified app.py

- **Before**: 155-line `main()` with mixed concerns.
- **After**: <30 lines, delegates to `ApplicationBootstrapper` and `CLIApplication`.

---

*Each decision improves maintainability, performance, or developer experience.* 