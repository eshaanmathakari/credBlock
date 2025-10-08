# backend/coin_balance.py
import argparse
import sys
import os

from web3 import Web3

DEFAULT_RPC_URL = "https://evm-rpc.sei-apis.com"
RPC_URL = os.getenv("SEI_RPC_URL", DEFAULT_RPC_URL)

__all__ = ["get_wallet_balance"]


def get_wallet_balance(wallet_address: str) -> float:
    """Return the SEI balance (in native SEI) for `wallet_address`."""
    w3 = Web3(Web3.HTTPProvider(RPC_URL))
    if not w3.is_connected():
        raise ConnectionError("Failed to connect to the Sei EVM RPC endpoint")

    balance_wei = w3.eth.get_balance(Web3.to_checksum_address(wallet_address))
    return w3.from_wei(balance_wei, "ether")


def _cli() -> None:
    parser = argparse.ArgumentParser(
        description="Fetch the native SEI balance for a wallet address"
    )
    parser.add_argument("wallet", help="Sei EVM wallet (0x…) address")
    args = parser.parse_args()

    try:
        balance = get_wallet_balance(args.wallet)
        print(f"Wallet {args.wallet} holds {balance} SEI")
    except Exception as exc:  # noqa: BLE001
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    _cli()
