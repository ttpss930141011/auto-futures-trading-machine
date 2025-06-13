# 🎯 First Automated Trade Tutorial - Taiwan Unified Futures Mini Index

> *Step-by-step guide to complete your first Taiwan futures automated trade*

## ⚠️ Important Prerequisites

- You must be a **Taiwan Unified Futures customer** and have applied for API permissions
- This tutorial uses **Mini Taiwan Index (MXFF5)** as an example
- It is recommended to practice in **test environment** first

## 📈 Strategy Overview

This system currently has **one built-in strategy**: **Right-side Entry Support/Resistance Strategy**

### Strategy Features
- **Right-side Entry**: Don't catch falling knives, wait for price confirmation reversal before entry
- **Dynamic Tracking**: Can adjust entry points based on market movements
- **Risk Control**: Built-in take profit, stop loss, and false breakout filtering mechanisms

### Operating Principle (Buy Example)
1. **Trigger Condition**: Strategy activates when price breaks below support level (Target Price)
2. **Wait for Confirmation**: Actually buy when price rebounds to `Target Price + Turning Point`
3. **Risk Control**: Automatically set take profit (+120 points) and stop loss (-30 points)

---

## 1. Taiwan Unified Futures Account Login

1. Start the application:
   ```bash
   python app.py
   ```

2. Select `1` to login:
   ```text
   > 1
   Enter the account: 80020290621        # Your Taiwan Unified Futures account
   Enter the password: [Enter password]  # Your Taiwan Unified Futures password
   Is this login for production?[y/n](blank for n): y  # y=production, n=test environment
   
   Message platform connection successful
   Domestic futures quote connection
   Domestic futures account connection
   Login status: Login successful!
   ```

## 2. View Available Futures Products

1. Select `7` to view futures products:
   ```text
   > 7
   Enter futures code (leave empty for all): MXF  # Mini Taiwan Index code
   
   Found 6 futures items
   ==== Futures Data ====
       Product Code     Product Name     Underlying    Delivery Month    Market Code    Position Price
   --------------------------------------------------------------------------------
      MXFF5          Mini Taiwan Index              202506      MXF       22253
      MXFG5          Mini Taiwan Index              202507      MXF       21953
      # ... other monthly contracts
   ```

## 3. Register Trading Product

1. Select `3` to register product:
   ```text
   > 3
   Enter item code: MXFF5              # Select nearest month Mini Taiwan Index
   {'action': 'register_item', 'message': 'User registered successfully'}
   ```

## 4. Create Support/Resistance Trading Conditions

1. Select `4` to create trading conditions:
   ```text
   > 4
   Enter the action (b/s): b                    # b=buy, s=sell
   Enter the target price: 22000               # Target price (breakout point)
   Enter the turning point: 30                 # Turning point (points)
   Enter the quantity: 1                       # Trading quantity
   Enter the take profit point (blank for default): 120  # Take profit points
   Enter the stop loss point (blank for default): 30    # Stop loss points
   Enter if the condition is following (y/n): y          # Dynamic tracking
   
   ✅ Trading conditions created successfully!
   ```

## 5. Select Trading Account

1. Select `5` to configure trading account:
   ```text
   > 5
   Select the order account:
   1. 0290621                          # Your futures trading account
   
   Enter the account number: 1
   {'action': 'select_order_account', 'message': 'Order account selected: 0290621'}
   ```

## 6. Check System Prerequisites

1. Select `10` to check if system can start:
   ```text
   > 10
   === System Prerequisites ===
   User logged in: ✓                   # Logged in
   Item registered: ✓                  # Product registered
   Order account selected: ✓           # Account selected
   Trading conditions defined: ✓       # Trading conditions defined
   ===========================
   ```

## 7. Start Automated Trading System

1. Select `10` again to start the system:
   ```text
   > 10
   === Starting All Trading System Components ===
   
   === System Startup Results ===
   Overall Status: ✓ Success
   Gateway: ✓ Running                  # DLL Gateway running
   Strategy: ✓ Running                 # Strategy process running  
   Order Executor: ✓ Running           # Order executor process running
   =============================
   
   Strategy process started. Waiting for market data...
   Order executor gateway process started. Waiting for trading signals...
   ```

🎉 **Congratulations! Your automated trading system is now running**

The system will now:
- Monitor real-time quotes for Mini Taiwan Index (MXFF5)
- Automatically buy 1 contract when price breaks above 22000 points
- Take profit target: 22120 points (120 points profit)
- Stop loss target: 21970 points (30 points loss)

## 8. Monitor Trading Status

Check positions:
```text
> 8
Account: 0290621
Enter product id (leave blank for all): [Leave blank to view all positions]
```

## 9. Stop Trading System

### Normal Logout
```text
> 2  # Logout from Taiwan Unified Futures system
Domestic futures quote disconnected
Domestic futures account disconnected
Login status: Logout successful!

> 0  # Exit program
Exiting the program
```

---

## 💡 Trading Parameters Explanation

| Parameter | Example Value | Description |
|-----------|---------------|-------------|
| **Target Price** | 22000 | Support/resistance level price, used as strategy trigger baseline |
| **Turning Point** | 30 | Point difference from trigger to actual entry (prevents false breakouts) |
| **Quantity** | 1 | Trading quantity (recommended to start with 1 contract for beginners) |
| **Take Profit** | 120 | Take profit points (automatic profit taking) |
| **Stop Loss** | 30 | Stop loss points (risk control mechanism) |
| **Following** | y | **Dynamic Tracking**: System adjusts entry points based on price movements |

### Following Dynamic Tracking Detailed Explanation

**Following = Yes Operating Mechanism**:
- **Buy Strategy**: If price continues to fall to lower levels, system automatically adjusts support level downward, waiting for better entry timing
- **Sell Strategy**: If price continues to rise to higher levels, system automatically adjusts resistance level upward, waiting for better entry timing
- **Advantage**: Avoids entering at wrong timing, improves strategy success rate
- **Risk**: May miss quick reversal opportunities

**Example Explanation** (Buy, Following=Yes):
1. Set support level 22000, turning point 30
2. Price drops to 21980 → Strategy triggered, waiting for rebound to 22010 to enter
3. Price continues to drop to 21950 → System adjusts support level to 21950, new entry point 21980
4. Price rebounds to 21985 → System sends buy signal

## ⚠️ Risk Warning

- **Futures trading carries high risk**, may result in total capital loss
- **Beginners should start with small positions**, increase after familiarizing with the system
- **Must set stop loss**, control maximum loss
- **Monitor system operation status**, stop immediately if abnormalities found

## 🚀 Strategy Expansion

The system currently only provides **Support/Resistance Strategy**. If you need:
- **Other technical indicator strategies** (MA, RSI, MACD, etc.)
- **Quantitative strategies** (statistical arbitrage, pairs trading, etc.)  
- **Multi-strategy combination management**

Please refer to **[Strategy Expansion Development Guide](../guides/STRATEGY_EXPANSION_GUIDE.md)** to learn how to expand the system.

---

*Wishing you successful trading! Remember: Never invest more than you can afford to lose.*