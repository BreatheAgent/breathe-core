"""
Breathe Core — Spending Guard
Enforces daily spending limits to prevent runaway losses.
No transaction above the daily limit passes without explicit human approval.
"""

import json
import os
from datetime import datetime, timezone, timedelta
from config.settings import settings
from utils.logger import get_logger, log_with_data

logger = get_logger("spending_guard")

SPEND_LOG_FILE = "data/daily_spend.json"


class SpendingGuard:
    """Tracks and enforces daily USDC spending limits."""

    def __init__(self):
        self.daily_limit = settings.DAILY_SPEND_LIMIT
        self._ensure_data_dir()
        self.spend_log = self._load_spend_log()
        logger.info(f"SpendingGuard initialized — daily limit: ${self.daily_limit}")

    def _ensure_data_dir(self):
        os.makedirs("data", exist_ok=True)

    def _load_spend_log(self) -> dict:
        """Load spending log from disk."""
        if os.path.exists(SPEND_LOG_FILE):
            with open(SPEND_LOG_FILE, "r") as f:
                return json.load(f)
        return {"date": self._today(), "total_spent": 0.0, "transactions": []}

    def _save_spend_log(self):
        """Persist spending log to disk."""
        with open(SPEND_LOG_FILE, "w") as f:
            json.dump(self.spend_log, f, indent=2)

    def _today(self) -> str:
        return datetime.now(timezone.utc).strftime("%Y-%m-%d")

    def _reset_if_new_day(self):
        """Reset daily counter if a new UTC day has started."""
        if self.spend_log["date"] != self._today():
            logger.info("📅 New day — resetting daily spend counter")
            self.spend_log = {
                "date": self._today(),
                "total_spent": 0.0,
                "transactions": [],
            }
            self._save_spend_log()

    def get_remaining_budget(self) -> float:
        """How much can still be spent today without approval."""
        self._reset_if_new_day()
        return max(0, self.daily_limit - self.spend_log["total_spent"])

    def can_spend(self, amount: float) -> bool:
        """Check if this amount is within the daily limit."""
        self._reset_if_new_day()
        remaining = self.get_remaining_budget()
        allowed = amount <= remaining

        if not allowed:
            log_with_data(logger, "warning", "Spending limit would be exceeded",
                         amount=amount, remaining=remaining, limit=self.daily_limit)

        return allowed

    def record_spend(self, amount: float, protocol: str, action: str, tx_hash: str = ""):
        """Record a spend event."""
        self._reset_if_new_day()
        self.spend_log["total_spent"] += amount
        self.spend_log["transactions"].append({
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "amount": amount,
            "protocol": protocol,
            "action": action,
            "tx_hash": tx_hash,
        })
        self._save_spend_log()

        log_with_data(logger, "info", "Spend recorded",
                     amount=amount, protocol=protocol, daily_total=self.spend_log["total_spent"])

    def request_human_approval(self, amount: float, reason: str) -> bool:
        """
        Request human approval for a transaction exceeding the daily limit.
        In production, this would integrate with Telegram/Discord bot.
        For now, logs the request and returns False (safe default).
        """
        logger.warning(
            f"🚨 HUMAN APPROVAL REQUIRED: ${amount:.2f} — {reason}\n"
            f"   Daily limit: ${self.daily_limit} | Already spent: ${self.spend_log['total_spent']:.2f}"
        )
        # In production: send notification, wait for response
        # For now, deny and log
        return False

    def get_daily_summary(self) -> dict:
        """Return today's spending summary."""
        self._reset_if_new_day()
        return {
            "date": self.spend_log["date"],
            "total_spent": self.spend_log["total_spent"],
            "remaining": self.get_remaining_budget(),
            "limit": self.daily_limit,
            "transaction_count": len(self.spend_log["transactions"]),
        }
