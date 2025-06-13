# 🔄 DLL Porting Guide - Migrating from Taiwan Unified Futures to Other Brokers

## 📋 Overview

This system is currently **highly coupled** to Taiwan Unified Futures (PFCF) proprietary DLL API. If you need to migrate the system to other broker APIs (such as Yuanta Securities, Capital Futures, etc.), this guide will help you identify locations requiring modification and provide refactoring recommendations.

## ⚠️ Coupling Assessment

**Coupling Level**: 🔴 **Extremely High** (95% of core functionality depends on PFCF)

| Layer | PFCF Coupling | Impact Scope |
|-------|---------------|--------------|
| **Infrastructure Layer** | 🔴 100% | Complete dependence on PFCF DLL |
| **Business Logic Layer** | 🔴 85% | DTOs, Use Cases hard-bound to PFCF |
| **Application Layer** | 🟡 40% | Configuration and dependency injection |
| **Domain Layer** | 🟢 10% | Entities and value objects relatively independent |

## 🎯 Core Coupling Point Identification

### 1. 🔧 **Infrastructure Layer - Complete Rewrite Area**

#### **PFCF Client Module** `src/infrastructure/pfcf_client/`
```
📁 Directory requiring complete replacement
├── dll.py                  ❌ PFCF DLL wrapper - needs complete rewrite
├── api.py                  ❌ PFCF API wrapper - needs complete rewrite
├── event_handler.py        ❌ PFCF event handling - needs complete rewrite
└── tick_producer.py        🟡 Partial modification - callback function signatures
```

**Replacement Strategy**:
```python
# Current PFCF structure
class PFCFApi:
    def __init__(self):
        self.client = PFCFAPI()        # ❌ PFCF specific
        self.trade = self.client.DTradeLib   # ❌ PFCF naming
        
# Recommended abstract structure  
class ExchangeApiInterface:
    def login(self, credentials: LoginCredentials) -> LoginResult
    def send_order(self, order: OrderRequest) -> OrderResult
    def get_positions(self, account: str) -> List[Position]
    def subscribe_market_data(self, symbols: List[str]) -> None
```

#### **DLL Gateway Service** `src/infrastructure/services/dll_gateway_server.py`
- **Line 14**: `from src.infrastructure.pfcf_client.api import PFCFApi` ❌
- **Line 39**: `def __init__(self, exchange_client: PFCFApi)` ❌
- **Lines 282-295**: PFCF order object creation and calls ❌

**Modification Guide**:
```python
# Before modification
def __init__(self, exchange_client: PFCFApi):
    
# After modification
def __init__(self, exchange_client: ExchangeApiInterface):
```

### 2. 💼 **Business Logic Layer - Refactoring Area**

#### **DTO Layer Refactoring** `src/interactor/dtos/send_market_order_dtos.py`

**PFCF-specific field mapping** (Lines 40-61):
```python
# ❌ PFCF-specific method to be removed
def to_pfcf_dict(self, service_container):
    return {
        "ACTNO": self.order_account,        # PFCF field naming
        "PRODUCTID": self.item_code,        # PFCF field naming
        "BS": converter.to_pfcf_enum(self.side),
        # ... other PFCF fields
    }
```

**Recommended Refactoring**:
```python
# ✅ Broker-neutral method
def to_exchange_dict(self, converter: ExchangeConverterInterface):
    return {
        "account": self.order_account,
        "symbol": self.item_code,
        "side": converter.convert_side(self.side),
        "order_type": converter.convert_order_type(self.order_type),
        # ... standardized fields
    }
```

#### **Use Case Layer Decoupling** `src/interactor/use_cases/`

**Use Cases requiring modification**:
- `send_market_order.py` (Lines 69-90) ❌ Direct PFCF API calls
- `user_login.py` (Lines 59-61) ❌ `PFCLogin` specific method
- `get_position.py` ❌ PFCF position queries

**Decoupling Strategy**:
```python
# Before - Direct PFCF dependency
order_result = self.service_container.exchange_client.DTradeLib.Order(order)

# After - Abstract interface
order_result = self.exchange_api.send_order(order_request)
```

