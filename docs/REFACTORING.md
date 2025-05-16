# 重構說明：GatewayController 與 AllInOneController

## 重構目標

此次重構的主要目標是改善 `GatewayController` 和 `AllInOneController` 的設計，使其符合 SOLID 原則和 Clean Architecture：

1. **單一職責原則 (SRP)** - 每個類別只負責單一功能
2. **開放封閉原則 (OCP)** - 類別應該對擴展開放，對修改關閉
3. **依賴反轉原則 (DIP)** - 高層模組不應依賴低層模組，兩者都應該依賴抽象
4. **清晰架構 (Clean Architecture)** - 業務邏輯獨立於框架和技術細節

## 主要問題

原有設計的主要問題：

1. Controller 做了太多事情，承擔了多個責任
2. 重複的檢查邏輯（ApplicationStartupStatusUseCase 在不同階層重複執行）
3. 底層技術細節（如 ZMQ 初始化、Port 檢查）直接在 Controller 中實作
4. 缺乏依賴反轉，難以測試和替換實作

## 重構架構

重構後的架構如下：

### 1. Service 層

- **PortCheckerService** - 負責檢查 port 可用性
- **GatewayInitializerService** - 負責初始化 Gateway 的 ZMQ 元件
- **ProcessManagerService** - 負責管理 Strategy 和 OrderExecutor 的進程

### 2. UseCase 層 (Interactor)

- **StartGatewayUseCase** - 負責啟動 Gateway
- **StartStrategyUseCase** - 負責啟動 Strategy
- **StartOrderExecutorUseCase** - 負責啟動 OrderExecutor
- **ApplicationStartupComponentsUseCase** - 負責協調啟動所有元件

### 3. Controller 層

- **GatewayController** - 負責處理用戶啟動 Gateway 的請求
- **AllInOneController** - 負責處理用戶啟動所有元件的請求

### 4. 介面層

- **PortCheckerServiceInterface** - Port 檢查服務介面
- **GatewayInitializerServiceInterface** - Gateway 初始化服務介面
- **ProcessManagerServiceInterface** - 進程管理服務介面
- **StatusCheckerInterface** - 狀態檢查服務介面

## 重構優點

1. **責任明確** - 每個類別只負責一個功能，便於維護與擴展
2. **消除重複** - 不再有重複的狀態檢查，邏輯集中管理
3. **技術隔離** - 技術細節（ZMQ、進程管理）隔離在 Service 層
4. **依賴抽象** - 高層依賴介面，不直接依賴具體實作
5. **便於測試** - 可以替換實作進行單元測試

## 使用方式

### GatewayController

```python
gateway_controller = GatewayController(service_container)
gateway_controller.execute()
```

### AllInOneController

```python
all_in_one_controller = AllInOneController(service_container)
all_in_one_controller.execute()
```

## 未來擴展

此架構設計便於未來擴展：

1. 可以輕易增加新的 UseCase 或 Service 而不影響現有程式碼
2. 可以替換 Service 的實作（如使用不同的消息佇列系統）而不影響 UseCase
3. 可以為各類別單獨編寫測試，提高測試覆蓋率和程式碼品質