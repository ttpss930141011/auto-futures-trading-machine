# ZeroMQ 在本專案的選型與架構決策

本文件詳細說明為何在「自動期貨交易機器人」專案採用 ZeroMQ，所使用的通訊模式（pattern）、資料流（flow）及背後的決策理由。

---

## 一、選擇 ZeroMQ 的因素

1. **高效能與低延遲**
   - ZeroMQ 採用非阻塞 I/O、事件驅動設計，適合高頻率、市場數據或交易訊號的即時傳輸。

2. **多進程／跨機器通訊**
   - 專案以三個獨立進程（Gateway、Strategy、Order Executor）運作，ZeroMQ 天生支援多進程與分散式部署。

3. **解耦與可擴充性**
   - 各元件只需依賴純粹的 Socket 接口，不直接綁定彼此程式碼，達到松耦合（loose coupling）。

4. **成熟生態**
   - ZeroMQ 社群活躍、文件齊全，且語言綁定廣泛，對 Python 的 `pyzmq` 有完整支援。

5. **符合 Clean Architecture**
   - 將通訊細節抽象在基礎設施層（infrastructure），上層 UseCase/Domain 層專注業務邏輯。

---

## 二、ZeroMQ 通訊模式（Pattern）

| 模式     | 角色               | 用途                           | 範例端口 |
| -------- | ------------------ | ------------------------------ | -------- |
| PUB/SUB  | Gateway → Strategy | 播送市場 TickEvent（行情）       | 5555     |
| PUSH/PULL| Strategy → OrderExecutor | 傳遞交易訊號（TradingSignal） | 5556     |

- **PUB/SUB**：Gateway (`TickProducer`) 將市場數據以 PUB 廣播，允許多個 Strategy 同步訂閱。
- **PUSH/PULL**：多個 Strategy 可並行 PUSH 訊號至同一個 PULL，OrderExecutor 負責拉取並執行下單。

---

## 三、資料流（Flow）

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
   ├─→ SupportResistanceStrategy 決策
   │    │
   │    └─ 若條件達成，serialize(TradingSignal)
   └─→ PUSH socket (tcp://localhost:5556)
       │
       ▼
OrderExecutor Process (ZmqPuller)
   │ deserialize → TradingSignal
   ├─→ OrderExecutor.process_received_signal()
   │    └─ SendMarketOrderUseCase 下單
   ▼
Exchange API (下單)
```  

---

## 四、決策理由

1. **Parallelism (併發)**
   - 分散在多個 OS 進程，避開 Python GIL，充分利用多核心 CPU。

2. **Backpressure & Buffering**
   - ZeroMQ 自帶高水位（HWM）機制，PUB/SUB 與 PUSH/PULL 可設定 LINGER、HWM，以控制訊息緩衝。

3. **容錯及監控**
   - 各元件崩潰只影響自身進程，主程式可透過 PID 與心跳檢測重啟。

4. **可水平擴充**
   - 未來可水平擴展多個 Strategy 或 OrderExecutor 範例，ZeroMQ 自帶 load balancing。

---

## 五、優勢與考量

- **優勢**：
  - 低延遲、高效能、易於擴充、錯誤隔離、程式碼解耦。

- **考量**：
  - 需管理多進程生命週期、日誌與監控。
  - ZeroMQ 本身不做訊息持久化，需在上層自行重試或落盤。

---

## 六、未來擴展

1. **多策略**：支援多個 Strategy Process，實現水平擴展。
2. **跨主機**：將不同元件部屬於不同主機或容器，形成微服務架構。
3. **複雜 Pattern**：如 ROUTER/DEALER 做動態路由與負載平衡。
4. **監控與健康檢查**：引入 Heartbeat、Prometheus 指標、Supervisor 自動重啟。
5. **訊息持久化**：結合 Kafka 或 Redis Stream 做交易訊號保證。
