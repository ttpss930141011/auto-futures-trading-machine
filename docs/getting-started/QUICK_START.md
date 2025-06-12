# 🚀 Quick Start Guide - 台灣期貨自動交易

> *Taiwan Futures Automated Trading System - 統一期貨專用*

## ⚠️ 重要說明

**這不是通用交易系統**：本系統專為台灣統一期貨 (PFCF) 設計，高度依賴統一期貨的 Python DLL API。如果您不是統一期貨的客戶，此系統將無法使用。

> 💡 **需要移植到其他券商？** 請參閱 [DLL 移植指南](../architecture/DLL_PORTING_GUIDE.md) 了解如何將系統移植到元大期貨、群益期貨等其他券商。

## 📋 Prerequisites

開始前，您必須具備：
- ✅ **統一期貨開戶** - 必須是統一期貨客戶
- ✅ **PFCF Python DLL API** - 向統一期貨申請 API 權限
- ✅ Python 3.12 或更高版本
- ✅ Windows 作業系統 (DLL 需求)
- ✅ 基本命令列操作知識

## 🎯 Step 1: Clone and Install

```bash
# Clone the repository
git clone https://github.com/ttpss930141011/futures-trading-machine.git
cd futures-trading-machine

# Install dependencies using poetry (recommended)
poetry install

# Or using pip
pip install -r requirements.txt
```

## 🔐 Step 2: 統一期貨 API 設置

### 申請 PFCF Python DLL API
1. 聯繫統一期貨客服申請 Python DLL API 權限
2. 下載統一期貨提供的 DLL 檔案
3. 將 DLL 檔案放置到 `src/infrastructure/pfcf_client/dll/`

### 配置環境變數
創建 `.env` 檔案：

```bash
# Windows
copy .env.example .env

# 或手動創建 .env
```

編輯 `.env` 並加入統一期貨提供的資訊：

```env
# 統一期貨 API 端點 (必須向統一期貨取得)
DEALER_TEST_URL=統一期貨提供的測試環境URL
DEALER_PROD_URL=統一期貨提供的正式環境URL

# 其他設定
TEST_MODE=true  # 測試模式
```

⚠️ **重要**：API 端點和憑證必須向統一期貨申請，無法自行取得。

## 🏃 Step 3: 啟動系統

```bash
# 啟動交易系統
python app.py
```

您會看到系統啟動訊息和主選單：
```
Initializing Auto Futures Trading Machine with DLL Gateway...
✓ DLL Gateway Server: Running on tcp://127.0.0.1:5557
✓ Exchange API: Centralized access through gateway
✓ Multi-process support: Enhanced security and stability

IMPORTANT: AllInOneController (option 10) now uses Gateway architecture
All processes will communicate through the centralized DLL Gateway.

Please choose an option:
0: ExitController
1: UserLoginController
2: UserLogoutController
3: RegisterItemController
4: CreateConditionController
5: SelectOrderAccountController
6: SendMarketOrderController
7: ShowFuturesController
8: GetPositionController
10: AllInOneController
```

## 🎮 Step 4: 完整操作流程 (根據實際使用)

### 1️⃣ 使用統一期貨帳號登錄
```
> 1
Enter the account: 80020290621
Enter the password: [輸入密碼]
Is this login for production?[y/n](blank for n): y

訊息平台連線成功
內期報價連線
內期帳務連線
Login status: 登入成功!
{'action': 'user_login', 'message': 'User logged in successfully', 
 'account': '80020290621', 'ip_address': '122.147.227.66'}
```

### 2️⃣ 查看可交易期貨商品
```
> 7
Enter futures code (leave empty for all): MXF

Found 6 futures items

==== Futures Data ====
    商品代號         商品名稱         標的物        交割月份       市場代碼       部位價格          到期日
--------------------------------------------------------------------------------
   MXFF5          小臺指                   202506      MXF       22253
   MXFG5          小臺指                   202507      MXF       21953
   MXFH5          小臺指                   202508      MXF       21805
   MXFI5          小臺指                   202509      MXF       21720
   MXFL5          小臺指                   202512      MXF       21631
   MXFC6          小臺指                   202603      MXF       21560
--------------------------------------------------------------------------------
Total items: 6
```

