# 🚀 策略擴展開發指南

## 📋 概述

本指南將指導您如何在台灣期貨自動交易系統中**擴展新策略**。目前系統只內建**支撐阻力策略**，但架構設計支援多策略擴展。

## 🏗️ 當前策略架構分析

### 現有支撐阻力策略結構

```
run_strategy.py
├── StrategySubscriber        # ZMQ 市場數據訂閱
├── SupportResistanceStrategy # 核心策略邏輯
├── SignalPublisher          # ZMQ 交易信號發布
└── TickEventHandler         # 處理tick事件
```

### 核心組件職責

| 組件 | 檔案位置 | 職責 |
|------|---------|------|
| **StrategySubscriber** | `run_strategy.py` | 訂閱端口5555的市場數據 |
| **SupportResistanceStrategy** | `run_strategy.py` | 實現右側進場支撐阻力邏輯 |
| **SignalPublisher** | `run_strategy.py` | 發布交易信號到端口5556 |
| **TickEventHandler** | `run_strategy.py` | 協調數據流與策略執行 |

## 🎯 策略接口設計

### 1. 抽象策略基類

```python
from abc import ABC, abstractmethod
from typing import List, Optional
from src.domain.entities.tick_event import TickEvent
from src.domain.entities.trading_signal import TradingSignal

class TradingStrategyInterface(ABC):
    """交易策略抽象介面"""
    
    @abstractmethod
    def initialize(self, config: dict) -> None:
        """策略初始化"""
        pass
    
    @abstractmethod
    def process_tick(self, tick_event: TickEvent) -> Optional[TradingSignal]:
        """處理tick數據並生成交易信號"""
        pass
    
    @abstractmethod
    def get_strategy_name(self) -> str:
        """獲取策略名稱"""
        pass
    
    @abstractmethod
    def get_required_params(self) -> List[str]:
        """獲取策略所需參數列表"""
        pass
    
    @abstractmethod
    def validate_params(self, params: dict) -> bool:
        """驗證策略參數"""
        pass
    
    @abstractmethod
    def reset_strategy(self) -> None:
        """重置策略狀態"""
        pass
```

### 2. 策略註冊管理器

```python
class StrategyManager:
    """策略管理器 - 支援多策略註冊與切換"""
    
    def __init__(self):
        self._strategies = {}
        self._active_strategy = None
    
    def register_strategy(self, strategy: TradingStrategyInterface) -> None:
        """註冊新策略"""
        name = strategy.get_strategy_name()
        self._strategies[name] = strategy
    
    def set_active_strategy(self, strategy_name: str) -> bool:
        """設定啟用策略"""
        if strategy_name in self._strategies:
            self._active_strategy = self._strategies[strategy_name]
            return True
        return False
    
    def process_tick(self, tick_event: TickEvent) -> Optional[TradingSignal]:
        """使用當前啟用策略處理tick"""
        if self._active_strategy:
            return self._active_strategy.process_tick(tick_event)
        return None
    
    def list_strategies(self) -> List[str]:
        """列出所有已註冊策略"""
        return list(self._strategies.keys())
```

## 📈 策略擴展範例

### 範例 1: 移動平均策略

