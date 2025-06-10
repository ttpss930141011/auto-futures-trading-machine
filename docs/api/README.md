# 📡 API Documentation

> *Overview of public interfaces and services*

## 📦 Modules

### 1. Infrastructure Services (`src/infrastructure/services`)
- **SystemManager**: `start_trading_system()`, `stop_trading_system()`, `get_system_health()`, `restart_component()`
- **EnhancedProcessManager**: `start_strategy_process()`, `start_order_executor_process()`, `monitor_process_health()`, `restart_failed_process()`
- **GatewayServiceWrapper**: `start_gateway()`, `stop_gateway()`, `get_gateway_status()`, `restart_gateway()`

### 2. Messaging (`src/infrastructure/messaging`)
- **ZmqPublisher**, **ZmqSubscriber**, **ZmqPusher**, **ZmqPuller**: `send()`, `receive()`, `publish()`, `subscribe()`
- **serializer**: `serialize()`, `deserialize()` (msgpack + custom types)

### 3. CLI Application (`src/app/cli_application.py`)
- **CLIApplication** class:
  - `run()`: start interactive CLI loop
  - `_display_startup_info()`, `_create_process_handler()`, `_cleanup()`

### 4. Bootstrapping (`src/app/bootstrap/application_bootstrapper.py`)
- **ApplicationBootstrapper**:
  - `bootstrap() -> BootstrapResult`
  - `create_service_container() -> ServiceContainer`
  - `validate_configuration() -> ValidationResult`

### 5. Use Case Interfaces (`src/app/use_cases`)
- Example: `StartStrategyUseCase`, `StartOrderExecutorUseCase`, `RunGatewayUseCase`

### 6. Controllers (`src/app/cli_pfcf/controllers`)
- `UserLoginController`, `UserLogoutController`, `RegisterItemController`, `CreateConditionController`, `SelectOrderAccountController`, `SendMarketOrderController`, `ShowFuturesController`, `GetPositionController`, `AllInOneController`

## 🔍 Finding Details

For full API signatures and examples, explore the source code under `src/`:

```bash
# Jump to CLI application
sed -n '1,50p' src/app/cli_application.py

# View SystemManager
sed -n '1,50p' src/infrastructure/services/system_manager.py
```

---

*This document provides a high-level map; use your IDE for in-depth exploration of each class and method.* 