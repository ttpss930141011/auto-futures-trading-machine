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

1. Copy the example environment file:
   ```bash
   cp .env.example .env
   ```
2. Open `.env` in a text editor and set your credentials:
   ```env
   EXCHANGE_API_KEY=your_api_key_here
   EXCHANGE_API_SECRET=your_api_secret_here
   EXCHANGE_ACCOUNT_ID=your_account_id
   TEST_MODE=true  # Optional: use paper trading
   ```

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