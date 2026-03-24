"""
Breathe Core — Transaction Logger
Append-only audit trail for every on-chain transaction.
Every USDC moved, every position opened, every swap — logged here.
"""

import json
import os
from datetime import datetime, timezone
from utils.logger import get_logger

logger = get_logger("tx_logger")

TX_LOG_FILE = "data/transactions.json"


class TransactionLogger:
    """Immutable transaction audit trail."""

    def __init__(self):
        os.makedirs("data", exist_ok=True)
        self._ensure_log()

    def _ensure_log(self):
        if not os.path.exists(TX_LOG_FILE):
            with open(TX_LOG_FILE, "w") as f:
                json.dump([], f)

    def log_transaction(
        self,
        protocol: str,
        action: str,
        amount_usdc: float,
        tx_hash: str,
        chain: str = "base",
        details: dict = None,
    ) -> dict:
        """Log a transaction to the audit trail."""
        entry = {
            "id": self._next_id(),
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "chain": chain,
            "protocol": protocol,
            "action": action,
            "amount_usdc": amount_usdc,
            "tx_hash": tx_hash,
            "details": details or {},
        }

        # Append to log
        log = self._read_log()
        log.append(entry)
        with open(TX_LOG_FILE, "w") as f:
            json.dump(log, f, indent=2)

        logger.info(
            f"📝 TX #{entry['id']} | {chain} | {protocol} | {action} | "
            f"${amount_usdc:.2f} | {tx_hash[:16]}..."
        )
        return entry

    def get_all_transactions(self) -> list:
        return self._read_log()

    def get_transactions_by_protocol(self, protocol: str) -> list:
        return [tx for tx in self._read_log() if tx["protocol"] == protocol]

    def get_transactions_by_chain(self, chain: str) -> list:
        return [tx for tx in self._read_log() if tx["chain"] == chain]

    def get_today_transactions(self) -> list:
        today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        return [tx for tx in self._read_log() if tx["timestamp"].startswith(today)]

    def get_total_volume(self) -> float:
        return sum(tx["amount_usdc"] for tx in self._read_log())

    def get_summary(self) -> dict:
        txs = self._read_log()
        today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        today_txs = [tx for tx in txs if tx["timestamp"].startswith(today)]

        return {
            "total_transactions": len(txs),
            "total_volume_usdc": sum(tx["amount_usdc"] for tx in txs),
            "today_transactions": len(today_txs),
            "today_volume_usdc": sum(tx["amount_usdc"] for tx in today_txs),
            "protocols_used": list(set(tx["protocol"] for tx in txs)),
            "chains_used": list(set(tx["chain"] for tx in txs)),
        }

    def _read_log(self) -> list:
        with open(TX_LOG_FILE, "r") as f:
            return json.load(f)

    def _next_id(self) -> int:
        log = self._read_log()
        return len(log) + 1
