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
python run_strategy.py

# Order executor process (separate process)
python run_order_executor_gateway.py
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
- **Dependency Injection**: Service container pattern
- **CQRS**: Separate DTOs for commands and queries

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
- **SystemManager**: `src/infrastructure/services/system_manager.py` - Centralized lifecycle management
- **MarketDataGatewayService**: `src/infrastructure/services/gateway/market_data_gateway_service.py` - Market data publishing
- **DllGatewayServer**: `src/infrastructure/services/dll_gateway_server.py` - Order execution server
- **Controllers**: `src/app/cli_pfcf/controllers/` - Handle CLI user interactions
- **Use Cases**: `src/interactor/use_cases/` - Business logic orchestration
- **Entities**: `src/domain/entities/` - Core business objects
- **Repositories**: `src/infrastructure/repositories/` - Data persistence
- **ZMQ Messaging**: `src/infrastructure/messaging/` - Inter-process communication
- **PFCF Integration**: `src/infrastructure/pfcf_client/` - Exchange API client

## ⚙️ Configuration

### Environment Setup
- Copy `.env.example` to `.env` and configure PFCF credentials
- Required: `DEALER_TEST_URL`, `DEALER_PROD_URL`
- Optional: ZMQ ports, logging levels, timeouts

### Key Files
- `pyproject.toml`: Poetry dependencies and tool configurations
- `pytest.ini`: Test configuration with pythonpath setup
- `.cursor/rules/python.mdc`: Development standards and practices

### 📚 Architecture Documentation
- `ARCHITECTURE.md`: 系統總覽和架構圖表
- `DETAILED_FLOW_DIAGRAMS.md`: 詳細的流程圖和數據流向
- `CLASS_DESIGN_GUIDE.md`: 類別設計指南和 OOP 原則應用

## 🧪 Testing Strategy

### Test Structure
- Tests are co-located with source code in `test/` subdirectories
- Integration tests in `/tests` at project root
- All tests use pytest framework (NOT unittest)
- Comprehensive mocking with pytest-mock

### Critical Test Areas
- **SystemManager lifecycle management** - Component startup/shutdown coordination
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