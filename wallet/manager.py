"""
Breathe Core — Wallet Manager
Manages EVM wallets for Base and Polygon chains.
Handles USDC balance checks, approvals, and transaction signing.
"""

from web3 import Web3
from eth_account import Account
from config.settings import settings
from config.constants import USDC_BASE, USDC_DECIMALS
from utils.logger import get_logger, log_with_data
from utils.web3_client import get_base_w3

logger = get_logger("wallet")

# Minimal ERC-20 ABI for balance and approval
ERC20_ABI = [
    {
        "constant": True,
        "inputs": [{"name": "_owner", "type": "address"}],
        "name": "balanceOf",
        "outputs": [{"name": "balance", "type": "uint256"}],
        "type": "function",
    },
    {
        "constant": False,
        "inputs": [
            {"name": "_spender", "type": "address"},
            {"name": "_value", "type": "uint256"},
        ],
        "name": "approve",
        "outputs": [{"name": "", "type": "bool"}],
        "type": "function",
    },
    {
        "constant": True,
        "inputs": [
            {"name": "_owner", "type": "address"},
            {"name": "_spender", "type": "address"},
        ],
        "name": "allowance",
        "outputs": [{"name": "", "type": "uint256"}],
        "type": "function",
    },
    {
        "constant": False,
        "inputs": [
            {"name": "_to", "type": "address"},
            {"name": "_value", "type": "uint256"},
        ],
        "name": "transfer",
        "outputs": [{"name": "", "type": "bool"}],
        "type": "function",
    },
]


class WalletManager:
    """Manages the treasury wallet on EVM chains."""

    def __init__(self):
        self.account = None
        self.address = None
        self._initialize()

    def _initialize(self):
        """Load wallet from private key."""
        if not settings.TREASURY_PRIVATE_KEY:
            logger.error("❌ TREASURY_PRIVATE_KEY not set — wallet disabled")
            return

        try:
            self.account = Account.from_key(settings.TREASURY_PRIVATE_KEY)
            self.address = self.account.address
            logger.info(f"✅ Treasury wallet loaded: {self.address}")
        except Exception as e:
            logger.error(f"❌ Failed to load wallet: {e}")

    @property
    def is_ready(self) -> bool:
        return self.account is not None

    def get_eth_balance(self, chain: str = "base") -> float:
        """Get native ETH balance."""
        w3 = get_base_w3()
        balance_wei = w3.eth.get_balance(self.address)
        balance = float(Web3.from_wei(balance_wei, "ether"))
        log_with_data(logger, "info", "ETH balance checked", chain=chain, balance=balance)
        return balance

    def get_usdc_balance(self, chain: str = "base") -> float:
        """Get USDC balance on specified chain."""
        w3 = get_base_w3()
        usdc = w3.eth.contract(address=Web3.to_checksum_address(USDC_BASE), abi=ERC20_ABI)
        raw_balance = usdc.functions.balanceOf(self.address).call()
        decimals = USDC_DECIMALS.get(chain, 6)
        balance = raw_balance / (10 ** decimals)
        log_with_data(logger, "info", "USDC balance checked", chain=chain, balance=balance)
        return balance

    def approve_token(self, token_address: str, spender: str, amount: float, chain: str = "base") -> str:
        """Approve a spender to use tokens. Returns tx hash."""
        if settings.DRY_RUN:
            logger.info(f"[DRY RUN] Would approve {amount} tokens for {spender}")
            return "0x_dry_run"

        w3 = get_base_w3()
        token = w3.eth.contract(address=Web3.to_checksum_address(token_address), abi=ERC20_ABI)
        decimals = USDC_DECIMALS.get(chain, 6)
        amount_raw = int(amount * (10 ** decimals))

        tx = token.functions.approve(
            Web3.to_checksum_address(spender), amount_raw
        ).build_transaction({
            "from": self.address,
            "nonce": w3.eth.get_transaction_count(self.address),
            "gas": 100_000,
            "gasPrice": w3.eth.gas_price,
            "chainId": w3.eth.chain_id,
        })

        signed = self.account.sign_transaction(tx)
        tx_hash = w3.eth.send_raw_transaction(signed.raw_transaction)
        receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

        hash_hex = receipt.transactionHash.hex()
        log_with_data(logger, "info", "Token approved",
                      token=token_address, spender=spender, amount=amount, tx_hash=hash_hex)
        return hash_hex

    def send_transaction(self, tx_data: dict) -> str:
        """Sign and send a transaction. Returns tx hash."""
        if settings.DRY_RUN:
            logger.info(f"[DRY RUN] Would send tx: {tx_data.get('to', 'unknown')}")
            return "0x_dry_run"

        w3 = get_base_w3()
        tx_data["from"] = self.address
        tx_data["nonce"] = w3.eth.get_transaction_count(self.address)
        tx_data["chainId"] = w3.eth.chain_id

        if "gas" not in tx_data:
            tx_data["gas"] = w3.eth.estimate_gas(tx_data)
        if "gasPrice" not in tx_data:
            tx_data["gasPrice"] = w3.eth.gas_price

        signed = self.account.sign_transaction(tx_data)
        tx_hash = w3.eth.send_raw_transaction(signed.raw_transaction)
        receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

        hash_hex = receipt.transactionHash.hex()
        log_with_data(logger, "info", "Transaction sent", tx_hash=hash_hex, status=receipt.status)
        return hash_hex

    def get_portfolio_summary(self) -> dict:
        """Get a complete portfolio summary."""
        eth_bal = self.get_eth_balance()
        usdc_bal = self.get_usdc_balance()

        return {
            "address": self.address,
            "eth_balance": eth_bal,
            "usdc_balance": usdc_bal,
            "total_value_usd": usdc_bal + (eth_bal * self._get_eth_price()),
        }

    def _get_eth_price(self) -> float:
        """Fetch ETH price from on-chain oracle or API."""
        try:
            import requests
            resp = requests.get(
                "https://api.coingecko.com/api/v3/simple/price?ids=ethereum&vs_currencies=usd",
                timeout=10
            )
            return resp.json()["ethereum"]["usd"]
        except Exception:
            logger.warning("Could not fetch ETH price, using 0")
            return 0.0
