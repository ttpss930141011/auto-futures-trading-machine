# ⚙️ Configuration Guide

> *Learn how to configure the Auto Futures Trading Machine*

## 🔍 Overview

All configuration settings live in the environment file `.env` at the project root. The application reads these values at startup.

## 📄 .env File Settings

```env
# Exchange API credentials (required)
EXCHANGE_API_KEY=your_api_key_here
EXCHANGE_API_SECRET=your_api_secret_here
EXCHANGE_ACCOUNT_ID=your_account_id

# Trading mode (optional)
# true  = paper trading (no real orders)
# false = live trading
TEST_MODE=true

# ZeroMQ socket addresses (optional)
# Uncomment to override defaults
# ZMQ_TICK_PUB_ADDRESS=tcp://*:5555
# ZMQ_SIGNAL_PULL_ADDRESS=tcp://*:5556
# ZMQ_ORDER_REQ_ADDRESS=tcp://*:5557

# Logging level (optional)
# Options: DEBUG, INFO, WARNING, ERROR
LOG_LEVEL=INFO

# Paths (optional)
# LOG_DIR=logs
# DATA_DIR=data
```

## 🔧 Customizing Settings

- To change the logging level, edit `LOG_LEVEL`.
- To change where logs and temporary files are stored, set `LOG_DIR` and `DATA_DIR`.
- To run against a different exchange or endpoint, modify the appropriate DLL Gateway or API client settings in `src/app/cli_pfcf/config.py`.

## ✅ Verification

After editing `.env`, restart the application:
```bash
python app.py
```
If any required setting is missing, you'll see a clear error indicating which variable is not set.

---

*Keep your credentials secure and never commit `.env` to source control.* 