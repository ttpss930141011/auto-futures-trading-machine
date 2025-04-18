
# Futures trading machine

<p align="center">
<img src="./static/logo/logo-transparent-png.png" width="100" height="100" align="">
</p>

## Description

Documentation is still in progress. The project is an automatic futures trading machine designed to trade futures
contracts on
every exchange due to Clean Architecture. The first presentation method is using CLI. With Clean Architecture, the
project is testable, scalable, and flexible to add new features and exchanges.

## Test Coverage

The test coverage tag for the project is as follows:

![image](https://ttpss930141011.github.io/auto-futures-trading-machine/coverage.svg)

## Event Storming

The event storming diagram for the project is as follows:

![Event Storming](static/imgs/EventStorming_20240328.png)

Updated Link on Miro: [Event Storming](https://miro.com/app/board/uXjVKbXfevY=/?share_link_id=268562178581)


# Futures Trading System Component Relationship Document

## 1. System Architecture Overview

The futures trading system adopts an event-driven architecture, composed of multiple components that interact through events. The diagram below illustrates the main components and their relationships:

```
┌─────────────────────┐                  ┌───────────────────┐
│    PFCF API Client   │                  │   Start Controller │
│ (External Interface) │◀────────────────┤   (Initializer)    │
└──────────┬──────────┘                  └─────────┬─────────┘
           │                                       │
           │ Raw Market Data                        │ Create and Initialize
           ▼                                       │
┌──────────────────────┐                           │
│     TickProducer     │◀──────────────────────────┘
│  (Event Generator)   │                           │
└──────────┬───────────┘                           │
           │                                       │
           │ Tick Event                             │
           ▼                                       │
┌──────────────────────┐                           │
│   EventDispatcher    │◀──────────────────────────┘
│   (Event Router)     │                           │
└┬────────────┬────────┘                           │
 │            │                                    │
 │            │                                    │
 │            ▼                                    │
 │    ┌───────────────────┐                        │
 │    │  SupportResistance│◀───────────────────────┘
 │    │     Strategy      │                        │
 │    └────────┬──────────┘                        │
 │             │                                   │
 │             │ Trading Signal                    │
 │             ▼                                   │
 │    ┌───────────────────┐                        │
 │    │   OrderExecutor   │◀───────────────────────┘
 │    │   (Action Taker)  │
 │    └────────┬──────────┘
 │             │
 │             │ Execute Order
 ▼             ▼
┌─────────────────────┐
│   External Systems  │
│ (Exchange, Database)│
└─────────────────────┘
```

## 2. Core Components and Relationships

### 2.1 StartController

**Role**: System Initializer and Coordinator

**Relationships**:
- Creates and initializes all core components
- Connects PFCF API callbacks to TickProducer
- Schedules periodic tasks to process event buffers
- Starts the event dispatch loop

**Code Example**:
```python
def _initialize_components(self) -> None:
    # Initialize all components
    self.tick_producer = TickProducer(...)
    self.strategy = SupportResistanceStrategy(...)
    self.order_executor = OrderExecutor(...)
    self._connect_api_callbacks()
```

### 2.2 TickProducer

**Role**: Market Data Processor

**Relationships**:
- Receives raw market data from PFCF API
- Converts data into standardized Tick events
- Maintains an event buffer (FifoQueueEventSource)
- Publishes events via EventDispatcher

**Data Flow**:
1. PFCF API → `handle_tick_data()` → Create Tick Event
2. Event is added to the buffer and published to EventDispatcher

**Code Example**:
```python
def handle_tick_data(self, commodity_id, ...):
    # Create Tick Event
    tick_event = TickEvent(datetime.now(), tick)
    
    # Add to buffer and publish
    self.tick_buffer.push(tick_event)
    self.event_dispatcher.publish_event("TICK", tick_event)
```

### 2.3 Event System

#### 2.3.1 Event

**Role**: Base class for all events

**Relationships**:
- Inherited by all specific event types
- Contains basic timestamp information

#### 2.3.2 FifoQueueEventSource

**Role**: Event Buffer

**Relationships**:
- Stores events and maintains FIFO order
- Provides buffer management methods (push, pop, peek, size)
- Supports temporary storage of high-frequency events

**Code Example**:
```python
def push(self, event: E) -> bool:
    """Add event to the end of the queue"""
    if self._max_size > 0 and len(self._queue) >= self._max_size:
        return False
    self._queue.append(event)
    return True
```

#### 2.3.3 RealtimeDispatcher

**Role**: Event Router and Dispatcher

**Relationships**:
- Maintains mapping from event types to handlers
- Routes events to the correct handlers
- Manages execution of scheduled tasks
- Processes events from the event source

**Data Flow**:
1. Receives events via `publish_event()`
2. Finds handlers subscribed to the event type
3. Calls handlers to process the event
4. Manages scheduled tasks and calls idle handlers when idle

**Code Example**:
```python
def publish_event(self, event_type: str, event: Event) -> None:
    """Publish event to all subscribers"""
    if event_type in self._event_handlers:
        for handler in self._event_handlers[event_type]:
            try:
                handler(event)
            except Exception as e:
                self._log_error(f"Error handling event: {e}")
```

### 2.4 SupportResistanceStrategy

**Role**: Trading Strategy

**Relationships**:
- Subscribes to Tick events
- Analyzes price data and checks trading conditions
- Generates trading signals
- Manages trading conditions using ConditionRepository

**Data Flow**:
1. Receives Tick event → `on_tick()`
2. Checks all active conditions
3. Generates trading signal when conditions are met
4. Publishes trading signal to EventDispatcher

**Code Example**:
```python
def on_tick(self, tick_event: TickEvent):
    # Extract price
    price = int(tick_event.tick.match_price)
    
    # Process conditions
    for condition in self.condition_repository.get_all().values():
        self._process_condition(condition, price, tick_event)
```

### 2.5 OrderExecutor

**Role**: Order Executor

**Relationships**:
- Subscribes to trading signal events
- Executes orders using SendMarketOrderUseCase
- Retrieves account information from SessionRepository

**Data Flow**:
1. Receives trading signal → `on_trading_signal()`
2. Constructs market order DTO
3. Calls SendMarketOrderUseCase
4. Records execution result

**Code Example**:
```python
def on_trading_signal(self, signal: TradingSignal):
    # Create order DTO
    input_dto = SendMarketOrderInputDto(
        order_account=self.session_repository.get_order_account(),
        item_code=signal.commodity_id,
        side=signal.operation,
        # ...other parameters
    )
    
    # Execute order
    result = self.send_order_use_case.execute(input_dto)
```

## 3. Detailed Data Flow

### 3.1 Event Processing Flow

The complete event processing flow is as follows:

1. **Market Data Reception**:
   ```
   PFCF API → TickProducer.handle_tick_data()
   ```

2. **Event Creation and Publishing**:
   ```
   TickProducer → Create TickEvent → Add to tick_buffer → EventDispatcher.publish_event()
   ```

3. **Event Routing and Processing**:
   ```
   EventDispatcher → Strategy.on_tick() → Analyze conditions
   ```

4. **Signal Generation**:
   ```
   Strategy → Conditions met → Create TradingSignal → EventDispatcher.publish_event()
   ```

5. **Order Execution**:
   ```
   EventDispatcher → OrderExecutor.on_trading_signal() → SendMarketOrderUseCase.execute()
   ```

### 3.2 Buffer Processing Flow

Buffer processing is performed asynchronously:

1. **Buffer Filling**:
   ```
   TickProducer.handle_tick_data() → tick_buffer.push()
   ```

2. **Periodic Processing**:
   ```
   StartController._schedule_buffer_processing() → Triggered every second → TickProducer.process_buffer()
   ```

3. **Batch Processing**:
   ```
   TickProducer.process_buffer() → Process multiple events → Record statistics
   ```

## 4. Key Design Decisions

### 4.1 Use of Direct Publishing and Buffer

The system uses both event handling mechanisms:

1. **Direct Publishing**:
   - Advantages: Low latency, real-time response
   - Usage: Ensures immediate response to critical market data

2. **Buffer**:
   - Advantages: Prevents system overload, smoothes load handling
   - Usage: Maintains system stability in high-frequency data streams

### 4.2 Generic Event Buffer

Design using generic `FifoQueueEventSource[E]`:

- Enhances type safety
- Makes buffer reusable for different event types
- Simplifies buffer implementation for specific event types

### 4.3 Scheduler and Scheduled Tasks

Use `SchedulerQueue` to manage scheduled tasks:

- Allows periodic buffer processing
- Implements delayed execution and recurring tasks
- Keeps event loop efficient

## 5. Dependency Analysis

Dependencies between components follow Clean Architecture principles:

```
Outer layers depend on inner layers, inner layers do not depend on outer layers
```

1. **StartController** depends on all other components (outermost layer)
   - Dependencies: TickProducer, Strategy, OrderExecutor, EventDispatcher

2. **TickProducer** depends on the event system
   - Dependencies: EventDispatcher, Event, FifoQueueEventSource

3. **Strategy** depends on the event system and domain layer
   - Dependencies: EventDispatcher, ConditionRepository

4. **OrderExecutor** depends on the event system and use case layer
   - Dependencies: EventDispatcher, SendMarketOrderUseCase, SessionRepository

5. **EventDispatcher** only depends on basic event classes (innermost layer)
   - Dependencies: Event, EventSource

This dependency structure ensures the system's testability and maintainability, allowing components to be independently replaced or modified.

## 6. System Configuration Parameters

Important system parameters and their default values:

| Parameter          | Default Value | Description                          | Location                          |
|--------------------|---------------|--------------------------------------|-----------------------------------|
| buffer_size        | 1000          | Tick event buffer size               | TickProducer.__init__             |
| max_events         | 50            | Maximum number of events per process | StartController._process_buffers  |
| processing_interval| 1 second      | Buffer processing interval           | StartController._schedule_buffer_processing |

You can adjust these parameters as needed to adapt to different market conditions and hardware environments.

## 7. Conclusion

Components in the system collaborate in a loosely coupled manner through an event-driven model, forming a complete trading process. This design:

1. Supports high-frequency event processing, preventing system overload through buffering mechanisms
2. Ensures events are processed in chronological order, guaranteeing correct trading decisions
3. Provides clear separation of component responsibilities, adhering to SOLID principles
4. Supports system scalability, allowing the addition of new event types and handlers

The system architecture adheres to Clean Architecture and SOLID principles, ensuring code maintainability, testability, and flexibility.