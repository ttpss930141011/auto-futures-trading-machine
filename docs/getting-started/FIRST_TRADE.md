# 🎯 First Trade Tutorial

> *Walk through your first automated futures trade step by step*

## 1. Login

1. Launch the application:
   ```bash
   python app.py
   ```
2. At the menu, choose `1` for **User Login**:
   ```text
   Enter your choice: 1
   Username: your_username
   Password: ********
   ✅ Login successful!
   ```

## 2. Register an Item to Trade

1. Choose `3` for **Register Item**:
   ```text
   Enter your choice: 3
   
   Available Futures:
   1. AAPL  2. TSLA  3. BTC
   
   Select item (1-3): 2
   ✅ Registered TSLA for trading
   ```

## 3. Create a Trading Condition

1. Choose `4` for **Create Condition**:
   ```text
   Enter your choice: 4
   
   Support Level: 250.00
   Resistance Level: 260.00
   Quantity: 1
   Take Profit Point: 5
   Stop Loss Point: 3
   Follow Market Price? [y/n]: y
   ✅ Condition created successfully!
   ```

## 4. Select an Order Account

1. Choose `5` for **Select Order Account**:
   ```text
   Enter your choice: 5
   
   Available Accounts:
   1. Main (50,000 USD)
   2. Test (10,000 USD)
   
   Select account: 1
   ✅ Main Account selected
   ```

## 5. Start Automated Trading

1. Choose `10` for **Start All Components**:
   ```text
   Enter your choice: 10
   
   🚀 Starting Auto-Trading System...
   ✅ Gateway: Running
   ✅ Strategy: Running
   ✅ Order Executor: Running
   ```
2. The system now runs in the background, watching ticks and placing orders automatically.

## 6. Monitor Your Trade

While trading, check your positions:
```text
Enter your choice: 8
Account: your_account_id
Enter product code (leave blank for all):
// Displays open positions or "No position data"
```

## 7. Stop Trading

Press `Ctrl+C` in the terminal running `app.py`:
```text
^C
🛑 Shutting down system...
✅ All processes stopped
✅ Logs saved to logs/session_<timestamp>.log
Goodbye!
```

---

*Congratulations on your first automated trade!* 