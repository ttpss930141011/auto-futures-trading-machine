# 🚀 Auto Futures Trading Machine

<p align="center">
<img src="./static/logo/logo-transparent-png.png" width="200" height="200" align="">
</p>

> **A Journey Through Event-Driven Trading System Architecture**  
> From monolithic beginnings to a distributed, production-ready futures trading platform

## 📖 Table of Contents

### 🎯 Getting Started
- [**Quick Start Guide**](docs/getting-started/QUICK_START.md) - Get up and running in 5 minutes
- [**Installation Guide**](docs/getting-started/INSTALLATION.md) - Detailed setup instructions
- [**First Trade Tutorial**](docs/getting-started/FIRST_TRADE.md) - Your first automated trade

### 🏗️ Architecture & Design
- [**Architecture Overview**](docs/architecture/ARCHITECTURE_OVERVIEW.md) - Visual system overview
- [**The Refactoring Story**](docs/architecture/REFACTORING_STORY.md) - How we transformed from chaos to clarity
- [**Event-Driven Design**](docs/architecture/EVENT_DRIVEN_DESIGN.md) - Why events power our system
- [**Clean Architecture Implementation**](docs/architecture/CLEAN_ARCHITECTURE.md) - SOLID principles in action

### 🔧 Technical Deep Dives
- [**Why ZeroMQ?**](docs/technical/WHY_ZEROMQ.md) - Message patterns and performance
- [**DLL Gateway Architecture**](docs/technical/DLL_GATEWAY_ARCHITECTURE.md) - Solving the security challenge
- [**High-Frequency Trading Concepts**](docs/technical/HFT_CONCEPTS.md) - What we borrowed from HFT
- [**Process Communication**](docs/technical/PROCESS_COMMUNICATION.md) - IPC patterns explained

### 📚 Developer Stories
- [**Migration Journey**](docs/stories/MIGRATION_JOURNEY.md) - From monolith to microservices
- [**Design Decisions**](docs/stories/DESIGN_DECISIONS.md) - Why we made the choices we did
- [**Lessons Learned**](docs/stories/LESSONS_LEARNED.md) - What worked and what didn't

### 🛠️ Implementation Guides
- [**Component Development**](docs/guides/COMPONENT_DEVELOPMENT.md) - Building new components
- [**Testing Strategies**](docs/guides/TESTING_STRATEGIES.md) - How we ensure reliability
- [**Performance Tuning**](docs/guides/PERFORMANCE_TUNING.md) - Optimizing for speed

### 📊 Trading Concepts
- [**Support & Resistance Strategy**](docs/trading/SUPPORT_RESISTANCE.md) - Our core algorithm
- [**Risk Management**](docs/trading/RISK_MANAGEMENT.md) - Protecting capital
- [**Market Data Processing**](docs/trading/MARKET_DATA.md) - From ticks to decisions

### 🗺️ Project Evolution
- [**Roadmap**](docs/ROADMAP.md) - Past, present, and future
- [**Architecture Decision Records**](docs/decisions/) - Key architectural choices
- [**Change Log**](CHANGELOG.md) - Version history

### 📋 References
- [**API Documentation**](docs/api/README.md) - Component APIs
- [**Configuration Guide**](docs/CONFIG_GUIDE.md) - System configuration
- [**Troubleshooting**](docs/TROUBLESHOOTING.md) - Common issues and solutions
- [**Contributing**](CONTRIBUTING.md) - How to contribute

---

## 🎬 The Story Begins...

Picture this: You're a developer tasked with building an automated futures trading system. You start simple - a single Python script that connects to an exchange, watches prices, and places orders. It works! But as requirements grow, so does the complexity...

**This is our story** - a journey from a monolithic application plagued by tight coupling and security concerns to a distributed, event-driven architecture that borrows concepts from high-frequency trading systems while remaining accessible to Python developers.

## 🏆 What Makes This Special?

### 🔐 **Security First**
We eliminated plaintext credential storage and centralized all exchange API access through a secure gateway - a pattern inspired by institutional trading systems.