```python
class MovingAverageStrategy(TradingStrategyInterface):
    """雙移動平均線交叉策略"""
    
    def __init__(self):
        self.short_period = 5
        self.long_period = 20
        self.short_ma_values = []
        self.long_ma_values = []
        self.last_signal = None
    
    def initialize(self, config: dict) -> None:
        """初始化策略參數"""
        self.short_period = config.get('short_period', 5)
        self.long_period = config.get('long_period', 20)
        self.quantity = config.get('quantity', 1)
        
    def process_tick(self, tick_event: TickEvent) -> Optional[TradingSignal]:
        """處理tick並生成交易信號"""
        price = tick_event.tick.match_price
        
        # 更新移動平均值
        self._update_moving_averages(price)
        
        # 檢查交叉信號
        if len(self.short_ma_values) < 2:
            return None
            
        current_short_ma = self._calculate_short_ma()
        current_long_ma = self._calculate_long_ma()
        
        previous_short_ma = self.short_ma_values[-2] if len(self.short_ma_values) >= 2 else 0
        previous_long_ma = self.long_ma_values[-2] if len(self.long_ma_values) >= 2 else 0
        
        # 黃金交叉 - 買入信號
        if (previous_short_ma <= previous_long_ma and 
            current_short_ma > current_long_ma and 
            self.last_signal != 'BUY'):
            
            self.last_signal = 'BUY'
            return TradingSignal(
                when=tick_event.when,
                operation=OrderOperation.BUY,
                commodity_id=tick_event.tick.commodity_id
            )
        
        # 死亡交叉 - 賣出信號
        elif (previous_short_ma >= previous_long_ma and 
              current_short_ma < current_long_ma and 
              self.last_signal != 'SELL'):
            
            self.last_signal = 'SELL'
            return TradingSignal(
                when=tick_event.when,
                operation=OrderOperation.SELL,
                commodity_id=tick_event.tick.commodity_id
            )
        
        return None
    
    def _update_moving_averages(self, price: float) -> None:
        """更新移動平均數列"""
        self.short_ma_values.append(price)
        self.long_ma_values.append(price)
        
        # 保持數列長度
        if len(self.short_ma_values) > self.short_period:
            self.short_ma_values.pop(0)
        if len(self.long_ma_values) > self.long_period:
            self.long_ma_values.pop(0)
    
    def _calculate_short_ma(self) -> float:
        """計算短期移動平均"""
        return sum(self.short_ma_values[-self.short_period:]) / min(len(self.short_ma_values), self.short_period)
    
    def _calculate_long_ma(self) -> float:
        """計算長期移動平均"""
        return sum(self.long_ma_values[-self.long_period:]) / min(len(self.long_ma_values), self.long_period)
    
    def get_strategy_name(self) -> str:
        return "移動平均交叉策略"
    
    def get_required_params(self) -> List[str]:
        return ['short_period', 'long_period', 'quantity']
    
    def validate_params(self, params: dict) -> bool:
        required = self.get_required_params()
        return all(param in params for param in required)
    
    def reset_strategy(self) -> None:
        self.short_ma_values.clear()
        self.long_ma_values.clear()
        self.last_signal = None
```

### 範例 2: RSI 策略

```python
class RSIStrategy(TradingStrategyInterface):
    """RSI相對強弱指標策略"""
    
    def __init__(self):
        self.period = 14
        self.oversold_level = 30
        self.overbought_level = 70
        self.price_changes = []
        self.last_price = None
        
    def initialize(self, config: dict) -> None:
        self.period = config.get('rsi_period', 14)
        self.oversold_level = config.get('oversold_level', 30)
        self.overbought_level = config.get('overbought_level', 70)
        
    def process_tick(self, tick_event: TickEvent) -> Optional[TradingSignal]:
        """處理tick並計算RSI"""
        current_price = tick_event.tick.match_price
        
        if self.last_price is None:
            self.last_price = current_price
            return None
        
        # 計算價格變化
        price_change = current_price - self.last_price
        self.price_changes.append(price_change)
        self.last_price = current_price
        
        # 保持期間長度
        if len(self.price_changes) > self.period:
            self.price_changes.pop(0)
        
        if len(self.price_changes) < self.period:
            return None
        
        # 計算RSI
        rsi = self._calculate_rsi()
        
        # 生成交易信號
        if rsi < self.oversold_level:
            return TradingSignal(
                when=tick_event.when,
                operation=OrderOperation.BUY,
                commodity_id=tick_event.tick.commodity_id
            )
        elif rsi > self.overbought_level:
            return TradingSignal(
                when=tick_event.when,
                operation=OrderOperation.SELL,
                commodity_id=tick_event.tick.commodity_id
            )
        
        return None
    
    def _calculate_rsi(self) -> float:
        """計算RSI指標"""
        gains = [change if change > 0 else 0 for change in self.price_changes]
        losses = [-change if change < 0 else 0 for change in self.price_changes]
        
        avg_gain = sum(gains) / len(gains)
        avg_loss = sum(losses) / len(losses)
        
        if avg_loss == 0:
            return 100
        
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        return rsi
    
    def get_strategy_name(self) -> str:
        return "RSI相對強弱指標策略"
    
    def get_required_params(self) -> List[str]:
        return ['rsi_period', 'oversold_level', 'overbought_level']
    
    def validate_params(self, params: dict) -> bool:
        required = self.get_required_params()
        return all(param in params for param in required)
    
    def reset_strategy(self) -> None:
        self.price_changes.clear()
        self.last_price = None
```

