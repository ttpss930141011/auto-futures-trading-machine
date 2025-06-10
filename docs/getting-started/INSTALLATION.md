# 🛠️ Installation Guide

> *Detailed setup instructions for the Auto Futures Trading Machine*

## 📋 Prerequisites

- Python 3.8 or higher
- Git installed on your system
- (Optional) Poetry for dependency management
- Exchange API credentials (API key, secret, account ID)

## 🔧 Step 1: Clone the Repository

```bash
# Using HTTPS
git clone https://github.com/ttpss930141011/futures-trading-machine.git
cd futures-trading-machine
```

## 🐍 Step 2: Create a Virtual Environment

```bash
# Using venv (standard)
python -m venv .venv
# Activate the environment
# Windows:
.\.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate
```

## 📦 Step 3: Install Dependencies

### Option A: Poetry (recommended)

```bash
# Install Poetry if not installed
pip install poetry

# Install project dependencies
toetry install

# To start a shell with the virtual env
toetry shell
```

### Option B: pip + requirements.txt

```bash
pip install -r requirements.txt
```

## 🔐 Step 4: Configure Environment Variables

> **🔔 Prerequisite: Obtain PFCF Python DLL API**  
> Apply to Taiwan Unified Futures (PFCF) for their proprietary Python DLL API at https://www.pfcf.com.tw/software/detail/2709 and place the DLL files into `src/infrastructure/pfcf_client/dll`.

1. Create or copy the environment file:
   ```bash
   cp .env.example .env  # macOS/Linux
   copy .env.example .env  # Windows
   ```
2. Open `.env` in a text editor and set the essential environment variables:
   ```env
   # PFCF API endpoints (required)
   DEALER_TEST_URL=your_test_url_here
   DEALER_PROD_URL=your_prod_url_here

   # Optional: Trading mode (paper trading)
   TEST_MODE=true
   ```
Refer to the [Configuration Guide](../../CONFIG_GUIDE.md) for full environment variable options.

## 🚀 Step 5: Verify the Setup

```bash
# Start the application
default> python app.py
```
You should see the CLI menu appear without errors.

## 📖 Next Steps

- ✅ Follow the [Quick Start Guide](QUICK_START.md) to run your first trade
- 📚 Review the [First Trade Tutorial](FIRST_TRADE.md)
- 🔍 Explore the [Configuration Guide](../../CONFIG_GUIDE.md) for advanced options

---

*Happy trading!*