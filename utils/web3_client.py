"""
Breathe Core — Multi-Chain Web3 Client
Shared Web3 provider instances for Base, Polygon, and Solana RPCs.
"""

from web3 import Web3
from config.settings import settings
from utils.logger import get_logger

logger = get_logger("web3_client")

# ── Base Mainnet ──
_base_w3 = None

def get_base_w3() -> Web3:
    """Get or create Web3 instance for Base Mainnet."""
    global _base_w3
    if _base_w3 is None:
        _base_w3 = Web3(Web3.HTTPProvider(settings.BASE_RPC_URL))
        if _base_w3.is_connected():
            chain_id = _base_w3.eth.chain_id
            logger.info(f"Connected to Base Mainnet (chain_id={chain_id})")
        else:
            logger.error("Failed to connect to Base Mainnet")
    return _base_w3


# ── Polygon ──
_polygon_w3 = None

def get_polygon_w3() -> Web3:
    """Get or create Web3 instance for Polygon."""
    global _polygon_w3
    if _polygon_w3 is None:
        _polygon_w3 = Web3(Web3.HTTPProvider(settings.POLYGON_RPC_URL))
        if _polygon_w3.is_connected():
            chain_id = _polygon_w3.eth.chain_id
            logger.info(f"Connected to Polygon (chain_id={chain_id})")
        else:
            logger.error("Failed to connect to Polygon")
    return _polygon_w3


def get_gas_price_gwei(w3: Web3) -> float:
    """Get current gas price in Gwei."""
    return float(Web3.from_wei(w3.eth.gas_price, "gwei"))


def is_gas_acceptable(w3: Web3, max_gwei: float = 50.0) -> bool:
    """Check if current gas price is within acceptable range."""
    current = get_gas_price_gwei(w3)
    acceptable = current <= max_gwei
    if not acceptable:
        logger.warning(f"Gas too high: {current:.1f} Gwei (max: {max_gwei})")
    return acceptable