### 3️⃣ 註冊要交易的商品 (以小台指為例)
```
> 3
Enter item code: MXFF5
{'action': 'register_item', 'message': 'User registered successfully'}
```

### 4️⃣ 創建交易條件 (支撐阻力策略)
```
> 4
Enter the action (b/s): b
Enter the target price: 22000
Enter the turning point: 30
Enter the quantity: 1
Enter the take profit point (blank for default): 120
Enter the stop loss point (blank for default): 30
Enter if the condition is following (y/n): y

{'action': 'create_condition', 'message': 'Condition 9a615336-39ee-44a3-aa30-d123ea9fde27 is created successfully',
 'condition': {...}}
```

### 5️⃣ 選擇交易帳戶
```
> 5
Select the order account:
1. 0290621

Enter the account number: 1
{'action': 'select_order_account', 'message': 'Order account selected: 0290621'}
```

### 6️⃣ 檢查系統前置條件
```
> 10
=== System Prerequisites ===
User logged in: ✓
Item registered: ✓
Order account selected: ✓
Trading conditions defined: ✓
===========================
```

### 7️⃣ 啟動自動交易系統
```
> 10
=== Starting All Trading System Components ===

=== System Startup Results ===
Overall Status: ✓ Success
Gateway: ✓ Running
Strategy: ✓ Running
Order Executor: ✓ Running
=============================

Strategy process started. Waiting for market data...
Order executor gateway process started. Waiting for trading signals...
```

## 🛑 Step 5: 停止系統

### 登出並停止系統
```
> 2  # 登出
內期報價斷線
內期帳務斷線
Login status: 登出成功!
{'action': 'logout', 'message': 'User logout successfully', 
 'account': '80020290621', 'is_success': True}

> 0  # 退出程式
Exiting the program

Shutting down application...
```

### 或使用 Ctrl+C 強制停止
在主終端機按 `Ctrl+C`：
```
^C
Shutting down application...
```

## 🔧 Common Issues & Solutions

### Issue: "Connection refused"
```bash
# Check if ports are available
netstat -an | grep -E "5555|5556|5557"

# If ports are in use, kill the processes
# Windows:
netstat -ano | findstr :5555
taskkill /PID <pid> /F

# Linux/Mac:
lsof -i :5555
kill -9 <pid>
```

### Issue: "Invalid credentials"
- Double-check your `.env` file
- Ensure no extra spaces in credentials
- Try with `TEST_MODE=true` first

### Issue: "No module named 'zmq'"
```bash
# Install ZeroMQ
pip install pyzmq
```

## 🎉 Success! What's Next?

Congratulations! Your trading system is running. Here's what to explore next:

1. **📚 [Understand the Architecture](../architecture/ARCHITECTURE_OVERVIEW.md)**
   - Learn how components communicate
   - Understand the event-driven design

2. **📈 [Configure Your Strategy](../trading/SUPPORT_RESISTANCE.md)**
   - Fine-tune support/resistance levels
   - Adjust risk parameters

3. **🧪 [Run Backtests](../guides/BACKTESTING.md)**
   - Test your strategy on historical data
   - Optimize parameters

4. **📊 [Set Up Monitoring](../guides/MONITORING.md)**
   - Configure Grafana dashboards
   - Set up alerts

## 💡 Pro Tips

1. **Start in Test Mode**: Always test with paper trading first
2. **Small Positions**: Begin with minimal position sizes
3. **Monitor Closely**: Watch the system for the first few hours
4. **Check Logs**: Review logs daily for insights
5. **Join Community**: Get help in our Discord server

## 🆘 Need Help?

- 🐛 Report issues on [GitHub](https://github.com/ttpss930141011/futures-trading-machine/issues)

---

*Remember: Start small, test thoroughly, and never trade more than you can afford to lose.*

**Ready for more?** Dive into the [Architecture Overview](../architecture/ARCHITECTURE_OVERVIEW.md) → 