## 🔧 系統整合步驟

### 步驟 1: 修改 `run_strategy.py`

```python
# 原本的硬編碼策略
# from support_resistance_strategy import SupportResistanceStrategy

# 改為動態策略管理
from strategy_manager import StrategyManager
from strategies.support_resistance_strategy import SupportResistanceStrategy
from strategies.moving_average_strategy import MovingAverageStrategy
from strategies.rsi_strategy import RSIStrategy

def main():
    # 初始化策略管理器
    strategy_manager = StrategyManager()
    
    # 註冊所有策略
    strategy_manager.register_strategy(SupportResistanceStrategy())
    strategy_manager.register_strategy(MovingAverageStrategy())
    strategy_manager.register_strategy(RSIStrategy())
    
    # 從配置檔案或命令列參數選擇策略
    active_strategy = os.getenv('ACTIVE_STRATEGY', 'support_resistance')
    strategy_manager.set_active_strategy(active_strategy)
    
    # 原本的事件處理邏輯保持不變
    # 只需要將 strategy.process_tick() 改為 strategy_manager.process_tick()
```

### 步驟 2: 創建策略目錄結構

```
src/strategies/
├── __init__.py
├── base_strategy.py                 # 抽象基類
├── strategy_manager.py              # 策略管理器
├── support_resistance_strategy.py   # 現有策略重構
├── moving_average_strategy.py       # 移動平均策略
├── rsi_strategy.py                 # RSI策略
└── technical_indicators/           # 技術指標庫
    ├── __init__.py
    ├── moving_average.py
    ├── rsi.py
    ├── macd.py
    └── bollinger_bands.py
```

### 步驟 3: 擴展配置系統

```python
# config.py 添加策略配置
class StrategyConfig:
    def __init__(self):
        self.active_strategy = os.getenv('ACTIVE_STRATEGY', 'support_resistance')
        self.strategy_params = self._load_strategy_params()
    
    def _load_strategy_params(self) -> dict:
        """從環境變數或配置檔案載入策略參數"""
        return {
            'support_resistance': {
                'turning_point': int(os.getenv('SR_TURNING_POINT', '15')),
                'take_profit': int(os.getenv('SR_TAKE_PROFIT', '90')),
                'stop_loss': int(os.getenv('SR_STOP_LOSS', '30')),
                'is_following': os.getenv('SR_FOLLOWING', 'true').lower() == 'true'
            },
            'moving_average': {
                'short_period': int(os.getenv('MA_SHORT_PERIOD', '5')),
                'long_period': int(os.getenv('MA_LONG_PERIOD', '20')),
                'quantity': int(os.getenv('MA_QUANTITY', '1'))
            },
            'rsi': {
                'rsi_period': int(os.getenv('RSI_PERIOD', '14')),
                'oversold_level': float(os.getenv('RSI_OVERSOLD', '30')),
                'overbought_level': float(os.getenv('RSI_OVERBOUGHT', '70'))
            }
        }
```

## 🎮 CLI 界面擴展

### 新增策略選擇控制器

```python
class StrategySelectionController:
    """策略選擇控制器"""
    
    def __init__(self, strategy_manager: StrategyManager):
        self.strategy_manager = strategy_manager
    
    def execute(self) -> dict:
        """執行策略選擇"""
        print("=== 可用策略列表 ===")
        strategies = self.strategy_manager.list_strategies()
        
        for i, strategy_name in enumerate(strategies, 1):
            print(f"{i}. {strategy_name}")
        
        try:
            choice = int(input("選擇策略 (輸入數字): ")) - 1
            if 0 <= choice < len(strategies):
                selected_strategy = strategies[choice]
                success = self.strategy_manager.set_active_strategy(selected_strategy)
                
                if success:
                    return {
                        'action': 'strategy_selected',
                        'message': f'已選擇策略: {selected_strategy}',
                        'strategy': selected_strategy
                    }
                else:
                    return {
                        'action': 'strategy_selection_failed',
                        'message': '策略選擇失敗'
                    }
            else:
                return {
                    'action': 'invalid_choice',
                    'message': '無效的選擇'
                }
                
        except ValueError:
            return {
                'action': 'invalid_input',
                'message': '請輸入有效數字'
            }
```

## 📊 技術指標庫

