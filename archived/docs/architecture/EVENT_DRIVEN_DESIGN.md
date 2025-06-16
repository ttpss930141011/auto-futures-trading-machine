# ⚡ Event-Driven Design: The Pulse of Our Trading System

> *"In trading, events don't wait for you. Your system shouldn't either."*

## 🌊 What is Event-Driven Architecture?

Imagine a trading floor. A price changes - that's an **event**. A trader shouts an order - another **event**. Someone confirms the trade - yet another **event**. Our system mirrors this natural flow.

### Traditional vs Event-Driven

```python
# Traditional: Polling (like constantly asking "Are we there yet?")
while True:
    price = get_current_price()
    if price > threshold:
        place_order()
    time.sleep(1)  # Waste 1 second between checks!

# Event-Driven: Reactive (like having a notification)
@on_tick_received
def handle_tick(tick_event):
    if tick_event.price > threshold:
        emit(TradingSignal(action=BUY))
```

**The difference?** Microseconds vs seconds. In trading, that's profit vs loss.

## 🎭 The Cast: Our Event Types

### 1. TickEvent: The Market Heartbeat

```python
@dataclass
class TickEvent:
    """Raw market data - the source of all truth"""
    timestamp: datetime
    instrument: str
    bid_price: float
    ask_price: float
    bid_volume: int
    ask_volume: int
    
    def spread(self) -> float:
        return self.ask_price - self.bid_price
```

**Born in**: Gateway Process  
**Consumed by**: Strategy Process  
**Frequency**: 50,000+ per second  

### 2. TradingSignal: The Decision

```python
@dataclass
class TradingSignal:
    """A strategy's decision to trade"""
    timestamp: datetime
    action: OrderOperation  # BUY or SELL
    instrument: str
    trigger_price: float
    quantity: int
    strategy_name: str
    confidence: float  # 0.0 to 1.0
    
    def is_high_confidence(self) -> bool:
        return self.confidence > 0.8
```

**Born in**: Strategy Process  
**Consumed by**: Order Executor  
**Frequency**: 10-100 per minute  

### 3. OrderEvent: The Commitment

```python
@dataclass
class OrderEvent:
    """An order sent to the exchange"""
    order_id: str
    signal_id: str  # Links back to TradingSignal
    status: OrderStatus
    filled_quantity: int
    fill_price: Optional[float]
    timestamp: datetime
    
    def is_fully_filled(self) -> bool:
        return self.status == OrderStatus.FILLED
```

**Born in**: Order Executor  
**Consumed by**: Risk Manager, Logger  
**Frequency**: Matches TradingSignal frequency  

## 🏗️ The Architecture: Event Flow

### The Journey of a Trade

```
1. Market Data Arrives
   Exchange ──► Gateway
                  │
                  ▼
           Create TickEvent
                  │
                  ▼
        ZMQ PUB (Port 5555)
                  │
                  ▼

2. Strategy Processes
        ZMQ SUB receives
                  │
                  ▼
         Deserialize TickEvent
                  │
                  ▼
    Support/Resistance Analysis
                  │
                  ▼
      Create TradingSignal
                  │
                  ▼
      ZMQ PUSH (Port 5556)
                  │
                  ▼

3. Order Execution
        ZMQ PULL receives
                  │
                  ▼
      Deserialize TradingSignal
                  │
                  ▼
        Validate & Enrich
                  │
                  ▼
     Send to DLL Gateway
                  │
                  ▼
        Create OrderEvent
                  │
                  ▼
           Log & Monitor
```

## 🎯 Why Event-Driven?

### 1. **Decoupling**: Components Don't Know Each Other

```python
# Bad: Tight coupling
class Strategy:
    def __init__(self):
        self.executor = OrderExecutor()  # Direct dependency!
    
    def process_tick(self, tick):
        if self.should_trade(tick):
            self.executor.place_order(...)  # Direct call!

# Good: Event-driven decoupling
class Strategy:
    def __init__(self, event_publisher):
        self.publisher = event_publisher
    
    def process_tick(self, tick):
        if self.should_trade(tick):
            signal = TradingSignal(...)
            self.publisher.publish(signal)  # Fire and forget!
```

### 2. **Scalability**: Add More Consumers Easily

