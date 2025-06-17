# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 🏗️ Project Overview

This is an **Auto Futures Trading Machine** - a distributed, event-driven automated trading system for Taiwan futures markets using PFCF (Polaris Futures Capital Future) API. The system follows Clean Architecture principles and uses ZeroMQ for inter-process communication to bypass Python's GIL limitations.

## 🚀 Essential Development Commands

### Poetry-based Dependency Management
```bash
# Install dependencies 
poetry install

# Activate virtual environment
poetry shell

# Add new dependency
poetry add <package>

# Add development dependency
poetry add --group dev <package>
```

### Testing
```bash
# Run all tests
pytest

# Run tests with coverage
pytest --cov=src --cov-report=xml --cov-report=html

# Run specific test file
pytest src/path/to/test_file.py

# Run tests with verbose output
pytest -v

# Run tests matching pattern
pytest -k "test_pattern"
```

### Code Quality
```bash
# Run Ruff linter
ruff check .

# Auto-fix linting issues
ruff check . --fix

# Run Pylint (if available)
pylint src/

# Format code (if using Ruff)
ruff format .
```

### Application Execution
```bash
# Main application (CLI interface)
python app.py

# Strategy process (separate process)
python process/run_strategy.py

# Order executor process (separate process)
python process/run_order_executor_gateway.py
```

## 🏛️ High-Level Architecture

### Multi-Process Design
The system uses a **DLL Gateway Architecture** with three main processes managed by **SystemManager**:

1. **Main Process** (`app.py`)
   - CLI interface for user interaction
   - **SystemManager**: Centralized lifecycle management for all components
   - **DLL Gateway Server**: Order execution (ZMQ REP on port 5557)
   - **Market Data Publisher**: Real-time tick data (ZMQ PUB on port 5555)
   - **PFCF API Integration**: Connects exchange callbacks to market data flow

2. **Strategy Process** (`run_strategy.py`)
   - Subscribes to market data (ZMQ SUB from port 5555)
   - Implements Support/Resistance trading strategy
   - Publishes trading signals (ZMQ PUSH to port 5556)

3. **Order Executor Process** (`run_order_executor_gateway.py`)
   - Receives trading signals (ZMQ PULL from port 5556)
   - Sends orders via DLL Gateway Client (ZMQ REQ to port 5557)

### Key Architectural Patterns
- **Clean Architecture**: Domain layer isolated from infrastructure
- **Event-Driven Design**: ZeroMQ messaging for real-time communication
- **Repository Pattern**: Abstracted data access layer
- **Dependency Injection**: ServiceContainer manages all dependencies
- **Service Layer**: Gateway Services for infrastructure abstraction
- **CQRS**: Separate DTOs for commands and queries
- **Component Status Management**: Enum-based status tracking with health checks

### ZeroMQ Communication Ports
- `5555`: Market data broadcast (PUB/SUB)
- `5556`: Trading signals (PUSH/PULL)
- `5557`: Order execution gateway (REQ/REP)

## 📁 Directory Structure Understanding

```
src/
├── app/                    # Application layer (CLI interface)
├── domain/                 # Business logic and entities
├── infrastructure/         # External concerns (ZMQ, PFCF API, persistence)
├── interactor/            # Use cases and business rules
```

### Important Component Locations

#### Core Infrastructure
- **ApplicationBootstrapper**: `src/app/bootstrap/application_bootstrapper.py` - Dependency injection and initialization
- **ServiceContainer**: `src/infrastructure/services/service_container.py` - Centralized dependency management
- **SystemManager**: `src/infrastructure/services/system_manager.py` - Component lifecycle with status management

#### Gateway Services Layer
- **MarketDataGatewayService**: `src/infrastructure/services/gateway/market_data_gateway_service.py` - Market data infrastructure
- **PortCheckerService**: `src/infrastructure/services/gateway/port_checker_service.py` - Port availability validation
- **GatewayInitializerService**: `src/infrastructure/services/gateway/gateway_initializer_service.py` - ZMQ component initialization

#### Core Services
- **DllGatewayServer**: `src/infrastructure/services/dll_gateway_server.py` - Order execution server
- **ProcessManagerService**: `src/infrastructure/services/process/process_manager_service.py` - Process lifecycle with PID management
- **StatusChecker**: `src/infrastructure/services/status_checker.py` - System health monitoring