### 建立可重用的技術指標庫

```python
# src/strategies/technical_indicators/moving_average.py
class MovingAverage:
    """移動平均計算器"""
    
    def __init__(self, period: int):
        self.period = period
        self.values = []
    
    def update(self, value: float) -> float:
        """更新數值並返回移動平均"""
        self.values.append(value)
        if len(self.values) > self.period:
            self.values.pop(0)
        return sum(self.values) / len(self.values)
    
    def is_ready(self) -> bool:
        """是否有足夠數據計算移動平均"""
        return len(self.values) >= self.period

# src/strategies/technical_indicators/rsi.py  
class RSI:
    """RSI計算器"""
    
    def __init__(self, period: int = 14):
        self.period = period
        self.price_changes = []
        self.last_price = None
    
    def update(self, price: float) -> Optional[float]:
        """更新價格並返回RSI值"""
        if self.last_price is None:
            self.last_price = price
            return None
        
        change = price - self.last_price
        self.price_changes.append(change)
        self.last_price = price
        
        if len(self.price_changes) > self.period:
            self.price_changes.pop(0)
        
        if len(self.price_changes) < self.period:
            return None
        
        return self._calculate_rsi()
    
    def _calculate_rsi(self) -> float:
        gains = [c if c > 0 else 0 for c in self.price_changes]
        losses = [-c if c < 0 else 0 for c in self.price_changes]
        
        avg_gain = sum(gains) / len(gains)
        avg_loss = sum(losses) / len(losses)
        
        if avg_loss == 0:
            return 100
        
        rs = avg_gain / avg_loss
        return 100 - (100 / (1 + rs))
```

## 🚀 實際應用範例

### 多策略組合管理

```python
class MultiStrategyManager:
    """多策略組合管理器"""
    
    def __init__(self):
        self.strategies = {}
        self.weights = {}
        
    def add_strategy(self, strategy: TradingStrategyInterface, weight: float = 1.0):
        """添加策略並設定權重"""
        name = strategy.get_strategy_name()
        self.strategies[name] = strategy
        self.weights[name] = weight
    
    def process_tick(self, tick_event: TickEvent) -> List[TradingSignal]:
        """處理tick並整合多策略信號"""
        signals = []
        
        for name, strategy in self.strategies.items():
            signal = strategy.process_tick(tick_event)
            if signal:
                # 根據權重調整信號強度
                weighted_signal = self._apply_weight(signal, self.weights[name])
                signals.append(weighted_signal)
        
        return self._combine_signals(signals)
    
    def _apply_weight(self, signal: TradingSignal, weight: float) -> TradingSignal:
        """應用策略權重"""
        # 可以調整數量或信號強度
        return signal
    
    def _combine_signals(self, signals: List[TradingSignal]) -> List[TradingSignal]:
        """整合多個信號"""
        # 可以實現投票機制、信號過濾等邏輯
        return signals
```

## 📋 開發檢查清單

### ✅ 新策略開發檢查

- [ ] **繼承 TradingStrategyInterface**
- [ ] **實現所有抽象方法**
- [ ] **定義清楚的參數需求**
- [ ] **實現參數驗證邏輯**
- [ ] **編寫詳細的測試案例**
- [ ] **文檔化策略邏輯**
- [ ] **性能測試 (< 1ms 處理時間)**

### ✅ 系統整合檢查

- [ ] **註冊到 StrategyManager**
- [ ] **添加到配置系統**
- [ ] **擴展 CLI 選項**
- [ ] **更新環境變數文檔**
- [ ] **集成測試通過**

## ⚠️ 重要注意事項

### 性能要求
- **Tick 處理**: < 1ms (維持高頻交易性能)
- **記憶體使用**: 避免無限增長的數據結構
- **線程安全**: 策略可能在多線程環境下運行

### 風險控制
- **參數驗證**: 嚴格驗證所有輸入參數
- **異常處理**: 妥善處理計算異常和數據錯誤
- **回測驗證**: 新策略必須經過充分回測

### 系統相容性
- **保持 ZMQ 通信協議不變**
- **維持現有 TradingSignal 格式**
- **確保向後相容性**

---

通過這個擴展指南，您可以輕鬆地在現有系統中添加新的交易策略，同時保持系統的穩定性和性能。記住始終先在測試環境中驗證新策略，再部署到生產環境！