# Gateway 與 AllInOneController 重構說明

## 重構目標

這次重構主要改善了以下方面：

1. **消除控制器間的依賴** - 刪除了 GatewayController，將其功能移至 RunGatewayUseCase
2. **簡化 ApplicationStartupStatusUseCase** - 移除了複雜的啟動流程組合
3. **統一啟動邏輯** - AllInOneController 直接協調各 UseCase 的執行
4. **符合 SOLID 原則** - 特別是單一職責和依賴反轉原則

## 主要變更

### 1. 新增 RunGatewayUseCase

這個新的 UseCase 集中了 Gateway 啟動和運行的所有邏輯，包括：
- 前置條件檢查
- 端口可用性檢查
- Gateway 元件初始化
- 事件循環處理
- 訊號處理和資源清理

```python
class RunGatewayUseCase:
    def execute(self, is_threaded_mode: bool = False) -> bool:
        # 檢查前置條件
        # 檢查端口可用性
        # 初始化 Gateway 元件
        # 運行事件循環
```

### 2. 刪除舊的控制器

- 刪除 GatewayController - 功能已遷移至 RunGatewayUseCase
- 刪除對 ApplicationStartupComponentsUseCase 的依賴（現改由 ApplicationStartupStatusUseCase 檢查前置條件）

### 3. 簡化 AllInOneController

AllInOneController 現在直接協調各個 UseCase 的執行，不再通過組合型 UseCase：

```python
def execute(self) -> None:
    # 檢查前置條件
    # 啟動 Gateway
    # 啟動 Strategy
    # 啟動 OrderExecutor
```

### 4. (已移除) 適配器模式

此項不再適用，目前直接由 AllInOneController 協調 RunGatewayUseCase。

## 架構改進

新的架構比舊架構有以下優勢：

1. **單一職責原則**：每個類別只負責一個任務，例如：
   - RunGatewayUseCase 只負責運行 Gateway
   - StartStrategyUseCase 只負責啟動 Strategy
   
2. **開放封閉原則**：
   - 可以輕鬆新增不同的執行模式而無需修改現有代碼
   - 例如，可以新增一個新的 Controller 來以不同方式使用這些 UseCase
   
3. **依賴反轉原則**：
   - 高層模組（Controllers）不再相互依賴
   - 所有控制器和 UseCase 都依賴於抽象介面
   
4. **更好的測試性**：
   - 每個 UseCase 可以單獨測試
   - 可以模擬依賴進行隔離測試

## 技術債務解決

這次重構解決了以下技術債務：

1. 移除了 Controller 層的循環依賴
2. 消除了重複的前置條件檢查邏輯
3. 簡化了事件循環處理邏輯
4. 統一了啟動元件的方法

## 未來擴展點

此架構設計便於以下未來擴展：

1. 添加新的啟動模式（例如：遠程啟動、排程啟動等）
2. 替換消息系統（例如：從 ZMQ 切換到 Kafka）
3. 添加監控和健康檢查功能
4. 實現更複雜的部署模式（例如：自動重啟失敗的服務）