# ADR-005: Gateway Naming Consolidation

## Status
Accepted — 2026-04-21

## Context

The word "gateway" accumulated three different meanings in the codebase,
causing repeated reader confusion:

1. **Concept A — DLL gateway** (outbound): centralizes PFCF DLL access so
   subprocesses can send orders / query positions via ZMQ REQ/REP instead
   of each holding their own DLL instance. See ADR-004.

2. **Concept B — Market data gateway** (inbound): bridges PFCF tick
   callbacks into a ZMQ PUB socket so the strategy subprocess can
   subscribe. Name: `MarketDataGatewayService`.

3. **Concept C — "uses a gateway"**: classes that *consume* a gateway
   without being one themselves. The clearest offender was
   `OrderExecutorGateway` in `src/domain/order/`, which processes
   trading signals and delegates order sending to `DllGatewayClient`.
   The class was not itself a gateway.

The physical layout also did not reflect the conceptual grouping:

- `MarketDataGatewayService` lived under `services/gateway/`
- `DllGatewayServer` / `DllGatewayClient` lived at `services/` root
- `PortCheckerService` lived under `services/gateway/` despite having
  nothing to do with gateways

## Decision

**The `services/gateway/` directory is reserved for PFCF bridge
components. `Gateway` in a class or module name means the thing itself
is a gateway, not that it uses one.**

### File moves

| From | To |
|---|---|
| `src/infrastructure/services/dll_gateway_server.py` | `src/infrastructure/services/gateway/dll_gateway_server.py` |
| `src/infrastructure/services/dll_gateway_client.py` | `src/infrastructure/services/gateway/dll_gateway_client.py` |
| `src/infrastructure/services/gateway/port_checker_service.py` | `src/infrastructure/services/port_checker_service.py` |

### Renames

| From | To |
|---|---|
| `OrderExecutorGateway` (class) | `OrderExecutor` |
| `OrderExecutorGatewayProcess` (class in subprocess script) | `OrderExecutorProcess` |
| `src/domain/order/order_executor_gateway.py` | `src/domain/order/order_executor.py` |
| `process/run_order_executor_gateway.py` | `process/run_order_executor.py` |
| `tmp/pids/order_executor_gateway.pid` (runtime file) | `tmp/pids/order_executor.pid` |

### Final gateway inventory

Under `src/infrastructure/services/gateway/`:

- `dll_gateway_server.py` — REP :5557, main process, wraps the exchange adapter
- `dll_gateway_client.py` — REQ, used by order-executor subprocess
- `market_data_gateway_service.py` — PUB :5555, wraps PFCF tick callbacks

Nothing else claims to be a gateway.

## Consequences

### Positive
- "Is this a gateway?" becomes a single-location question (check the
  directory).
- New contributors stop asking whether `OrderExecutorGateway` is a
  gateway-server variant.
- ADR-004's original pattern is preserved; this is purely a naming /
  location fix on top of it.

### Neutral
- Import paths changed for `DllGatewayServer` / `DllGatewayClient` /
  `PortCheckerService`. Affected call sites: bootstrapper, system
  manager, subprocess runner, tests.

### Negative
- The PID filename change (`order_executor_gateway.pid` →
  `order_executor.pid`) is the only runtime-visible effect. Operators
  upgrading must stop any still-running subprocess before pulling,
  otherwise the old PID file is orphaned.

## References

- ADR-004: DLL Gateway Centralization (original gateway pattern)
