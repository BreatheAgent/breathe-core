"""
Breathe Core — CEO Agent
The top-level decision orchestrator. Manages capital allocation across
all strategy engines (DeFi, Perps, Polymarket, Memes).

Responsibilities:
- Receive treasury commands from the user
- Determine capital allocation based on risk profile
- Delegate to strategy-specific agents
- Request human approval for large moves
- Produce daily reflection & strategy adjustments
"""

import json
import os
from datetime import datetime, timezone
from config.settings import settings
from portfolio.manager import PortfolioManager
from portfolio.pnl_tracker import PNLTracker
from safety.spending_guard import SpendingGuard
from safety.kill_switch import KillSwitch
from safety.tx_logger import TransactionLogger
from utils.logger import get_logger, log_with_data

logger = get_logger("ceo_agent")


class CEOAgent:
    """
    Central command agent — orchestrates all Breathe operations.

    Flow:
    1. Receives a capital growth command
    2. Assesses current portfolio state
    3. Determines optimal allocation across strategies
    4. Delegates to sub-agents (Yield, Trading, Meme)
    5. Monitors performance and adjusts strategy
    """

    def __init__(self):
        self.portfolio = PortfolioManager()
        self.pnl = PNLTracker()
        self.spending_guard = SpendingGuard()
        self.kill_switch = KillSwitch()
        self.tx_logger = TransactionLogger()
        self.allocation = settings.get_allocation_profile()

        logger.info("🧠 CEO Agent initialized")
        logger.info(f"   Risk tolerance: {settings.RISK_TOLERANCE}")
        logger.info(f"   Allocation: {json.dumps(self.allocation)}")

    def execute_growth_cycle(self):
        """
        Main decision loop — called periodically.
        This is the ReAct reasoning cycle for capital management.
        """
        # ── Step 0: Safety Check ──
        if not self.kill_switch.check_or_halt():
            return {"status": "HALTED", "reason": "Kill switch active"}

        logger.info("═" * 60)
        logger.info("🧠 CEO AGENT — Growth Cycle Starting")
        logger.info("═" * 60)

        # ── Step 1: OBSERVE — Assess current state ──
        logger.info("📊 [OBSERVE] Assessing portfolio state...")
        portfolio_state = self.portfolio.get_state()
        total_value = portfolio_state["total_value_usd"]
        spending_summary = self.spending_guard.get_daily_summary()

        logger.info(f"   Total portfolio value: ${total_value:.2f}")
        logger.info(f"   Today's spend: ${spending_summary['total_spent']:.2f} / ${spending_summary['limit']:.2f}")

        # ── Step 2: THINK — Determine what needs rebalancing ──
        logger.info("🤔 [THINK] Analyzing allocation drift...")
        actions = self._analyze_allocation(portfolio_state)

        if not actions:
            logger.info("   ✅ Portfolio is balanced — no actions needed")
            return {"status": "BALANCED", "actions": []}

        # ── Step 3: DECIDE — Filter through safety checks ──
        logger.info(f"📋 [DECIDE] {len(actions)} potential actions identified")
        approved_actions = []
        for action in actions:
            if self._approve_action(action):
                approved_actions.append(action)
            else:
                logger.warning(f"   ❌ Action rejected: {action['description']}")

        # ── Step 4: ACT — Execute approved actions ──
        if settings.DRY_RUN:
            logger.info("🔍 [DRY RUN] Would execute the following actions:")
            for a in approved_actions:
                logger.info(f"   → {a['description']} | ${a['amount']:.2f}")
            return {"status": "DRY_RUN", "actions": approved_actions}

        results = []
        for action in approved_actions:
            result = self._execute_action(action)
            results.append(result)

        # ── Step 5: REFLECT — Log and learn ──
        logger.info("🔄 [REFLECT] Cycle complete")
        self.pnl.record_snapshot(portfolio_state)
        self._save_cycle_log(results)

        return {"status": "EXECUTED", "actions": results}

    def _analyze_allocation(self, portfolio_state: dict) -> list:
        """
        Compare current allocation vs target and generate rebalance actions.
        """
        current = portfolio_state.get("allocations", {})
        target = self.allocation
        total = portfolio_state["total_value_usd"]
        actions = []

        for strategy, target_pct in target.items():
            current_pct = current.get(strategy, 0)
            drift = target_pct - current_pct

            # Only rebalance if drift > 5%
            if abs(drift) > 0.05:
                amount = abs(drift) * total
                action_type = "deploy" if drift > 0 else "withdraw"
                actions.append({
                    "strategy": strategy,
                    "action": action_type,
                    "amount": amount,
                    "current_pct": current_pct,
                    "target_pct": target_pct,
                    "drift": drift,
                    "description": f"{action_type.upper()} ${amount:.2f} → {strategy} (drift: {drift:+.1%})",
                })

        return actions

    def _approve_action(self, action: dict) -> bool:
        """Run action through safety checks."""
        amount = action["amount"]

        # Check daily spending limit
        if not self.spending_guard.can_spend(amount):
            # Request human approval for large moves
            return self.spending_guard.request_human_approval(
                amount, action["description"]
            )

        return True

    def _execute_action(self, action: dict) -> dict:
        """
        Execute a single action by delegating to the appropriate strategy engine.
        In production, this calls breathe-defi, breathe-trading, or breathe-memes via API/import.
        """
        strategy = action["strategy"]
        logger.info(f"⚡ Executing: {action['description']}")

        # Record spending
        self.spending_guard.record_spend(
            action["amount"], strategy, action["action"]
        )

        # Log transaction
        self.tx_logger.log_transaction(
            protocol=strategy,
            action=action["action"],
            amount_usdc=action["amount"],
            tx_hash="pending",  # Would be real in production
            details=action,
        )

        # In production: delegate to sub-module
        # if strategy == "defi": yield_agent.execute(action)
        # if strategy == "perps": trading_engine.execute(action)
        # etc.

        return {**action, "status": "executed", "timestamp": datetime.now(timezone.utc).isoformat()}

    def _save_cycle_log(self, results: list):
        """Save cycle results to disk."""
        os.makedirs("data", exist_ok=True)
        log_file = "data/cycle_log.json"

        history = []
        if os.path.exists(log_file):
            with open(log_file, "r") as f:
                history = json.load(f)

        history.append({
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "actions_count": len(results),
            "results": results,
        })

        with open(log_file, "w") as f:
            json.dump(history, f, indent=2)

    def daily_reflection(self) -> dict:
        """
        End-of-day self-assessment.
        Reviews today's performance and adjusts strategy for tomorrow.
        """
        logger.info("🌅 Daily Reflection Starting...")

        pnl_report = self.pnl.get_daily_report()
        tx_summary = self.tx_logger.get_summary()
        spend_summary = self.spending_guard.get_daily_summary()

        reflection = {
            "date": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
            "pnl": pnl_report,
            "transactions": tx_summary,
            "spending": spend_summary,
            "assessment": self._generate_assessment(pnl_report),
        }

        # Save reflection
        os.makedirs("data/reflections", exist_ok=True)
        with open(f"data/reflections/{reflection['date']}.json", "w") as f:
            json.dump(reflection, f, indent=2)

        logger.info(f"   Daily PNL: ${pnl_report.get('daily_pnl', 0):.2f}")
        logger.info(f"   Total ROI: {pnl_report.get('total_roi', 0):.2%}")

        return reflection

    def _generate_assessment(self, pnl_report: dict) -> str:
        """Generate a text assessment of today's performance."""
        daily_pnl = pnl_report.get("daily_pnl", 0)
        roi = pnl_report.get("total_roi", 0)

        if daily_pnl > 0:
            return f"Positive day (+${daily_pnl:.2f}). Strategy performing within parameters."
        elif daily_pnl > -10:
            return f"Minor loss (${daily_pnl:.2f}). Within acceptable risk tolerance."
        else:
            return f"Significant loss (${daily_pnl:.2f}). Consider reducing exposure."

    def get_status(self) -> dict:
        """Get complete agent status for dashboard/reporting."""
        return {
            "agent": "CEO",
            "risk_tolerance": settings.RISK_TOLERANCE,
            "allocation": self.allocation,
            "kill_switch": self.kill_switch.get_status(),
            "daily_spending": self.spending_guard.get_daily_summary(),
            "portfolio": self.portfolio.get_state(),
            "dry_run": settings.DRY_RUN,
        }
