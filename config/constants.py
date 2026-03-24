"""
Breathe Core — On-Chain Constants
Contract addresses, token addresses, and protocol constants for Base Mainnet.
"""

# ══════════════════════════════════════════════════════
# Base Mainnet Token Addresses
# ══════════════════════════════════════════════════════

USDC_BASE = "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913"
WETH_BASE = "0x4200000000000000000000000000000000000006"
USDbC_BASE = "0xd9aAEc86B65D86f6A7B5B1b0c42FFA531710b6Ca"

# ══════════════════════════════════════════════════════
# DeFi Protocol Addresses (Base Mainnet)
# ══════════════════════════════════════════════════════

# Aave V3
AAVE_V3_POOL = "0xA238Dd80C259a72e81d7e4664a9801593F98d1c5"
AAVE_V3_DATA_PROVIDER = "0x2d8A3C5677189723C4cB8873CfC9C8976FDF38Ac"

# Morpho Blue
MORPHO_BLUE = "0xBBBBBbbBBb9cC5e90e3b3Af64bdAF62C37EEFFCb"

# Aerodrome
AERODROME_ROUTER = "0xcF77a3Ba9A5CA399B7c97c74d54e5b1Beb874E43"
AERODROME_FACTORY = "0x420DD381b31aEf6683db6B902084cB0FFECe40Da"

# Uniswap V3
UNISWAP_V3_ROUTER = "0x2626664c2603336E57B271c5C0b26F421741e481"
UNISWAP_V3_FACTORY = "0x33128a8fC17869897dcE68Ed026d694621f6FDfD"

# ══════════════════════════════════════════════════════
# Perpetuals Protocol Addresses (Base Mainnet)
# ══════════════════════════════════════════════════════

# GMX V2 (Base)
GMX_ROUTER = "0x7C68C7866A64FA2160F78EEaE12217FFbf871fa8"
GMX_EXCHANGE_ROUTER = "0x900173A66dbD345006C51fA35fA3aB760FcD843b"
GMX_READER = "0x0537C767cDAC0726c76f5b58F64F5a7b5f9A2f1C"

# Synthetix Perps V3 (Base)
SYNTHETIX_PERPS_MARKET = "0x0A2AF931eFFd34b81ebcc57E3d3c9B1E1dE1C9Ce"
SYNTHETIX_CORE = "0xffffffaEff0B96Ea8e4f94b2253f31abdD875847"

# ══════════════════════════════════════════════════════
# Polymarket (Polygon → bridged)
# ══════════════════════════════════════════════════════

POLYMARKET_CTF = "0x4D97DCd97eC945f40cF65F87097ACe5EA0476045"
POLYMARKET_EXCHANGE = "0x4bFb41d5B3570DeFd03C39a9A4D8dE6Bd8B8982E"
USDC_POLYGON = "0x3c499c542cEF5E3811e1192ce70d8cC03d5c3359"

# ══════════════════════════════════════════════════════
# Solana Addresses
# ══════════════════════════════════════════════════════

USDC_SOLANA = "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v"
SOL_MINT = "So11111111111111111111111111111111111111112"
RAYDIUM_AMM = "675kPX9MHTjS2zt1qfr1NYHuzeLXfQM9H24wFSUt1Mp8"
JUPITER_V6_API = "https://quote-api.jup.ag/v6"
PUMPFUN_PROGRAM = "6EF8rrecthR5Dkzon8Nwu78hRvfCKubJ14M5uBEwF6P"

# ══════════════════════════════════════════════════════
# Operational Constants
# ══════════════════════════════════════════════════════

# Minimum viable amounts
MIN_TRADE_USDC = 1.0          # Don't trade less than $1
MIN_YIELD_APY = 0.01          # Minimum 1% APY to consider
MAX_GAS_GWEI = 50             # Skip if gas is too high
MAX_SLIPPAGE_PCT = 0.005      # 0.5% max slippage

# Risk scoring
PROTOCOL_RISK_SCORES = {
    "aave_v3": 0.1,       # Very safe — battle-tested lending
    "morpho": 0.2,        # Safe — optimized lending
    "uniswap_v3": 0.3,    # Moderate — IL risk
    "aerodrome": 0.35,    # Moderate — newer protocol
    "gmx_v2": 0.5,        # Higher — leverage
    "synthetix": 0.5,     # Higher — leverage
    "polymarket": 0.6,    # Higher — prediction risk
    "meme_tokens": 0.9,   # Very high — rug risk
}

# USDC decimals per chain
USDC_DECIMALS = {
    "base": 6,
    "polygon": 6,
    "solana": 6,
}
