# 🔄 DLL 移植指南 - 從統一期貨移植到其他券商

## 📋 概述

本系統目前**高度耦合**於台灣統一期貨 (PFCF) 的專用 DLL API。如果您需要將系統移植到其他券商的 API（如元大期貨、群益期貨等），本指南將協助您識別需要修改的位置並提供重構建議。

## ⚠️ 耦合度評估

**耦合程度**: 🔴 **極高** (95% 的核心功能依賴 PFCF)

| 層級 | PFCF 耦合度 | 影響範圍 |
|------|------------|----------|
| **基礎設施層** | 🔴 100% | 完全依賴 PFCF DLL |
| **業務邏輯層** | 🔴 85% | DTO、Use Case 硬綁定 PFCF |
| **應用層** | 🟡 40% | 配置和依賴注入 |
| **領域層** | 🟢 10% | 實體和值對象相對獨立 |

## 🎯 核心耦合點識別

### 1. 🔧 **基礎設施層 - 完全重寫區域**

#### **PFCF 客戶端模組** `src/infrastructure/pfcf_client/`
```
📁 需要完全替換的目錄
├── dll.py                  ❌ PFCF DLL 封裝 - 需完全重寫
├── api.py                  ❌ PFCF API 包裝器 - 需完全重寫
├── event_handler.py        ❌ PFCF 事件處理 - 需完全重寫
└── tick_producer.py        🟡 部分修改 - 回調函數簽名
```

**替換策略**:
```python
# 目前的 PFCF 結構
class PFCFApi:
    def __init__(self):
        self.client = PFCFAPI()        # ❌ PFCF 特定
        self.trade = self.client.DTradeLib   # ❌ PFCF 命名
        
# 建議的抽象結構  
class ExchangeApiInterface:
    def login(self, credentials: LoginCredentials) -> LoginResult
    def send_order(self, order: OrderRequest) -> OrderResult
    def get_positions(self, account: str) -> List[Position]
    def subscribe_market_data(self, symbols: List[str]) -> None
```

#### **DLL Gateway 服務** `src/infrastructure/services/dll_gateway_server.py`
- **第14行**: `from src.infrastructure.pfcf_client.api import PFCFApi` ❌
- **第39行**: `def __init__(self, exchange_client: PFCFApi)` ❌
- **第282-295行**: PFCF 訂單物件創建和調用 ❌

**修改指導**:
```python
# 修改前
def __init__(self, exchange_client: PFCFApi):
    
# 修改後
def __init__(self, exchange_client: ExchangeApiInterface):
```

### 2. 💼 **業務邏輯層 - 重構區域**

#### **DTO 層重構** `src/interactor/dtos/send_market_order_dtos.py`

**PFCF 特定字段映射** (第40-61行):
```python
# ❌ 需要移除的 PFCF 特定方法
def to_pfcf_dict(self, service_container):
    return {
        "ACTNO": self.order_account,        # PFCF 字段命名
        "PRODUCTID": self.item_code,        # PFCF 字段命名
        "BS": converter.to_pfcf_enum(self.side),
        # ... 其他 PFCF 字段
    }
```

**建議重構**:
```python
# ✅ 券商中立的方法
def to_exchange_dict(self, converter: ExchangeConverterInterface):
    return {
        "account": self.order_account,
        "symbol": self.item_code,
        "side": converter.convert_side(self.side),
        "order_type": converter.convert_order_type(self.order_type),
        # ... 標準化字段
    }
```

#### **Use Case 層解耦** `src/interactor/use_cases/`

**需要修改的 Use Cases**:
- `send_market_order.py` (第69-90行) ❌ 直接 PFCF API 調用
- `user_login.py` (第59-61行) ❌ `PFCLogin` 特定方法
- `get_position.py` ❌ PFCF 倉位查詢

**解耦策略**:
```python
# 修改前 - 直接依賴 PFCF
order_result = self.service_container.exchange_client.DTradeLib.Order(order)

# 修改後 - 抽象介面
order_result = self.exchange_api.send_order(order_request)
```

### 3. ⚙️ **服務層重構**

#### **枚舉轉換服務** `src/infrastructure/services/enum_converter.py`
- **第36-66行**: PFCF 特定枚舉映射 ❌
- **第70-79行**: `to_pfcf_decimal` 方法 ❌

**重構建議**:
```python
# 券商特定轉換器工廠
class ExchangeConverterFactory:
    @staticmethod
    def create_converter(exchange_type: ExchangeType) -> ExchangeConverterInterface:
        if exchange_type == ExchangeType.PFCF:
            return PFCFConverter()
        elif exchange_type == ExchangeType.YUANTA:
            return YuantaConverter()  # 元大期貨
        elif exchange_type == ExchangeType.CAPITAL:
            return CapitalConverter()  # 群益期貨
```

#### **服務容器** `src/infrastructure/services/service_container.py`
- **第28行**: `def __init__(self, exchange_api: PFCFApi)` ❌ 硬綁定
- **第45-58行**: PFCF 特定屬性訪問 ❌

### 4. 📊 **資料存取層**

#### **倉位存儲庫** `src/infrastructure/repositories/pfcf_position_repository.py`
- **第134-140行**: PFCF API 直接調用 ❌
- **第41-63行**: 22個 PFCF 特定參數處理 ❌

## 🏗️ 建議的重構架構

### **階段 1: 創建抽象層**