### ⚡ **Event-Driven Architecture**
Every market tick, every trading signal, every order - they're all events flowing through our system via ZeroMQ, enabling true parallelism and bypassing Python's GIL.

### 🧩 **Clean Architecture**
SOLID principles aren't just theory here. Our recent refactoring (see [The Refactoring Story](docs/architecture/REFACTORING_STORY.md)) demonstrates how proper separation of concerns transforms maintainability.

### 📊 **Production Ready**
From comprehensive test coverage to graceful error handling, this isn't just a prototype - it's a system designed for real trading.

## 🚀 Quick Start

```bash
# Clone the repository
git clone https://github.com/your-repo/futures-trading-machine.git

# Install dependencies
poetry install

# Configure your exchange credentials
cp .env.example .env
# Edit .env with your credentials

# Run the system
python app.py
```

Follow our [Quick Start Guide](docs/getting-started/QUICK_START.md) for detailed instructions.

## 🏛️ System Architecture at a Glance

```
┌─────────────────────────────────────────────────────────────────┐
│                      Main Process (app.py)                      │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐    │
│  │     CLI     │  │ DLL Gateway │  │  Market Data        │    │
│  │  Interface  │  │   Server    │  │   Publisher         │    │
│  │             │  │  Port 5557  │  │   Port 5555         │    │
│  └─────────────┘  └─────────────┘  └─────────────────────┘    │
└─────────────────────────────────────────────────────────────────┘
         │                  ▲                    │
         │                  │ ZMQ REQ/REP       │ ZMQ PUB
         │                  │ (Orders)          │ (Market Data)
         │                  │                    ▼
         │          ┌───────┴────────┐   ┌─────────────────┐
         │          │ Order Executor │   │    Strategy     │
         │          │    Process     │   │    Process      │
         │          │                │   │                 │
         │          │ ┌────────────┐ │   │ ┌─────────────┐│
         │          │ │   Signal   │ │   │ │    Tick     ││
         │          │ │  Receiver  │◄├───┤►│ Subscriber  ││
         └──────────┤►│            │ │   │ └─────────────┘│
                    │ └────────────┘ │   │                 │
                    │                │   │  ┌────────────┐ │
                    │ ┌────────────┐ │   │  │ Support/   │ │
                    │ │  Gateway   │ │   │  │ Resistance │ │
                    │ │   Client   │ │   │  │ Strategy   │ │
                    │ └────────────┘ │   │  └────────────┘ │
                    └────────────────┘   └─────────────────┘
                                               ZMQ PUSH
                                            (Trading Signals)
```

## 📈 Performance Metrics

- **Tick Processing**: < 1ms latency (ZeroMQ + msgpack serialization)
- **Signal Generation**: < 5ms from tick to trading decision
- **Order Execution**: < 10ms round-trip to exchange
- **Test Coverage**: 95%+ across critical components

## 🎓 Learning Path

Whether you're interested in:
- **Trading Systems**: Start with [Support & Resistance Strategy](docs/trading/SUPPORT_RESISTANCE.md)
- **Software Architecture**: Begin with [Clean Architecture Implementation](docs/architecture/CLEAN_ARCHITECTURE.md)
- **Distributed Systems**: Explore [Why ZeroMQ?](docs/technical/WHY_ZEROMQ.md)
- **Real-world Refactoring**: Read [The Refactoring Story](docs/architecture/REFACTORING_STORY.md)

This documentation serves as both a **technical reference** and a **learning resource** for building production-grade trading systems.

## 🤝 Contributing

We welcome contributions! Whether it's:
- 🐛 Bug fixes
- ✨ New features
- 📚 Documentation improvements
- 🧪 Test coverage

Please read our [Contributing Guide](CONTRIBUTING.md) to get started.

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

This project stands on the shoulders of giants:
- The **ZeroMQ** community for incredible messaging patterns
- **Clean Architecture** principles by Robert C. Martin
- High-frequency trading system designs that inspired our architecture
- All contributors who've helped shape this journey

---

*"In trading, as in software, the best systems are those that are simple to understand, yet sophisticated in their execution."*

**Ready to dive in?** Start with our [Quick Start Guide](docs/getting-started/QUICK_START.md) →