#### Application Layer
- **Controllers**: `src/app/cli_pfcf/controllers/` - Handle CLI user interactions
- **Use Cases**: `src/interactor/use_cases/` - Business logic orchestration
- **Entities**: `src/domain/entities/` - Core business objects
- **Repositories**: `src/infrastructure/repositories/` - Data persistence
- **ZMQ Messaging**: `src/infrastructure/messaging/` - Inter-process communication
- **PFCF Integration**: `src/infrastructure/pfcf_client/` - Exchange API client

## ⚙️ Configuration

### Environment Setup
- Copy `.env.example` to `.env` and configure PFCF credentials

#### Required Environment Variables
- `DEALER_TEST_URL`: PFCF test environment URL
- `DEALER_PROD_URL`: PFCF production environment URL

#### Optional Environment Variables
```bash
# ZMQ Configuration
ZMQ_HOST=127.0.0.1
ZMQ_TICK_PORT=5555
ZMQ_SIGNAL_PORT=5556

# DLL Gateway Configuration
DLL_GATEWAY_HOST=127.0.0.1
DLL_GATEWAY_PORT=5557
DLL_GATEWAY_REQUEST_TIMEOUT_MS=5000
DLL_GATEWAY_RETRY_COUNT=3
```

#### Directory Structure Created at Runtime
- `tmp/pids/`: Process ID files for lifecycle management
- `logs/`: Application logs
- `src/data/`: JSON file repositories (sessions, conditions)

### Key Files
- `pyproject.toml`: Poetry dependencies and tool configurations
- `pytest.ini`: Test configuration with pythonpath setup
- `.cursor/rules/python.mdc`: Development standards and practices

### 📚 Architecture Documentation
- [Architecture Guide](docs/ARCHITECTURE.md): Complete system overview with English documentation
- [ServiceContainer Architecture Update](docs/architecture/SERVICECONTAINER_ARCHITECTURE_UPDATE.md): Latest architectural improvements
- [Detailed Flow Diagrams](docs/architecture/DETAILED_FLOW_DIAGRAMS.md): Process flows and data interactions
- [Class Design Guide](docs/architecture/CLASS_DESIGN_GUIDE.md): OOP principles and design patterns

## 🧪 Testing Strategy

### Test Structure
- Tests are co-located with source code in `test/` subdirectories
- Integration tests in `/tests` at project root
- All tests use pytest framework (NOT unittest)
- Comprehensive mocking with pytest-mock

### Critical Test Areas
- **ApplicationBootstrapper** - Dependency injection and validation
- **ServiceContainer** - Centralized dependency management
- **SystemManager lifecycle management** - Component status management, health checks, startup/shutdown coordination
- **Gateway Services** - Port checking, market data gateway, process management
- Use case business logic validation
- ZMQ messaging serialization/deserialization
- DLL Gateway client/server communication
- PFCF API callback integration and market data flow
- Trading strategy condition evaluation
- Repository data persistence

## ⚠️ Important Development Notes

### PFCF DLL Dependencies
- This system requires proprietary PFCF Python DLL API
- DLL files should be placed in `src/infrastructure/pfcf_client/dll/`
- Apply to Taiwan Unified Futures for API access

### Security Considerations
- No credentials in child processes - only in main process
- DLL Gateway provides centralized security layer
- All exchange communication goes through secure gateway

### Process Management
- Strategy and Order Executor run as separate processes
- ZMQ handles all inter-process communication
- Graceful shutdown with signal handling

### Performance Requirements
- Tick processing: < 1ms latency target
- Signal generation: < 5ms from tick to decision
- Order execution: < 10ms round-trip to exchange

### Component Status Management
- **Status Tracking**: All components use `ComponentStatus` enum (STOPPED, STARTING, RUNNING, STOPPING, ERROR)
- **Health Monitoring**: SystemManager provides health checks and uptime tracking
- **Graceful Shutdown**: Coordinated shutdown sequence with proper cleanup
- **PID Management**: ProcessManagerService handles PID files in `tmp/pids/` directory

### Dependency Injection Architecture
- **ServiceContainer**: Centralized container for all application dependencies
- **ApplicationBootstrapper**: Handles initialization sequence and validation
- **Clean Separation**: Core components, repositories, and services properly injected
- **Configuration Validation**: Comprehensive environment variable validation during bootstrap