# backend/transactions.py
import requests
from typing import Dict, Any, Optional

BASE_URL = "https://sei.blockscout.com/api/v2/addresses"
HEADERS = {"accept": "application/json"}


def get_wallet_transactions(
    wallet_address: str,
    page: int = 1,
    limit: int = 50,
) -> Optional[Dict[str, Any]]:
    """
    Return a page of transactions for `wallet_address` from the Sei Blockscout API.
    """
    url = (
        f"{BASE_URL}/{wallet_address}/transactions"
        f"?page={page}&block_number=true&limit={limit}&sort=desc"
    )

    try:
        resp = requests.get(url, headers=HEADERS, timeout=10)
        resp.raise_for_status()
        return resp.json()
    except requests.RequestException as exc:  # network / 4xx / 5xx
        print(f"Could not fetch transactions: {exc}")
        return None


if __name__ == "__main__":
    import argparse

    ap = argparse.ArgumentParser(description="Fetch Sei wallet transactions")
    ap.add_argument("wallet", help="Sei wallet address (0x…)")
    ap.add_argument("--page", type=int, default=1)
    ap.add_argument("--limit", type=int, default=50)
    ns = ap.parse_args()

    data = get_wallet_transactions(ns.wallet, ns.page, ns.limit)
    print(data if data else "No data returned.")
