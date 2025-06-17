# DLL Decoupling Refactoring

## Overview

This document describes the refactoring done to decouple the system from PFCF DLL API by introducing abstraction layers.

## Problem

The system was **highly coupled** to Taiwan Unified Futures (PFCF) DLL API:
- Infrastructure layer 100% dependent on PFCF
- DTOs contain PFCF-specific fields
- Use Cases directly call PFCF API
- No abstraction layer exists

## Solution

We introduced abstraction layers following Clean Architecture principles:

### 1. Exchange API Interface

Created `ExchangeApiInterface` in domain layer:
- Standard broker-neutral methods (connect, send_order, get_positions)
- Broker-neutral data classes (OrderRequest, OrderResult, Position)
- No dependency on specific broker implementation

### 2. Exchange Converter Interface

Created `ExchangeConverterInterface` for data conversion:
- Convert between internal enums and broker formats
- Format prices and quantities per broker requirements
- Standardize error codes

### 3. PFCF Adapter Implementation

Created `PFCFExchangeApi` that:
- Implements `ExchangeApiInterface`
- Wraps existing PFCF API
- Converts between standard and PFCF formats
- Isolates PFCF-specific logic

### 4. Exchange Factory

Created `ExchangeFactory` for:
- Creating appropriate exchange implementation
- Supporting multiple brokers via configuration
- Easy testing with simulator

### 5. Updated DllGatewayServer

Modified to use abstract interface:
- Takes `ExchangeApiInterface` instead of `PFCFApi`
- Uses standard data formats internally
- Converts DTOs to/from standard formats

## Benefits

1. **Loose Coupling**: Business logic no longer depends on PFCF
2. **Easy Testing**: Can use simulator without real connection
3. **Multi-Broker Support**: Can add new brokers without changing core
4. **Clean Architecture**: Proper dependency direction

## Migration Path

### Phase 1: Abstract Interface (Done)
- ✅ Create interfaces
- ✅ Create PFCF adapter
- ✅ Update DllGatewayServer
- ✅ Create simulator for testing

### Phase 2: Refactor Use Cases (Next)
- Update Use Cases to use abstract interface
- Remove PFCF-specific logic from business layer
- Create broker-neutral DTOs

### Phase 3: Add New Brokers (Future)
- Implement Yuanta adapter
- Implement Capital Futures adapter
- Test multi-broker scenarios

## Configuration

Set exchange provider in environment:
```bash
EXCHANGE_PROVIDER=PFCF  # or YUANTA, CAPITAL, SIMULATOR
```

## Testing

Run with simulator:
```bash
EXCHANGE_PROVIDER=SIMULATOR python app.py
```

## Code Examples

### Before (Coupled)
```python
class DllGatewayServer:
    def __init__(self, exchange_client: PFCFApi):
        # Directly depends on PFCF
        
    def _execute_order(self):
        # Direct PFCF API calls
        order = self._exchange_client.trade.OrderObject()
        order.ACTNO = pfcf_input.get("ACTNO")
        # ... PFCF specific code
```

### After (Decoupled)
```python
class DllGatewayServer:
    def __init__(self, exchange_client: ExchangeApiInterface):
        # Depends on abstraction
        
    def _execute_order(self):
        # Standard interface calls
        order_request = OrderRequest(
            account=input_dto.order_account,
            symbol=input_dto.item_code,
            # ... standard fields
        )
        result = self._exchange_client.send_order(order_request)
```

## Next Steps

1. Continue refactoring Use Cases
2. Create broker-neutral DTOs
3. Test with simulator
4. Document new broker integration process

## Notes

- Existing PFCF functionality remains unchanged
- System can still run with PFCF as before
- New abstraction adds minimal overhead
- Future brokers can be added without core changes