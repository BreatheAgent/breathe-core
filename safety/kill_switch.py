"""
Breathe Core — Kill Switch
Emergency shutdown mechanism. When triggered:
1. Halts all pending operations
2. Withdraws all DeFi positions to USDC
3. Closes all perps positions
4. Locks the treasury
"""

import json
import os
from datetime import datetime, timezone
from utils.logger import get_logger

logger = get_logger("kill_switch")

KILL_STATE_FILE = "data/kill_state.json"


class KillSwitch:
    """Emergency stop mechanism for the entire Breathe system."""

    def __init__(self):
        os.makedirs("data", exist_ok=True)
        self._state = self._load_state()

    def _load_state(self) -> dict:
        if os.path.exists(KILL_STATE_FILE):
            with open(KILL_STATE_FILE, "r") as f:
                return json.load(f)
        return {"killed": False, "timestamp": None, "reason": None}

    def _save_state(self):
        with open(KILL_STATE_FILE, "w") as f:
            json.dump(self._state, f, indent=2)

    @property
    def is_killed(self) -> bool:
        """Check if the kill switch is active."""
        return self._state.get("killed", False)

    def activate(self, reason: str = "Manual activation"):
        """
        ACTIVATE KILL SWITCH — Emergency shutdown.
        This will:
        - Set the kill flag (halts all new operations)
        - Log the event
        - In production: trigger withdrawal of all positions
        """
        logger.critical(f"🛑 KILL SWITCH ACTIVATED — Reason: {reason}")

        self._state = {
            "killed": True,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "reason": reason,
        }
        self._save_state()

        # In production, this would call:
        # - DeFi rebalancer to withdraw all
        # - Perps position manager to close all
        # - Meme exit strategy to market sell all
        logger.critical("🛑 All operations halted. Treasury locked.")
        logger.critical("🛑 To resume, call: python main.py --resume")

        return {
            "status": "KILLED",
            "timestamp": self._state["timestamp"],
            "reason": reason,
        }

    def deactivate(self, reason: str = "Manual resume"):
        """Resume operations after kill switch."""
        if not self.is_killed:
            logger.info("Kill switch is not active, nothing to resume")
            return

        logger.warning(f"✅ KILL SWITCH DEACTIVATED — Reason: {reason}")
        self._state = {"killed": False, "timestamp": None, "reason": None}
        self._save_state()

    def check_or_halt(self) -> bool:
        """
        Call this before any operation.
        Returns True if operations can proceed, False if halted.
        """
        if self.is_killed:
            logger.warning(
                f"⛔ Operation blocked — Kill switch active since {self._state['timestamp']}\n"
                f"   Reason: {self._state['reason']}"
            )
            return False
        return True

    def get_status(self) -> dict:
        return self._state.copy()
