# 🌬️ Breathe Core — Autonomous AI Capital Growth Engine

<p align="center">
  <strong>"Not an assistant. An autonomous economic entity."</strong>
</p>

---

## 🧬 The 1K → Growth Experiment

**Starting capital:** $1,000 USDC  
**Goal:** Autonomous capital growth over 30 days  
**Risk profile:** Configurable (conservative / moderate / aggressive)

Breathe is an AI-powered autonomous agent that manages a treasury across multiple chains and strategies. Give it capital, define your risk tolerance, and let it work.

## 🏗️ Architecture

Breathe operates as a **multi-agent system**:

| Agent | Role |
|-------|------|
| **CEO Agent** | Top-level capital allocator & decision maker |
| **Risk Guardian** | Validates every trade, enforces limits, veto power |
| **Yield Agent** | DeFi strategy optimizer (via breathe-defi) |
| **Trading Engine** | Perps + Polymarket (via breathe-trading) |
| **Meme Sniper** | Solana meme token trading (via breathe-memes) |

### Capital Allocation (Moderate Risk)

| Strategy | Allocation | Chain |
|----------|-----------|-------|
| DeFi Yield | 40% | Base |
| Leveraged Perps | 25% | Base |
| Polymarket | 20% | Polygon |
| Meme Tokens | 15% | Solana |

## 🚀 Quick Start

```bash
# 1. Clone
git clone https://github.com/BreatheAgent/breathe-core.git
cd breathe-core

# 2. Install
pip install -r requirements.txt

# 3. Configure
cp .env.example .env
# Edit .env with your keys

# 4. Validate
python main.py --validate-config

# 5. Dry Run (simulated, no real transactions)
python main.py --mode treasury --dry-run

# 6. Go Live
python main.py --mode treasury
```

## 🛡️ Safety Architecture

| Control | Detail |
|---------|--------|
| Daily spend limit | $100 without human approval |
| Per-trade limit | Max 10% of treasury |
| Meme trade limit | Max 2% of treasury |
| Max leverage | 3x on perps |
| Stop-loss | Always active |
| Kill-switch | `python main.py --mode kill` |
| Drawdown halt | Auto-kill at 15% drawdown |
| Tx logging | Every transaction logged |

## 📊 Commands

```bash
python main.py --mode treasury      # Start autonomous growth
python main.py --mode report        # Generate PNL report
python main.py --mode status        # Show portfolio status
python main.py --mode kill          # Emergency shutdown
python main.py --mode resume        # Resume operations
python main.py --validate-config    # Check configuration
```

## 🐳 Docker

```bash
docker-compose up -d
```

## 📂 Ecosystem Repos

| Repo | Purpose |
|------|---------|
| [breathe-core](https://github.com/BreatheAgent/breathe-core) | Central brain & orchestrator |
| [breathe-defi](https://github.com/BreatheAgent/breathe-defi) | DeFi yield farming (Base) |
| [breathe-trading](https://github.com/BreatheAgent/breathe-trading) | Perps + Polymarket |
| [breathe-memes](https://github.com/BreatheAgent/breathe-memes) | Solana meme token sniping |

## ⚠️ Disclaimer

This is an experimental autonomous trading system. It interacts with real smart contracts and real capital. Use at your own risk. Always start with dry-run mode and small amounts.

---

<sub>Built by [BreatheAgent](https://github.com/BreatheAgent) · Powered by Virtuals Protocol · Running on Base, Polygon & Solana</sub>