```python
# 1. 交易所 API 抽象介面
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

# 2. 數據轉換器抽象介面
class ExchangeConverterInterface(ABC):
    @abstractmethod
    def convert_side(self, side: Side) -> Any:
        pass
    
    @abstractmethod
    def convert_order_type(self, order_type: OrderType) -> Any:
        pass
```

### **階段 2: PFCF 實現類**

```python
# PFCF 具體實現
class PFCFExchangeApi(ExchangeApiInterface):
    def __init__(self):
        self._client = PFCFAPI()  # 封裝 PFCF 特定邏輯
    
    def send_order(self, order: OrderRequest) -> OrderResult:
        # 將標準 OrderRequest 轉換為 PFCF 格式
        pfcf_order = self._convert_to_pfcf_order(order)
        result = self._client.DTradeLib.Order(pfcf_order)
        return self._convert_from_pfcf_result(result)
```

### **階段 3: 其他券商實現**

```python
# 元大期貨實現範例
class YuantaExchangeApi(ExchangeApiInterface):
    def __init__(self):
        self._client = YuantaAPI()  # 元大 API
    
    def send_order(self, order: OrderRequest) -> OrderResult:
        # 轉換為元大格式並調用
        yuanta_order = self._convert_to_yuanta_order(order)
        result = self._client.PlaceOrder(yuanta_order)
        return self._convert_from_yuanta_result(result)
```

## 📋 移植檢查清單

### **🔍 第一階段：分析目標券商 API**

- [ ] **取得 API 文檔**: 研究目標券商的 DLL/API 結構
- [ ] **識別對等功能**: 登錄、下單、查詢倉位、市場數據
- [ ] **比較數據格式**: 訂單結構、回調參數、錯誤碼
- [ ] **確認事件模型**: 回調機制或輪詢機制

### **🏗️ 第二階段：建立抽象層**

- [ ] **定義抽象介面**: `ExchangeApiInterface`
- [ ] **設計標準化 DTO**: 券商中立的數據結構
- [ ] **創建轉換器介面**: `ExchangeConverterInterface`
- [ ] **重構服務容器**: 支援依賴注入抽象介面

### **🔧 第三階段：實現具體適配器**

- [ ] **PFCF 適配器**: 將現有代碼包裝到抽象介面
- [ ] **目標券商適配器**: 實現新券商的具體類別
- [ ] **配置管理**: 支援多券商配置切換
- [ ] **錯誤處理統一**: 標準化不同券商的錯誤格式

### **🧪 第四階段：測試和驗證**

- [ ] **單元測試**: 抽象介面和適配器
- [ ] **集成測試**: 端到端交易流程
- [ ] **並行測試**: PFCF 和新券商同時運行
- [ ] **性能測試**: 確保延遲沒有顯著增加

## 📝 配置範例

### **多券商支援配置**

```env
# .env 配置
EXCHANGE_PROVIDER=PFCF          # PFCF, YUANTA, CAPITAL
PFCF_TEST_URL=統一期貨測試URL
PFCF_PROD_URL=統一期貨正式URL
YUANTA_TEST_URL=元大期貨測試URL
YUANTA_PROD_URL=元大期貨正式URL
```

### **依賴注入配置**

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

## ⚡ 性能考量

### **抽象層開銷**

| 操作類型 | 預期開銷 | 優化策略 |
|---------|----------|----------|
| 訂單轉換 | < 0.1ms | 對象池化、預編譯轉換邏輯 |
| 數據序列化 | < 0.2ms | 使用 msgpack 而非 JSON |
| 介面調用 | < 0.05ms | 避免過度抽象，直接委託 |

### **記憶體管理**

- **對象重用**: 避免頻繁創建轉換對象
- **連接池**: 每個券商維護獨立的連接池
- **事件去耦**: 使用弱引用避免回調記憶體洩漏

## 🚨 常見陷阱

### **1. 過度抽象**
❌ 不要為了抽象而抽象，保持實用性
✅ 只抽象真正變化的部分

### **2. 性能損失**
❌ 避免多層轉換導致延遲增加
✅ 直接映射，避免中間格式

### **3. 錯誤處理不一致**
❌ 不同券商的錯誤格式差異巨大
✅ 定義統一的錯誤碼和訊息格式

### **4. 測試困難**
❌ 依賴真實券商 API 進行測試
✅ 創建模擬器支援離線測試

## 📈 預估工作量

| 階段 | 工作量 | 風險等級 |
|------|-------|----------|
| **抽象介面設計** | 3-5 天 | 🟡 中等 |
| **PFCF 適配器重構** | 5-8 天 | 🔴 高 |
| **新券商適配器** | 10-15 天 | 🔴 高 |
| **測試和調優** | 8-12 天 | 🟡 中等 |
| **總計** | **26-40 天** | 🔴 高 |

## 💡 成功關鍵因素

1. **深度理解目標 API**: 詳細研究券商 DLL 文檔
2. **漸進式重構**: 不要一次性重寫所有代碼
3. **完整測試覆蓋**: 確保重構後功能完全對等
4. **性能基準測試**: 確保抽象層不影響交易延遲
5. **回滾計劃**: 準備快速回復到 PFCF 版本的策略

---

**⚠️ 重要提醒**: 移植工作具有高度複雜性和風險。建議在充分測試環境中進行，並保持與原始 PFCF 版本的並行運行能力。

*如果您只是要使用統一期貨進行交易，建議直接使用現有系統，無需進行移植。*