```
One Gateway, Multiple Strategies:

         Gateway
            │
    ┌───────┼───────┐
    ▼       ▼       ▼
Strategy1 Strategy2 Strategy3

Each runs independently!
```

### 3. **Resilience**: Failure Isolation

```python
# If Strategy2 crashes:
Gateway:     ✓ Still running
Strategy1:   ✓ Still running  
Strategy2:   ✗ Crashed (but isolated!)
Strategy3:   ✓ Still running
Executor:    ✓ Still running

# The system continues!
```

### 4. **Performance**: True Parallelism

Traditional threading in Python:
```
Thread 1: ━━━━━┫ GIL ┣━━━━━━┫ GIL ┣━━━━━
Thread 2: ━━━━━━━━━━━┫ GIL ┣━━━━━━━━━━━━
          Only one thread runs at a time!
```

Event-driven with processes:
```
Process 1: ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Process 2: ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Process 3: ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
           All run truly in parallel!
```

## 🎨 Event Patterns We Use

### 1. **Publish-Subscribe**: Market Data Distribution

```python
# Publisher (Gateway)
class TickPublisher:
    def publish_tick(self, tick: TickEvent):
        serialized = msgpack.packb(tick)
        self.socket.send_multipart([
            b"TICK." + tick.instrument.encode(),
            serialized
        ])

# Subscriber (Strategy)
class TickSubscriber:
    def subscribe(self, instruments: List[str]):
        for instrument in instruments:
            self.socket.subscribe(f"TICK.{instrument}")
    
    def receive_tick(self) -> Optional[TickEvent]:
        if self.socket.poll(timeout=10):
            topic, data = self.socket.recv_multipart()
            return msgpack.unpackb(data)
```

### 2. **Request-Reply**: Order Execution

```python
# Client (Order Executor)
def send_order(self, order: Order) -> OrderResult:
    request = {"operation": "send_order", "order": order}
    self.socket.send_json(request)
    
    response = self.socket.recv_json()
    return OrderResult(**response)

# Server (DLL Gateway)
def handle_request(self, request: dict) -> dict:
    if request["operation"] == "send_order":
        result = self.exchange_api.place_order(request["order"])
        return {"success": result.success, "order_id": result.id}
```

### 3. **Push-Pull**: Signal Pipeline

```python
# Pusher (Strategy)
def emit_signal(self, signal: TradingSignal):
    # Fire and forget - no waiting
    self.push_socket.send(msgpack.packb(signal))

# Puller (Order Executor)
def process_signals(self):
    while self.running:
        if self.pull_socket.poll(timeout=100):
            data = self.pull_socket.recv()
            signal = msgpack.unpackb(data)
            self.execute_signal(signal)
```

## 🏃 Event Processing Strategies

### 1. **At-Most-Once**: Fire and Forget

```python
# Good for: High-frequency data where losing some is OK
def publish_tick(self, tick):
    try:
        self.socket.send(tick, zmq.NOBLOCK)
    except zmq.Again:
        # Buffer full, drop the tick
        self.dropped_ticks += 1
```

### 2. **At-Least-Once**: Guaranteed Delivery

```python
# Good for: Critical signals that must be processed
def send_signal_reliable(self, signal):
    retries = 3
    while retries > 0:
        self.socket.send(signal)
        if self.wait_for_ack(timeout=1000):
            break
        retries -= 1
    else:
        raise SignalDeliveryError("Failed to deliver signal")
```

### 3. **Exactly-Once**: Idempotent Processing

```python
# Good for: Orders (can't place the same order twice!)
class OrderExecutor:
    def __init__(self):
        self.processed_signals = set()
    
    def process_signal(self, signal):
        if signal.id in self.processed_signals:
            return  # Already processed
        
        self.execute_order(signal)
        self.processed_signals.add(signal.id)
```

## 🔍 Event Sourcing Considerations

### What We Do Now

```python
# Current: State-based
class Position:
    def __init__(self):
        self.quantity = 0
        self.average_price = 0.0
    
    def update(self, fill):
        # Directly update state
        self.quantity += fill.quantity
        self.average_price = ...
```

### What We Could Do (Event Sourcing)

