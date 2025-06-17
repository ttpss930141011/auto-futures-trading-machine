# 📚 Documentation Directory

## 🎯 Main Documents (Project Root)

### 🏛️ System Architecture
- **[ARCHITECTURE.md](../ARCHITECTURE.md)** - Complete system overview with visual diagrams
- **[CLAUDE.md](../CLAUDE.md)** - Developer instructions and essential commands

### 📖 Quick Start
- **[README.md](../README.md)** - Project overview and learning paths

---

## 📁 docs/ Folder Structure

### 🏗️ architecture/
Detailed documentation related to system architecture

- **[DETAILED_FLOW_DIAGRAMS.md](architecture/DETAILED_FLOW_DIAGRAMS.md)** - Detailed flow diagrams and sequence diagrams
- **[CLASS_DESIGN_GUIDE.md](architecture/CLASS_DESIGN_GUIDE.md)** - Class design guide and SOLID principles

### 📋 guides/
User guides and operation manuals

- **[ALLINONE_CONTROLLER_GUIDE.md](guides/ALLINONE_CONTROLLER_GUIDE.md)** - AllInOneController startup flow detailed explanation

### 🔧 technical/
Technical deep-dive analysis

- **[WHY_ZEROMQ.md](technical/WHY_ZEROMQ.md)** - ZeroMQ selection rationale and messaging patterns
- **[HFT_CONCEPTS.md](technical/HFT_CONCEPTS.md)** - High-frequency trading concepts application
- **[PROCESS_COMMUNICATION.md](technical/PROCESS_COMMUNICATION.md)** - Inter-process communication patterns

### 🚀 getting-started/
Beginner tutorials

- **[INSTALLATION.md](getting-started/INSTALLATION.md)** - Detailed installation guide
- **[QUICK_START.md](getting-started/QUICK_START.md)** - 5-minute quick start
- **[FIRST_TRADE.md](getting-started/FIRST_TRADE.md)** - First automated trade tutorial

### 📊 guides/
Advanced usage guides

- **[BACKTESTING.md](guides/BACKTESTING.md)** - Backtesting system guide
- **[MONITORING.md](guides/MONITORING.md)** - System monitoring configuration

### 📚 stories/
Development stories and decision processes

- **[DESIGN_DECISIONS.md](stories/DESIGN_DECISIONS.md)** - Important design decisions record
- **[LESSONS_LEARNED.md](stories/LESSONS_LEARNED.md)** - Development process experience summary

### 🗺️ decisions/
Architecture Decision Records (ADR)

- **[001-use-zeromq-for-ipc.md](decisions/001-use-zeromq-for-ipc.md)** - Decision to use ZeroMQ
- **[004-dll-gateway-centralization.md](decisions/004-dll-gateway-centralization.md)** - DLL Gateway centralization
- Other ADR documents...

### 🔧 api/
API Documentation

- **[README.md](api/README.md)** - Component API overview

### 🗃️ archived/
Historical document archive

- **Deprecated or outdated documents** - Kept for historical reference, should not be used for current development

---

## 🎓 Recommended Learning Sequence

### 🔰 New Developers
1. [README.md](../README.md) - Understand project overview
2. [ARCHITECTURE.md](../ARCHITECTURE.md) - Understand system architecture
3. [getting-started/INSTALLATION.md](getting-started/INSTALLATION.md) - Environment setup
4. [getting-started/QUICK_START.md](getting-started/QUICK_START.md) - Quick start

### 👨‍💻 Experienced Developers
1. [ARCHITECTURE.md](../ARCHITECTURE.md) - System overview
2. [architecture/CLASS_DESIGN_GUIDE.md](architecture/CLASS_DESIGN_GUIDE.md) - Design patterns
3. [architecture/DETAILED_FLOW_DIAGRAMS.md](architecture/DETAILED_FLOW_DIAGRAMS.md) - Detailed flow
4. [guides/ALLINONE_CONTROLLER_GUIDE.md](guides/ALLINONE_CONTROLLER_GUIDE.md) - Startup mechanism

### 🏗️ Architecture Designers
1. [decisions/](decisions/) - Review all ADRs
2. [technical/WHY_ZEROMQ.md](technical/WHY_ZEROMQ.md) - Technology selection
3. [stories/DESIGN_DECISIONS.md](stories/DESIGN_DECISIONS.md) - Design philosophy
4. [stories/LESSONS_LEARNED.md](stories/LESSONS_LEARNED.md) - Experience summary

---

## ⚠️ Important Reminders

- **Archived Documents**: Documents in the `archived/` folder are outdated, please do not reference
- **Document Synchronization**: Please update related documents when modifying code
- **Diagram Format**: All diagrams use Mermaid format for easy maintenance and version control
- **Hyperlink Validation**: Regularly check if hyperlinks between documents are valid

---

*Last Updated: December 2024*