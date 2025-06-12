# 🎯 第一筆自動交易教學 - 統一期貨小台指

> *逐步完成您的第一筆台灣期貨自動交易*

## ⚠️ 重要前提

- 您必須是**統一期貨客戶**且已申請 API 權限
- 此教學以**小台指 (MXFF5)** 為範例
- 建議先在**測試環境**練習

## 📈 策略說明

本系統目前內建**唯一策略**：**右側進場支撐阻力策略**

### 策略特色
- **右側進場**: 不搶反彈，等價格確認反轉後才進場
- **動態追蹤**: 可根據市場走勢調整進場點位
- **風險控制**: 內建停利停損與假突破過濾機制

### 運作原理 (買入範例)
1. **觸發條件**: 價格跌破支撐位 (Target Price) 時啟動策略
2. **等待確認**: 價格反彈至 `Target Price + Turning Point` 時才實際買入
3. **風險控制**: 自動設定停利 (+120點) 和停損 (-30點)

---

## 1. 統一期貨帳號登錄

1. 啟動應用程式：
   ```bash
   python app.py
   ```

2. 選擇 `1` 進行登錄：
   ```text
   > 1
   Enter the account: 80020290621        # 您的統一期貨帳號
   Enter the password: [輸入密碼]         # 您的統一期貨密碼
   Is this login for production?[y/n](blank for n): y  # y=正式環境, n=測試環境
   
   訊息平台連線成功
   內期報價連線
   內期帳務連線
   Login status: 登入成功!
   ```

## 2. 查看可交易的期貨商品

1. 選擇 `7` 查看期貨商品：
   ```text
   > 7
   Enter futures code (leave empty for all): MXF  # 小台指代碼
   
   Found 6 futures items
   ==== Futures Data ====
       商品代號         商品名稱         標的物        交割月份       市場代碼       部位價格
   --------------------------------------------------------------------------------
      MXFF5          小臺指                   202506      MXF       22253
      MXFG5          小臺指                   202507      MXF       21953
      # ... 其他月份合約
   ```

## 3. 註冊要交易的商品

1. 選擇 `3` 註冊商品：
   ```text
   > 3
   Enter item code: MXFF5              # 選擇最近月份的小台指
   {'action': 'register_item', 'message': 'User registered successfully'}
   ```

## 4. 創建支撐阻力交易條件

1. 選擇 `4` 創建交易條件：
   ```text
   > 4
   Enter the action (b/s): b                    # b=買進, s=賣出
   Enter the target price: 22000               # 目標價格 (突破點)
   Enter the turning point: 30                 # 轉折點 (點數)
   Enter the quantity: 1                       # 交易口數
   Enter the take profit point (blank for default): 120  # 停利點 (點數)
   Enter the stop loss point (blank for default): 30    # 停損點 (點數)
   Enter if the condition is following (y/n): y          # 是否跟隨市價
   
   ✅ 交易條件創建成功！
   ```

## 5. 選擇交易帳戶

1. 選擇 `5` 設定交易帳戶：
   ```text
   > 5
   Select the order account:
   1. 0290621                          # 您的期貨交易帳戶
   
   Enter the account number: 1
   {'action': 'select_order_account', 'message': 'Order account selected: 0290621'}
   ```

## 6. 檢查系統前置條件

1. 選擇 `10` 檢查是否可以啟動：
   ```text
   > 10
   === System Prerequisites ===
   User logged in: ✓                   # 已登錄
   Item registered: ✓                  # 已註冊商品
   Order account selected: ✓           # 已選擇帳戶
   Trading conditions defined: ✓       # 已定義交易條件
   ===========================
   ```

## 7. 啟動自動交易系統

1. 再次選擇 `10` 啟動系統：
   ```text
   > 10
   === Starting All Trading System Components ===
   
   === System Startup Results ===
   Overall Status: ✓ Success
   Gateway: ✓ Running                  # DLL Gateway 運行中
   Strategy: ✓ Running                 # 策略進程運行中  
   Order Executor: ✓ Running           # 訂單執行進程運行中
   =============================
   
   Strategy process started. Waiting for market data...
   Order executor gateway process started. Waiting for trading signals...
   ```

🎉 **恭喜！您的自動交易系統已啟動**

系統現在會：
- 監聽小台指 (MXFF5) 的即時報價
- 當價格突破 22000 點時，自動買進 1 口
- 停利目標：22120 點 (獲利 120 點)
- 停損目標：21970 點 (虧損 30 點)

## 8. 監控交易狀態

檢查倉位：
```text
> 8
Account: 0290621
Enter product id (leave blank for all): [留空查看所有部位]
```

## 9. 停止交易系統

### 正常登出
```text
> 2  # 統一期貨系統登出
內期報價斷線
內期帳務斷線
Login status: 登出成功!

> 0  # 退出程式
Exiting the program
```

---

## 💡 交易參數說明

| 參數 | 範例值 | 說明 |
|------|-------|------|
| **Target Price** | 22000 | 支撐/阻力位價格，作為策略觸發基準點 |
| **Turning Point** | 30 | 從觸發點到實際進場的點數差距 (避免假突破) |
| **Quantity** | 1 | 交易口數 (建議新手從 1 口開始) |
| **Take Profit** | 120 | 停利點數 (自動獲利了結) |
| **Stop Loss** | 30 | 停損點數 (風險控制機制) |
| **Following** | y | **動態追蹤**: 啟用後系統會根據價格變化調整進場點位 |

### Following 動態追蹤詳解

**Following = Yes 的運作機制**:
- **買入策略**: 如果價格持續下跌至更低點，系統會自動調整支撐位向下，等待更好的進場時機
- **賣出策略**: 如果價格持續上漲至更高點，系統會自動調整阻力位向上，等待更好的進場時機
- **優勢**: 避免在錯誤時機進場，提高策略成功率
- **風險**: 可能錯過快速反轉的機會

**範例說明** (買入, Following=Yes):
1. 設定支撐位 22000，轉折點 30
2. 價格跌至 21980 → 觸發策略，等待反彈至 22010 進場
3. 價格繼續跌至 21950 → 系統調整支撐位為 21950，新進場點為 21980
4. 價格反彈至 21985 → 系統發出買入信號

## ⚠️ 風險提醒

- **期貨交易具有高風險**，可能導致全部資金損失
- **建議新手從小口數開始**，熟悉系統後再增加
- **務必設定停損**，控制最大損失
- **監控系統運行狀況**，發現異常立即停止

## 🚀 策略擴展

目前系統只提供**支撐阻力策略**，如果您需要：
- **其他技術指標策略** (MA, RSI, MACD 等)
- **量化策略** (統計套利、配對交易等)  
- **多策略組合管理**

請參考 **[策略擴展開發指南](../guides/STRATEGY_EXPANSION_GUIDE.md)** 了解如何擴展系統。

---

*祝您交易順利！記住：永遠不要投資超過您能承受損失的資金。*