### 3. ⚙️ **Service Layer Refactoring**

#### **Enum Converter Service** `src/infrastructure/services/enum_converter.py`
- **Lines 36-66**: PFCF-specific enum mapping ❌
- **Lines 70-79**: `to_pfcf_decimal` method ❌

**Refactoring Recommendation**:
```python
# Broker-specific converter factory
class ExchangeConverterFactory:
    @staticmethod
    def create_converter(exchange_type: ExchangeType) -> ExchangeConverterInterface:
        if exchange_type == ExchangeType.PFCF:
            return PFCFConverter()
        elif exchange_type == ExchangeType.YUANTA:
            return YuantaConverter()  # Yuanta Securities
        elif exchange_type == ExchangeType.CAPITAL:
            return CapitalConverter()  # Capital Futures
```

#### **Service Container** `src/infrastructure/services/service_container.py`
- **Line 28**: `def __init__(self, exchange_api: PFCFApi)` ❌ Hard-bound
- **Lines 45-58**: PFCF-specific property access ❌

### 4. 📊 **Data Access Layer**

#### **Position Repository** `src/infrastructure/repositories/pfcf_position_repository.py`
- **Lines 134-140**: Direct PFCF API calls ❌
- **Lines 41-63**: 22 PFCF-specific parameter handling ❌

## 🏗️ Recommended Refactoring Architecture

### **Phase 1: Create Abstraction Layer**

```python
# 1. Exchange API abstract interface
class ExchangeApiInterface(ABC):
    @abstractmethod
    def login(self, credentials: LoginCredentials) -> LoginResult:
        pass
    
    @abstractmethod 
    def send_order(self, order: OrderRequest) -> OrderResult:
        pass
    
    @abstractmethod
    def get_positions(self, account: str) -> List[Position]:
        pass
    
    @abstractmethod
    def subscribe_market_data(self, symbols: List[str], callback: Callable) -> None:
        pass

# 2. Data converter abstract interface
class ExchangeConverterInterface(ABC):
    @abstractmethod
    def convert_side(self, side: Side) -> Any:
        pass
    
    @abstractmethod
    def convert_order_type(self, order_type: OrderType) -> Any:
        pass
```

### **Phase 2: PFCF Implementation Class**

```python
# PFCF concrete implementation
class PFCFExchangeApi(ExchangeApiInterface):
    def __init__(self):
        self._client = PFCFAPI()  # Encapsulate PFCF-specific logic
    
    def send_order(self, order: OrderRequest) -> OrderResult:
        # Convert standard OrderRequest to PFCF format
        pfcf_order = self._convert_to_pfcf_order(order)
        result = self._client.DTradeLib.Order(pfcf_order)
        return self._convert_from_pfcf_result(result)
```

### **Phase 3: Other Broker Implementations**

```python
# Yuanta Securities implementation example
class YuantaExchangeApi(ExchangeApiInterface):
    def __init__(self):
        self._client = YuantaAPI()  # Yuanta API
    
    def send_order(self, order: OrderRequest) -> OrderResult:
        # Convert to Yuanta format and call
        yuanta_order = self._convert_to_yuanta_order(order)
        result = self._client.PlaceOrder(yuanta_order)
        return self._convert_from_yuanta_result(result)
```

## 📋 Migration Checklist

### **🔍 Phase 1: Analyze Target Broker API**

- [ ] **Obtain API documentation**: Research target broker's DLL/API structure
- [ ] **Identify equivalent functions**: Login, order placement, position queries, market data
- [ ] **Compare data formats**: Order structures, callback parameters, error codes
- [ ] **Confirm event model**: Callback mechanism or polling mechanism

### **🏗️ Phase 2: Establish Abstraction Layer**

- [ ] **Define abstract interfaces**: `ExchangeApiInterface`
- [ ] **Design standardized DTOs**: Broker-neutral data structures
- [ ] **Create converter interfaces**: `ExchangeConverterInterface`
- [ ] **Refactor service container**: Support dependency injection of abstract interfaces

