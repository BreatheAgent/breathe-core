"""
Breathe Core — PNL Tracker
Tracks profit and loss over time. Calculates daily PNL, ROI, and Sharpe ratio.
"""

import json
import os
from datetime import datetime, timezone
from utils.logger import get_logger

logger = get_logger("pnl_tracker")

PNL_HISTORY_FILE = "data/pnl_history.json"


class PNLTracker:
    """Tracks portfolio performance over time."""

    def __init__(self):
        os.makedirs("data", exist_ok=True)
        self.history = self._load_history()

    def _load_history(self) -> list:
        if os.path.exists(PNL_HISTORY_FILE):
            with open(PNL_HISTORY_FILE, "r") as f:
                return json.load(f)
        return []

    def _save_history(self):
        with open(PNL_HISTORY_FILE, "w") as f:
            json.dump(self.history, f, indent=2)

    def record_snapshot(self, portfolio_state: dict):
        """Record a portfolio snapshot for PNL tracking."""
        snapshot = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "total_value": portfolio_state.get("total_value_usd", 0),
            "positions": portfolio_state.get("positions", {}),
            "allocations": portfolio_state.get("allocations", {}),
        }
        self.history.append(snapshot)
        self._save_history()

    def get_daily_report(self) -> dict:
        """Generate daily PNL report."""
        if len(self.history) < 2:
            return {
                "daily_pnl": 0,
                "total_pnl": 0,
                "total_roi": 0,
                "snapshots_today": len(self.history),
            }

        latest = self.history[-1]["total_value"]
        initial = self.history[0]["total_value"]

        # Find yesterday's last snapshot
        today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        yesterday_snapshots = [
            s for s in self.history if not s["timestamp"].startswith(today)
        ]

        if yesterday_snapshots:
            yesterday_value = yesterday_snapshots[-1]["total_value"]
        else:
            yesterday_value = initial

        daily_pnl = latest - yesterday_value
        total_pnl = latest - initial
        total_roi = total_pnl / initial if initial > 0 else 0

        return {
            "daily_pnl": daily_pnl,
            "total_pnl": total_pnl,
            "total_roi": total_roi,
            "current_value": latest,
            "initial_value": initial,
            "snapshots_total": len(self.history),
        }

    def get_weekly_report(self) -> dict:
        """Generate weekly performance report."""
        report = self.get_daily_report()

        if len(self.history) > 7:
            week_ago_value = self.history[-7]["total_value"]
            current = self.history[-1]["total_value"]
            report["weekly_pnl"] = current - week_ago_value
            report["weekly_roi"] = report["weekly_pnl"] / week_ago_value if week_ago_value > 0 else 0

        return report

    def get_sharpe_ratio(self, risk_free_rate: float = 0.05) -> float:
        """Calculate annualized Sharpe ratio from daily returns."""
        if len(self.history) < 3:
            return 0.0

        # Calculate daily returns
        returns = []
        for i in range(1, len(self.history)):
            prev = self.history[i - 1]["total_value"]
            curr = self.history[i]["total_value"]
            if prev > 0:
                returns.append((curr - prev) / prev)

        if not returns:
            return 0.0

        import statistics
        mean_return = statistics.mean(returns)
        std_return = statistics.stdev(returns) if len(returns) > 1 else 0.001

        daily_rf = risk_free_rate / 365
        sharpe = (mean_return - daily_rf) / std_return * (365 ** 0.5)

        return round(sharpe, 2)
