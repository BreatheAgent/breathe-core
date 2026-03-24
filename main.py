#!/usr/bin/env python3
"""
🌬️ Breathe Core — Autonomous AI Capital Growth Engine
=====================================================

The central nervous system of the Breathe ecosystem.
Manages capital allocation across DeFi, Perps, Polymarket, and Meme strategies.

Usage:
    python main.py --mode treasury              # Start autonomous growth cycle
    python main.py --mode treasury --dry-run     # Simulate without real transactions
    python main.py --mode report                 # Generate PNL report
    python main.py --mode status                 # Show current portfolio status
    python main.py --mode kill                   # Emergency shutdown
    python main.py --mode resume                 # Resume after kill switch
    python main.py --validate-config             # Validate configuration
"""

import argparse
import json
import sys
import time

from config.settings import settings, Settings
from agents.ceo_agent import CEOAgent
from agents.risk_guardian import RiskGuardian
from safety.kill_switch import KillSwitch
from utils.logger import get_logger

logger = get_logger("breathe", level=settings.LOG_LEVEL)

# ══════════════════════════════════════════════════════
# ASCII Banner
# ══════════════════════════════════════════════════════

BANNER = """
╔═══════════════════════════════════════════════════════════╗
║                                                           ║
║   🌬️  B R E A T H E                                      ║
║   Autonomous AI Capital Growth Engine                     ║
║                                                           ║
║   "Not an assistant. An autonomous economic entity."      ║
║                                                           ║
║   Chains: Base · Polygon · Solana                         ║
║   Strategies: DeFi · Perps · Polymarket · Memes           ║
║                                                           ║
╚═══════════════════════════════════════════════════════════╝
"""


def validate_config():
    """Validate all configuration variables."""
    print("🔍 Validating configuration...")
    errors = Settings.validate()
    if errors:
        print("❌ Configuration errors:")
        for e in errors:
            print(f"   • {e}")
        return False
    else:
        print("✅ Configuration valid!")
        profile = Settings.get_allocation_profile()
        print(f"   Risk tolerance: {settings.RISK_TOLERANCE}")
        print(f"   Allocation: {json.dumps(profile, indent=2)}")
        print(f"   Daily limit: ${settings.DAILY_SPEND_LIMIT}")
        print(f"   Max leverage: {settings.MAX_LEVERAGE}x")
        print(f"   Dry run: {settings.DRY_RUN}")
        return True


def run_treasury_mode():
    """Main autonomous growth mode."""
    print(BANNER)
    logger.info("🚀 Starting Treasury Mode")

    if settings.DRY_RUN:
        logger.info("📌 DRY RUN MODE — No real transactions will be executed")

    # Initialize agents
    ceo = CEOAgent()
    risk_guardian = RiskGuardian()

    logger.info(f"💰 Starting capital: $1,000 USDC")
    logger.info(f"📊 Risk profile: {settings.RISK_TOLERANCE}")
    logger.info(f"⏱️  Scan interval: {settings.SCAN_INTERVAL}s")
    logger.info("")

    try:
        cycle_count = 0
        while True:
            cycle_count += 1
            logger.info(f"\n{'═' * 60}")
            logger.info(f"🔄 Growth Cycle #{cycle_count}")
            logger.info(f"{'═' * 60}")

            # Execute growth cycle
            result = ceo.execute_growth_cycle()
            logger.info(f"   Cycle result: {result['status']}")

            # Check drawdown
            portfolio = ceo.portfolio.get_state()
            drawdown = risk_guardian.check_drawdown(
                portfolio["total_value_usd"],
                portfolio.get("peak_value", portfolio["total_value_usd"]),
            )
            if drawdown.get("exceeded"):
                logger.critical("🛑 Drawdown limit exceeded — activating kill switch")
                ceo.kill_switch.activate("Automatic: drawdown threshold exceeded")
                break

            # Wait for next cycle
            time.sleep(settings.SCAN_INTERVAL)

    except KeyboardInterrupt:
        logger.info("\n⚡ Graceful shutdown initiated")
        logger.info("   Running final reflection...")
        ceo.daily_reflection()
        logger.info("   ✅ Shutdown complete")


def run_report_mode():
    """Generate and display PNL report."""
    print(BANNER)
    ceo = CEOAgent()

    report = ceo.daily_reflection()
    print("\n📊 DAILY REPORT")
    print("═" * 40)
    print(json.dumps(report, indent=2))


def run_status_mode():
    """Show current portfolio status."""
    print(BANNER)
    ceo = CEOAgent()

    status = ceo.get_status()
    print("\n📊 PORTFOLIO STATUS")
    print("═" * 40)
    print(json.dumps(status, indent=2))


def run_kill_mode():
    """Activate emergency kill switch."""
    ks = KillSwitch()
    result = ks.activate("Manual kill command")
    print(json.dumps(result, indent=2))


def run_resume_mode():
    """Resume after kill switch."""
    ks = KillSwitch()
    ks.deactivate("Manual resume command")
    print("✅ Operations resumed")


def main():
    parser = argparse.ArgumentParser(
        description="🌬️ Breathe — Autonomous AI Capital Growth Engine"
    )
    parser.add_argument(
        "--mode",
        choices=["treasury", "report", "status", "kill", "resume"],
        default="treasury",
        help="Operating mode",
    )
    parser.add_argument("--dry-run", action="store_true", help="Simulate without real transactions")
    parser.add_argument("--validate-config", action="store_true", help="Validate configuration")

    args = parser.parse_args()

    if args.validate_config:
        sys.exit(0 if validate_config() else 1)

    if args.dry_run:
        import os
        os.environ["DRY_RUN"] = "true"

    mode_handlers = {
        "treasury": run_treasury_mode,
        "report": run_report_mode,
        "status": run_status_mode,
        "kill": run_kill_mode,
        "resume": run_resume_mode,
    }

    handler = mode_handlers.get(args.mode)
    if handler:
        handler()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