### **🔧 Phase 3: Implement Concrete Adapters**

- [ ] **PFCF adapter**: Wrap existing code into abstract interface
- [ ] **Target broker adapter**: Implement new broker's concrete classes
- [ ] **Configuration management**: Support multi-broker configuration switching
- [ ] **Unified error handling**: Standardize error formats from different brokers

### **🧪 Phase 4: Testing and Validation**

- [ ] **Unit tests**: Abstract interfaces and adapters
- [ ] **Integration tests**: End-to-end trading workflows
- [ ] **Parallel testing**: PFCF and new broker running simultaneously
- [ ] **Performance testing**: Ensure no significant latency increase

## 📝 Configuration Examples

### **Multi-broker Support Configuration**

```env
# .env configuration
EXCHANGE_PROVIDER=PFCF          # PFCF, YUANTA, CAPITAL
PFCF_TEST_URL=Taiwan_Unified_Futures_Test_URL
PFCF_PROD_URL=Taiwan_Unified_Futures_Prod_URL
YUANTA_TEST_URL=Yuanta_Securities_Test_URL
YUANTA_PROD_URL=Yuanta_Securities_Prod_URL
```

### **Dependency Injection Configuration**

```python
# config.py
class ExchangeConfig:
    def create_exchange_api(self) -> ExchangeApiInterface:
        provider = os.getenv("EXCHANGE_PROVIDER", "PFCF")
        
        if provider == "PFCF":
            return PFCFExchangeApi()
        elif provider == "YUANTA":
            return YuantaExchangeApi()
        elif provider == "CAPITAL":
            return CapitalExchangeApi()
        else:
            raise ValueError(f"Unsupported exchange provider: {provider}")
```

## ⚡ Performance Considerations

### **Abstraction Layer Overhead**

| Operation Type | Expected Overhead | Optimization Strategy |
|---------------|-------------------|----------------------|
| Order conversion | < 0.1ms | Object pooling, precompiled conversion logic |
| Data serialization | < 0.2ms | Use msgpack instead of JSON |
| Interface calls | < 0.05ms | Avoid over-abstraction, direct delegation |

### **Memory Management**

- **Object reuse**: Avoid frequent creation of conversion objects
- **Connection pooling**: Each broker maintains independent connection pools
- **Event decoupling**: Use weak references to avoid callback memory leaks

## 🚨 Common Pitfalls

### **1. Over-abstraction**
❌ Don't abstract for the sake of abstraction, maintain practicality
✅ Only abstract parts that truly vary

### **2. Performance Loss**
❌ Avoid multi-layer conversion causing increased latency
✅ Direct mapping, avoid intermediate formats

### **3. Inconsistent Error Handling**
❌ Different brokers have vastly different error formats
✅ Define unified error codes and message formats

### **4. Testing Difficulties**
❌ Relying on real broker APIs for testing
✅ Create simulators to support offline testing

## 📈 Estimated Workload

| Phase | Workload | Risk Level |
|-------|----------|------------|
| **Abstract interface design** | 3-5 days | 🟡 Medium |
| **PFCF adapter refactoring** | 5-8 days | 🔴 High |
| **New broker adapter** | 10-15 days | 🔴 High |
| **Testing and optimization** | 8-12 days | 🟡 Medium |
| **Total** | **26-40 days** | 🔴 High |

## 💡 Success Key Factors

1. **Deep understanding of target API**: Detailed study of broker DLL documentation
2. **Gradual refactoring**: Don't rewrite all code at once
3. **Complete test coverage**: Ensure functionality is completely equivalent after refactoring
4. **Performance benchmarking**: Ensure abstraction layer doesn't affect trading latency
5. **Rollback plan**: Prepare strategy for quick reversion to PFCF version

---

**⚠️ Important Reminder**: Migration work has high complexity and risk. It is recommended to proceed in a fully tested environment and maintain parallel operation capability with the original PFCF version.

*If you only need to trade with Taiwan Unified Futures, it is recommended to use the existing system directly without migration.*