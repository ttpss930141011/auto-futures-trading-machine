# ⚙️ Configuration Guide

> *Learn how to configure the Auto Futures Trading Machine*

## 🔍 Overview

All configuration settings live in the environment file `.env` at the project root. The application reads these values at startup.

> **Note**: This project uses the proprietary PFCF Python DLL API. Apply to Taiwan Unified Futures (PFCF) for their Python DLL API at https://www.pfcf.com.tw/software/detail/2709 and place the DLL files into `src/infrastructure/pfcf_client/dll`.

## 📄 .env File Settings

```env
# PFCF API endpoints (required)
DEALER_TEST_URL=your_test_url_here
DEALER_PROD_URL=your_prod_url_here

# Trading mode (optional): paper trading when true
TEST_MODE=true

# ZeroMQ configuration (optional)
ZMQ_HOST=127.0.0.1
ZMQ_TICK_PORT=5555
ZMQ_SIGNAL_PORT=5556

# DLL Gateway configuration (optional)
DLL_GATEWAY_HOST=127.0.0.1
DLL_GATEWAY_PORT=5557
DLL_GATEWAY_REQUEST_TIMEOUT_MS=5000
DLL_GATEWAY_RETRY_COUNT=3

# Logging level (optional)
LOG_LEVEL=INFO

# Paths (optional)
LOG_DIR=logs
DATA_DIR=data
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