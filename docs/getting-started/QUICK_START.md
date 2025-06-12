# 🚀 Quick Start Guide

> *Get your automated trading system running in 5 minutes!*

## 📋 Prerequisites

Before you begin, ensure you have:
- ✅ Python 3.8 or higher
- ✅ Exchange API credentials (we'll show you how)
- ✅ Basic command line knowledge
- ✅ 5 minutes of your time

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

## 🔐 Step 2: Configure Credentials

> **🌟 Prerequisite: Obtain PFCF Python DLL API**  
> Apply to Taiwan Unified Futures (PFCF) for their proprietary Python DLL API at https://www.pfcf.com.tw/software/detail/2709 and place the DLL files into `src/infrastructure/pfcf_client/dll`.

Create a `.env` file in the project root:

```bash
# Copy the example file (if provided)
cp .env.example .env  # macOS/Linux
copy .env.example .env  # Windows

# Or manually create .env
```

Edit `.env` with your favorite editor and add:

```env
# PFCF API endpoints (required)
DEALER_TEST_URL=your_test_url_here
DEALER_PROD_URL=your_prod_url_here

# Optional: Trading mode (paper trading when true)
TEST_MODE=true
```

Refer to [Configuration Guide](../CONFIG_GUIDE.md) for advanced environment variable options.

## 🏃 Step 3: Run the System

```bash
# Start the trading system
python app.py
```

You'll see the main menu:
```
╔════════════════════════════════════════╗
║    Auto Futures Trading Machine        ║
║    Version 1.0.0                       ║
╚════════════════════════════════════════╝

Please select an option:
- 0. Exit
- 1. User Login
- 2. User Logout
- 3. Register Item
- 4. Create Condition
- 5. Select Order Account
- 6. Send Market Order
- 7. Show Futures
- 8. Get Current Positions
- 10. Start All Components

Enter your choice:
```

## 🎮 Step 4: Basic Workflow

### 1️⃣ Login First
```
Enter your choice: 1
Username: your_username
Password: ********
✅ Login successful!
```

### 2️⃣ Register a Trading Item
```
Enter your choice: 3

Available Futures:
1. AAPL - Apple Inc.
2. TSLA - Tesla Inc.
3. BTC - Bitcoin Futures

Select item (1-3): 2
✅ Registered TSLA for trading
```

### 3️⃣ Create Trading Conditions
```
Enter your choice: 4

Creating Support/Resistance Condition:
Support Level: 240.50
Resistance Level: 255.75
Position Size: 10

✅ Condition created successfully!
```

### 4️⃣ Select Trading Account
```
Enter your choice: 5

Available Accounts:
1. Main Account (Balance: $50,000)
2. Test Account (Balance: $10,000)

Select account: 1
✅ Main Account selected
```

### 5️⃣ Check Current Positions
```
Enter your choice: 8
Account: 0290621
Enter product id (leave blank for all):
No position data or list of positions
```

### 6️⃣ Start Automated Trading
```
Enter your choice: 10

🚀 Starting Auto-Trading System...
✅ Gateway: Running (Port 5555)
✅ Strategy: Running (Port 5556)
✅ Order Executor: Running (Port 5557)

System is now trading automatically!
Press Ctrl+C to stop.
```

## 🛑 Step 5: Stopping the System

### Graceful Shutdown
Press `Ctrl+C` in the main terminal:
```
^C
🛑 Stopping trading system...
✅ All positions closed
✅ Processes terminated cleanly
✅ Logs saved to: logs/session_20240315_143022.log

Goodbye!
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