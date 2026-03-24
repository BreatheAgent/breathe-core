"""
Breathe Core — Risk Guardian Agent
The safety watchdog that monitors all agent activity and can veto or halt operations.

Responsibilities:
- Validate every proposed transaction against risk parameters
- Monitor portfolio concentration (max % in single protocol)
- Track drawdown and halt if threshold exceeded
- Enforce leverage limits
- Verify smart contract risk scores
"""

from config.settings import settings
from config.constants import PROTOCOL_RISK_SCORES
from utils.logger import get_logger, log_with_data

logger = get_logger("risk_guardian")


class RiskGuardian:
    """
    Risk monitoring agent — validates all actions before execution.
    Has veto power over any transaction.
    """

    def __init__(self):
        self.max_single_trade = settings.MAX_SINGLE_TRADE_PCT
        self.max_meme_trade = settings.MAX_MEME_TRADE_PCT
        self.max_leverage = settings.MAX_LEVERAGE
        self.stop_loss = settings.STOP_LOSS_PCT
        self.max_drawdown = 0.15  # Halt if portfolio drops 15% from peak

        logger.info("🛡️ Risk Guardian initialized")
        logger.info(f"   Max single trade: {self.max_single_trade:.0%}")
        logger.info(f"   Max leverage: {self.max_leverage}x")
        logger.info(f"   Stop-loss: {self.stop_loss:.0%}")

    def validate_trade(self, trade: dict, portfolio_value: float) -> dict:
        """
        Validate a proposed trade against all risk parameters.

        Args:
            trade: {
                "protocol": str,
                "action": str,
                "amount": float,
                "leverage": float (optional),
                "strategy": str,
            }
            portfolio_value: Current total portfolio value in USD

        Returns:
            {"approved": bool, "reason": str, "risk_score": float}
        """
        checks = []

        # ── Check 1: Position size limit ──
        max_pct = self.max_meme_trade if trade.get("strategy") == "memes" else self.max_single_trade
        trade_pct = trade["amount"] / portfolio_value if portfolio_value > 0 else 1.0

        if trade_pct > max_pct:
            checks.append({
                "check": "position_size",
                "passed": False,
                "detail": f"Trade is {trade_pct:.1%} of portfolio (max: {max_pct:.1%})",
            })
        else:
            checks.append({"check": "position_size", "passed": True})

        # ── Check 2: Leverage limit ──
        leverage = trade.get("leverage", 1.0)
        if leverage > self.max_leverage:
            checks.append({
                "check": "leverage",
                "passed": False,
                "detail": f"Leverage {leverage}x exceeds max {self.max_leverage}x",
            })
        else:
            checks.append({"check": "leverage", "passed": True})

        # ── Check 3: Protocol risk score ──
        protocol = trade.get("protocol", "unknown")
        risk_score = PROTOCOL_RISK_SCORES.get(protocol, 0.5)

        risk_threshold = {
            "conservative": 0.3,
            "moderate": 0.6,
            "aggressive": 0.9,
        }.get(settings.RISK_TOLERANCE, 0.6)

        if risk_score > risk_threshold:
            checks.append({
                "check": "protocol_risk",
                "passed": False,
                "detail": f"Protocol risk {risk_score} exceeds threshold {risk_threshold} for {settings.RISK_TOLERANCE} profile",
            })
        else:
            checks.append({"check": "protocol_risk", "passed": True})

        # ── Check 4: Minimum trade size ──
        if trade["amount"] < 1.0:
            checks.append({
                "check": "min_amount",
                "passed": False,
                "detail": f"Trade amount ${trade['amount']:.2f} below minimum $1.00",
            })
        else:
            checks.append({"check": "min_amount", "passed": True})

        # ── Final verdict ──
        all_passed = all(c["passed"] for c in checks)
        failed = [c for c in checks if not c["passed"]]

        result = {
            "approved": all_passed,
            "risk_score": risk_score,
            "checks": checks,
            "reason": "All checks passed" if all_passed else "; ".join(c["detail"] for c in failed),
        }

        if all_passed:
            log_with_data(logger, "info", f"✅ Trade approved: {trade.get('protocol')}",
                         amount=trade["amount"], risk_score=risk_score)
        else:
            log_with_data(logger, "warning", f"❌ Trade REJECTED: {result['reason']}",
                         trade=trade, checks=failed)

        return result

    def check_drawdown(self, current_value: float, peak_value: float) -> dict:
        """
        Check if portfolio drawdown exceeds maximum threshold.
        If exceeded, recommends activating kill switch.
        """
        if peak_value <= 0:
            return {"exceeded": False}

        drawdown = (peak_value - current_value) / peak_value

        result = {
            "drawdown": drawdown,
            "threshold": self.max_drawdown,
            "exceeded": drawdown > self.max_drawdown,
            "current_value": current_value,
            "peak_value": peak_value,
        }

        if result["exceeded"]:
            logger.critical(
                f"🚨 DRAWDOWN ALERT: {drawdown:.1%} exceeds {self.max_drawdown:.1%} threshold!\n"
                f"   Peak: ${peak_value:.2f} → Current: ${current_value:.2f}\n"
                f"   RECOMMENDATION: Activate kill switch"
            )

        return result

    def validate_portfolio_concentration(self, positions: dict, total_value: float) -> list:
        """
        Check if any single protocol has too much concentration.
        Max 40% in any single protocol.
        """
        max_concentration = 0.40
        warnings = []

        for protocol, value in positions.items():
            pct = value / total_value if total_value > 0 else 0
            if pct > max_concentration:
                warnings.append({
                    "protocol": protocol,
                    "concentration": pct,
                    "max": max_concentration,
                    "excess": value - (max_concentration * total_value),
                })
                logger.warning(
                    f"⚠️ Concentration risk: {protocol} is {pct:.1%} of portfolio (max: {max_concentration:.1%})"
                )

        return warnings

    def get_risk_report(self, portfolio_state: dict) -> dict:
        """Generate a comprehensive risk assessment."""
        return {
            "risk_tolerance": settings.RISK_TOLERANCE,
            "max_leverage": self.max_leverage,
            "max_single_trade": self.max_single_trade,
            "max_meme_trade": self.max_meme_trade,
            "stop_loss": self.stop_loss,
            "max_drawdown": self.max_drawdown,
            "concentration_warnings": self.validate_portfolio_concentration(
                portfolio_state.get("positions", {}),
                portfolio_state.get("total_value_usd", 0),
            ),
        }
