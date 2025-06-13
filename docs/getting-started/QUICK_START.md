# 🚀 Quick Start Guide - Taiwan Futures Automated Trading

> *Taiwan Futures Automated Trading System - Specifically for Polaris Futures Capital Future (PFCF)*

## ⚠️ Important Notice

**This is not a generic trading system**: This system is specifically designed for Taiwan Unified Futures (PFCF) and is highly dependent on their proprietary Python DLL API. If you are not a customer of Taiwan Unified Futures, this system will not work for you.

> 💡 **Need to migrate to other brokers?** Please refer to the [DLL Porting Guide](../architecture/DLL_PORTING_GUIDE.md) to learn how to migrate the system to other brokers like Yuanta Securities, Capital Futures, etc.

## 📋 Prerequisites

Before you begin, you must have:
- ✅ **Taiwan Unified Futures Account** - Must be a customer of Taiwan Unified Futures
- ✅ **PFCF Python DLL API** - Apply for API permissions from Taiwan Unified Futures
- ✅ Python 3.12 or higher
- ✅ Windows Operating System (DLL requirement)
- ✅ Basic command line knowledge

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

## 🔐 Step 2: Taiwan Unified Futures API Setup

### Apply for PFCF Python DLL API
1. Contact Taiwan Unified Futures customer service to apply for Python DLL API permissions
2. Download the DLL files provided by Taiwan Unified Futures
3. Place the DLL files in `src/infrastructure/pfcf_client/dll/`

### Configure Environment Variables
Create a `.env` file:

```bash
# Windows
copy .env.example .env

# Or manually create .env
```

Edit `.env` and add the information provided by Taiwan Unified Futures:

```env
# Taiwan Unified Futures API endpoints (must be obtained from Taiwan Unified Futures)
DEALER_TEST_URL=Test_environment_URL_provided_by_Taiwan_Unified_Futures
DEALER_PROD_URL=Production_environment_URL_provided_by_Taiwan_Unified_Futures

# Other settings
TEST_MODE=true  # Test mode
```

⚠️ **Important**: API endpoints and credentials must be applied for from Taiwan Unified Futures and cannot be obtained independently.

## 🏃 Step 3: Start the System

```bash
# Start the trading system
python app.py
```

You will see the system startup messages and main menu:
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

## 🎮 Step 4: Complete Operation Workflow (Based on Actual Usage)

### 1️⃣ Login with Taiwan Unified Futures Account
```
> 1
Enter the account: 80020290621
Enter the password: [Enter your password]
Is this login for production?[y/n](blank for n): y

Message platform connection successful
Domestic futures quote connection
Domestic futures account connection
Login status: Login successful!
{'action': 'user_login', 'message': 'User logged in successfully', 
 'account': '80020290621', 'ip_address': '122.147.227.66'}
```

### 2️⃣ View Available Futures Products
```
> 7
Enter futures code (leave empty for all): MXF

Found 6 futures items

==== Futures Data ====
    Product Code     Product Name     Underlying    Delivery Month    Market Code    Position Price    Expiry Date
--------------------------------------------------------------------------------
   MXFF5          Mini Taiwan Index                202506      MXF       22253
   MXFG5          Mini Taiwan Index                202507      MXF       21953
   MXFH5          Mini Taiwan Index                202508      MXF       21805
   MXFI5          Mini Taiwan Index                202509      MXF       21720
   MXFL5          Mini Taiwan Index                202512      MXF       21631
   MXFC6          Mini Taiwan Index                202603      MXF       21560
--------------------------------------------------------------------------------
Total items: 6
```

### 3️⃣ Register Trading Product (Using Mini Taiwan Index as Example)
```
> 3
Enter item code: MXFF5
{'action': 'register_item', 'message': 'User registered successfully'}
```

### 4️⃣ Create Trading Conditions (Support/Resistance Strategy)
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

### 5️⃣ Select Trading Account
```
> 5
Select the order account:
1. 0290621

Enter the account number: 1
{'action': 'select_order_account', 'message': 'Order account selected: 0290621'}
```

### 6️⃣ Check System Prerequisites
```
> 10
=== System Prerequisites ===
User logged in: ✓
Item registered: ✓
Order account selected: ✓
Trading conditions defined: ✓
===========================
```

### 7️⃣ Start Automated Trading System
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

## 🛑 Step 5: Stop the System

### Logout and Stop System
```
> 2  # Logout
Domestic futures quote disconnected
Domestic futures account disconnected
Login status: Logout successful!
{'action': 'logout', 'message': 'User logout successfully', 
 'account': '80020290621', 'is_success': True}

> 0  # Exit program
Exiting the program

Shutting down application...
```

### Or Use Ctrl+C to Force Stop
Press `Ctrl+C` in the main terminal:
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

1. **📚 [Understand the Architecture](../architecture/CLASS_DESIGN_GUIDE.md)**
   - Learn how components communicate
   - Understand the clean architecture design

2. **📈 [Learn Strategy Details](../guides/STRATEGY_EXPANSION_GUIDE.md)**
   - Understand the support/resistance strategy
   - Learn how to add new strategies

3. **🧪 [Run Backtests](../guides/BACKTESTING.md)**
   - Test your strategy on historical data
   - Optimize parameters

4. **📊 [Set Up Monitoring](../guides/MONITORING.md)**
   - Configure system monitoring
   - Set up alerts

## 💡 Pro Tips

1. **Start in Test Mode**: Always test with paper trading first
2. **Small Positions**: Begin with minimal position sizes
3. **Monitor Closely**: Watch the system for the first few hours
4. **Check Logs**: Review logs daily for insights
5. **Understanding Architecture**: Study the system design before customization

## 🆘 Need Help?

- 🐛 Report issues on [GitHub](https://github.com/ttpss930141011/futures-trading-machine/issues)

---

*Remember: Start small, test thoroughly, and never trade more than you can afford to lose.*

**Ready for more?** Dive into the [Class Design Guide](../architecture/CLASS_DESIGN_GUIDE.md) →