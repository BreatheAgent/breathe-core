"""
Breathe Core — Portfolio Manager
Tracks the overall portfolio state across all strategies and chains.
"""

import json
import os
from datetime import datetime, timezone
from config.settings import settings
from utils.logger import get_logger

logger = get_logger("portfolio")

PORTFOLIO_STATE_FILE = "data/portfolio_state.json"


class PortfolioManager:
    """Manages the aggregate portfolio state across all strategies."""

    def __init__(self):
        os.makedirs("data", exist_ok=True)
        self.state = self._load_state()
        logger.info("📊 Portfolio Manager initialized")

    def _load_state(self) -> dict:
        if os.path.exists(PORTFOLIO_STATE_FILE):
            with open(PORTFOLIO_STATE_FILE, "r") as f:
                return json.load(f)
        return self._default_state()

    def _default_state(self) -> dict:
        return {
            "initial_capital": 1000.0,
            "total_value_usd": 1000.0,
            "peak_value": 1000.0,
            "positions": {
                "idle_usdc": 1000.0,
                "defi": 0.0,
                "perps": 0.0,
                "polymarket": 0.0,
                "memes": 0.0,
            },
            "allocations": {
                "defi": 0.0,
                "perps": 0.0,
                "polymarket": 0.0,
                "memes": 0.0,
            },
            "last_updated": datetime.now(timezone.utc).isoformat(),
        }

    def _save_state(self):
        with open(PORTFOLIO_STATE_FILE, "w") as f:
            json.dump(self.state, f, indent=2)

    def get_state(self) -> dict:
        """Get current portfolio state."""
        self._recalculate_allocations()
        return self.state.copy()

    def update_position(self, strategy: str, new_value: float):
        """Update the value of a specific strategy position."""
        if strategy in self.state["positions"]:
            old_value = self.state["positions"][strategy]
            self.state["positions"][strategy] = new_value

            # Recalculate total
            self.state["total_value_usd"] = sum(self.state["positions"].values())

            # Track peak
            if self.state["total_value_usd"] > self.state.get("peak_value", 0):
                self.state["peak_value"] = self.state["total_value_usd"]

            self.state["last_updated"] = datetime.now(timezone.utc).isoformat()
            self._recalculate_allocations()
            self._save_state()

            logger.info(f"📊 Updated {strategy}: ${old_value:.2f} → ${new_value:.2f}")
        else:
            logger.warning(f"Unknown strategy: {strategy}")

    def deploy_capital(self, strategy: str, amount: float) -> bool:
        """Move USDC from idle to a strategy."""
        if amount > self.state["positions"]["idle_usdc"]:
            logger.warning(f"Insufficient idle USDC: ${self.state['positions']['idle_usdc']:.2f} < ${amount:.2f}")
            return False

        self.state["positions"]["idle_usdc"] -= amount
        self.state["positions"][strategy] = self.state["positions"].get(strategy, 0) + amount
        self.state["last_updated"] = datetime.now(timezone.utc).isoformat()
        self._recalculate_allocations()
        self._save_state()

        logger.info(f"💰 Deployed ${amount:.2f} to {strategy}")
        return True

    def withdraw_to_idle(self, strategy: str, amount: float) -> bool:
        """Move USDC from a strategy back to idle."""
        current = self.state["positions"].get(strategy, 0)
        if amount > current:
            logger.warning(f"Insufficient {strategy} balance: ${current:.2f} < ${amount:.2f}")
            return False

        self.state["positions"][strategy] -= amount
        self.state["positions"]["idle_usdc"] += amount
        self.state["last_updated"] = datetime.now(timezone.utc).isoformat()
        self._recalculate_allocations()
        self._save_state()

        logger.info(f"💰 Withdrew ${amount:.2f} from {strategy} to idle")
        return True

    def _recalculate_allocations(self):
        """Recalculate allocation percentages."""
        total = self.state["total_value_usd"]
        if total <= 0:
            return

        for strategy in ["defi", "perps", "polymarket", "memes"]:
            value = self.state["positions"].get(strategy, 0)
            self.state["allocations"][strategy] = value / total

    def get_pnl(self) -> dict:
        """Calculate overall PNL."""
        initial = self.state["initial_capital"]
        current = self.state["total_value_usd"]
        pnl = current - initial
        roi = pnl / initial if initial > 0 else 0

        return {
            "initial_capital": initial,
            "current_value": current,
            "pnl": pnl,
            "roi": roi,
            "peak_value": self.state.get("peak_value", initial),
        }
