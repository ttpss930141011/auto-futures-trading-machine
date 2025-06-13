# 🧪 Backtesting Guide

> *Test your trading strategy against historical market data*

## 📂 Historical Data

- Place CSV or JSON files in the `data/historical/` directory.
- Files should contain timestamped `TickEvent` data:
  ```csv
datetime,instrument,bid_price,ask_price,bid_volume,ask_volume
2024-06-01T09:00:00Z,TSLA,250.00,250.10,100,100
...
```

## ⚙️ Running Backtests

1. Activate your environment:
   ```bash
   source .venv/bin/activate  # or .\.venv\Scripts\activate
   ```
2. Run the backtest script with the path to your data:
   ```bash
   python scripts/run_backtest.py --data data/historical/tsla_ticks.csv \
       --strategy SupportResistanceStrategy \
       --output results/tsla_backtest_report.json
   ```

## 📊 Results

- The script generates a report with:
  - Total trades executed
  - Win/loss ratio
  - Profit & loss summary
  - Drawdown analysis
- Open `results/tsla_backtest_report.json` to view details or load into a notebook.

## 🔄 Iterating on Strategy

- Adjust strategy parameters (`support`, `resistance`, `quantity`) via CLI or config file.
- Re-run backtests until results meet your requirements.

---

*Use backtesting to gain confidence before going live.* 