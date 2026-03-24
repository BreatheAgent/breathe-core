"""
Breathe Core — Centralized Configuration
Loads all settings from environment variables with sensible defaults.
"""

import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    """Central configuration for the Breathe autonomous agent."""

    # ── Chain RPCs ──
    BASE_RPC_URL: str = os.getenv("BASE_RPC_URL", "https://mainnet.base.org")
    SOLANA_RPC_URL: str = os.getenv("SOLANA_RPC_URL", "https://api.mainnet-beta.solana.com")
    POLYGON_RPC_URL: str = os.getenv("POLYGON_RPC_URL", "https://polygon-rpc.com")

    # ── Wallet Keys ──
    TREASURY_PRIVATE_KEY: str = os.getenv("TREASURY_PRIVATE_KEY", "")
    SOLANA_PRIVATE_KEY: str = os.getenv("SOLANA_PRIVATE_KEY", "")

    # ── API Keys ──
    VIRTUALS_API_KEY: str = os.getenv("VIRTUALS_API_KEY", "")
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    POLYMARKET_API_KEY: str = os.getenv("POLYMARKET_API_KEY", "")
    DEXSCREENER_API_KEY: str = os.getenv("DEXSCREENER_API_KEY", "")

    # ── Risk Parameters ──
    RISK_TOLERANCE: str = os.getenv("RISK_TOLERANCE", "moderate")  # conservative, moderate, aggressive
    DAILY_SPEND_LIMIT: float = float(os.getenv("DAILY_SPEND_LIMIT", "100"))
    MAX_LEVERAGE: float = float(os.getenv("MAX_LEVERAGE", "3.0"))
    MAX_SINGLE_TRADE_PCT: float = float(os.getenv("MAX_SINGLE_TRADE_PCT", "0.10"))  # 10% of treasury
    MAX_MEME_TRADE_PCT: float = float(os.getenv("MAX_MEME_TRADE_PCT", "0.02"))  # 2% of treasury
    STOP_LOSS_PCT: float = float(os.getenv("STOP_LOSS_PCT", "0.30"))  # 30% stop-loss
    TAKE_PROFIT_MEME: float = float(os.getenv("TAKE_PROFIT_MEME", "3.0"))  # 3x take-profit for memes

    # ── Allocation Strategy (moderate default) ──
    ALLOC_DEFI: float = float(os.getenv("ALLOC_DEFI", "0.40"))
    ALLOC_PERPS: float = float(os.getenv("ALLOC_PERPS", "0.25"))
    ALLOC_POLYMARKET: float = float(os.getenv("ALLOC_POLYMARKET", "0.20"))
    ALLOC_MEMES: float = float(os.getenv("ALLOC_MEMES", "0.15"))

    # ── Contracts ──
    VIRTUALS_AGENT_CONTRACT: str = os.getenv(
        "VIRTUALS_AGENT_CONTRACT", "0x4E35C3F6314A349Ed923Bd2F493646Ad9b320494"
    )

    # ── Operational ──
    SCAN_INTERVAL: int = int(os.getenv("SCAN_INTERVAL", "60"))  # seconds
    REBALANCE_INTERVAL: int = int(os.getenv("REBALANCE_INTERVAL", "3600"))  # 1 hour
    REPORT_HOUR: int = int(os.getenv("REPORT_HOUR", "9"))  # daily report time (UTC)
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    DRY_RUN: bool = os.getenv("DRY_RUN", "false").lower() == "true"

    @classmethod
    def validate(cls) -> list[str]:
        """Validate required configuration. Returns list of errors."""
        errors = []
        if not cls.TREASURY_PRIVATE_KEY:
            errors.append("TREASURY_PRIVATE_KEY is required")
        if not cls.BASE_RPC_URL:
            errors.append("BASE_RPC_URL is required")

        total_alloc = cls.ALLOC_DEFI + cls.ALLOC_PERPS + cls.ALLOC_POLYMARKET + cls.ALLOC_MEMES
        if abs(total_alloc - 1.0) > 0.01:
            errors.append(f"Allocations must sum to 1.0, got {total_alloc}")

        if cls.RISK_TOLERANCE not in ("conservative", "moderate", "aggressive"):
            errors.append(f"Invalid RISK_TOLERANCE: {cls.RISK_TOLERANCE}")

        return errors

    @classmethod
    def get_allocation_profile(cls) -> dict:
        """Return allocation based on risk tolerance."""
        profiles = {
            "conservative": {"defi": 0.60, "perps": 0.20, "polymarket": 0.15, "memes": 0.05},
            "moderate":     {"defi": 0.40, "perps": 0.25, "polymarket": 0.20, "memes": 0.15},
            "aggressive":   {"defi": 0.20, "perps": 0.30, "polymarket": 0.25, "memes": 0.25},
        }
        return profiles.get(cls.RISK_TOLERANCE, profiles["moderate"])


settings = Settings()