```python
# Future: Event-sourced
class Position:
    def __init__(self):
        self.events = []
    
    def apply_event(self, event):
        self.events.append(event)
        # Rebuild state from events
    
    @property
    def current_state(self):
        # Calculate from event history
        return reduce(apply_event, self.events, initial_state)
```

**Benefits**:
- Complete audit trail
- Time travel debugging
- Event replay for testing

**Current Decision**: Not yet - adds complexity we don't need... yet.

## 📊 Performance Characteristics

### Latency Measurements

| Event Path | Latency | Volume |
|------------|---------|---------|
| Exchange → Gateway | ~0.1ms | 50K/sec |
| Gateway → Strategy | ~0.5ms | 50K/sec |
| Strategy → Executor | ~1ms | 100/sec |
| Executor → Exchange | ~5ms | 100/sec |

### Throughput Limits

```python
# Current capacity
MAX_TICKS_PER_SECOND = 50_000
MAX_SIGNALS_PER_SECOND = 1_000
MAX_ORDERS_PER_SECOND = 100

# Bottleneck analysis
if ticks_per_second > MAX_TICKS_PER_SECOND:
    # Need to: Add more strategy processes
    # Or: Filter ticks at gateway
    # Or: Upgrade to kernel bypass networking
```

## 🛡️ Error Handling in Event Systems

### 1. **Dead Letter Queue**: For Unprocessable Events

```python
class EventProcessor:
    def process(self, event):
        try:
            self.handle_event(event)
        except Exception as e:
            # Send to dead letter queue for analysis
            self.dead_letter_queue.send({
                "event": event,
                "error": str(e),
                "timestamp": datetime.now()
            })
```

### 2. **Circuit Breaker**: Prevent Cascade Failures

```python
class CircuitBreaker:
    def __init__(self, failure_threshold=5):
        self.failure_count = 0
        self.failure_threshold = failure_threshold
        self.is_open = False
    
    def call(self, func, *args):
        if self.is_open:
            raise CircuitOpenError("Circuit breaker is open")
        
        try:
            result = func(*args)
            self.failure_count = 0  # Reset on success
            return result
        except Exception as e:
            self.failure_count += 1
            if self.failure_count >= self.failure_threshold:
                self.is_open = True
            raise
```

## 🔮 Future Event-Driven Enhancements

### 1. **Complex Event Processing (CEP)**

```python
# Detect patterns across multiple events
@rule
def detect_momentum(tick_stream):
    # If 5 consecutive ticks show increasing price
    if all(t1.price < t2.price for t1, t2 in 
           zip(tick_stream[-5:], tick_stream[-4:])):
        emit(MomentumSignal(instrument=tick_stream[-1].instrument))
```

### 2. **Event Streaming with Kafka**

```python
# For persistent event streams
producer = KafkaProducer()
producer.send('market-ticks', tick_event)

# Multiple consumers can replay from any point
consumer = KafkaConsumer('market-ticks')
for message in consumer:
    process_historical_tick(message.value)
```

### 3. **CQRS Pattern**

```python
# Separate read and write models
class TradingCommandHandler:
    def handle_place_order(self, command):
        # Write side - focused on business logic
        order = Order.from_command(command)
        self.repository.save(order)
        emit(OrderPlacedEvent(order))

class PositionQueryHandler:
    def get_current_position(self, account):
        # Read side - optimized for queries
        return self.read_model.get_position(account)
```

## 🎯 Key Takeaways

1. **Events are First-Class Citizens**: Not an afterthought but the core design
2. **Loose Coupling Enables Evolution**: Add features without breaking existing ones
3. **Performance Through Parallelism**: Break free from Python's GIL
4. **Resilience Through Isolation**: One component's failure doesn't cascade
5. **Observability is Built-In**: Every event can be logged, monitored, analyzed

## 📚 Learning Resources

- [Enterprise Integration Patterns](https://www.enterpriseintegrationpatterns.com/) - The bible of messaging
- [Designing Event-Driven Systems](https://www.confluent.io/designing-event-driven-systems/) - Modern patterns
- [Reactive Manifesto](https://www.reactivemanifesto.org/) - The philosophy

---

*"In an event-driven system, every component is both a performer and an audience member in the grand theater of computation."*

**Next**: Deep dive into [Clean Architecture Implementation](CLEAN_ARCHITECTURE.md) → 