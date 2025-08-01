"""
Credit-scoring engine for Sei wallets – FINAL FAST VERSION
• automatic 2 000-block batching (provider limit)
• starts scan at wallet’s first ever tx block
• re-uses coin_balance.get_wallet_balance
"""

from __future__ import annotations

import datetime as _dt
import json
import time
from dataclasses import dataclass
from typing import Any, Dict, List, Set, Tuple

import requests
from web3 import Web3

from coin_balance import get_wallet_balance  # ← reuse working routine


# --------------------------------------------------------------------------- #
# 1.  RPC / Explorer helpers
# --------------------------------------------------------------------------- #

RPC_URL = "https://evm-rpc.sei-apis.com"
EXPLORER = "https://sei.blockscout.com/api/v2/addresses"
HEADERS = {"accept": "application/json"}

MAX_BLOCK_RANGE = 1_000  # enforced by Sei RPC (reduced from 2000)


def _fetch_json(url: str, retries: int = 3, timeout: int = 30) -> Dict[str, Any]:
    """Fetch JSON with retry logic and better timeout handling."""
    for attempt in range(retries):
        try:
            resp = requests.get(url, headers=HEADERS, timeout=timeout)
            resp.raise_for_status()
            return resp.json()
        except (requests.exceptions.Timeout, requests.exceptions.ConnectionError) as e:
            if attempt < retries - 1:
                wait_time = (attempt + 1) * 2  # Progressive backoff: 2s, 4s, 6s
                print(f"API request failed (attempt {attempt + 1}/{retries}), retrying in {wait_time}s...")
                time.sleep(wait_time)
                continue
            else:
                print(f"API request failed after {retries} attempts: {e}")
                # Return empty dict so the script can continue with default values
                return {}
        except requests.exceptions.RequestException as e:
            print(f"API request error: {e}")
            return {}


# --------------------------------------------------------------------------- #
# 2.  Sei provider – light wrapper around Web3 + explorer
# --------------------------------------------------------------------------- #

@dataclass(slots=True)
class SeiProvider:
    w3: Web3

    @classmethod
    def connect(cls, rpc: str = RPC_URL) -> "SeiProvider":
        w3 = Web3(Web3.HTTPProvider(rpc))
        if not w3.is_connected():
            raise ConnectionError("Cannot reach Sei RPC")
        return cls(w3=w3)

    # -------- wallet metadata -------------------------------------------- #

    def first_tx_info(self, wallet: str) -> Tuple[_dt.datetime | None, int | None]:
        """
        Returns (timestamp, block_number) of the wallet's very first tx.
        If the wallet has no tx history or API fails, both return None.
        """
        url = f"{EXPLORER}/{wallet}/transactions?limit=1&sort=asc"
        data = _fetch_json(url)
        items = data.get("items", []) if data else []
        if not items:
            return None, None

        try:
            tx = items[0]
            ts_raw = tx["timestamp"]
            blk_raw = tx.get("block_number") or tx.get("blockNumber")

            # timestamp can be "168…" or ISO "2025-07-15T…" – normalise
            if isinstance(ts_raw, (int, float)) or (isinstance(ts_raw, str) and ts_raw.isdigit()):
                ts = _dt.datetime.fromtimestamp(int(ts_raw), _dt.timezone.utc)
            else:
                ts = _dt.datetime.fromisoformat(ts_raw.replace("Z", "+00:00"))

            blk = int(blk_raw) if blk_raw is not None else None
            return ts, blk
        except (KeyError, ValueError, TypeError) as e:
            print(f"Error parsing transaction data: {e}")
            return None, None

    def counters(self, wallet: str) -> Dict[str, Any]:
        data = _fetch_json(f"{EXPLORER}/{wallet}/counters")
        return data if data else {"transaction_count": 0, "unique_addresses": []}


# --------------------------------------------------------------------------- #
# 3.  Lending-pool event fetcher
# --------------------------------------------------------------------------- #

def batched_logs(
    event,
    start: int,
    end: int,
    **filters,
) -> List[Any]:
    """Fetch logs in provider-safe 2 000-block chunks with auto-retry."""
    all_logs: List[Any] = []
    cur = start
    while cur <= end:
        tgt = min(cur + MAX_BLOCK_RANGE - 1, end)
        try:
            logs = event.get_logs(
                from_block=cur,
                to_block=tgt,
                argument_filters=filters,
            )
            all_logs.extend(logs)
            if logs:
                print(f"   {len(logs):3d} logs {cur:>8d}-{tgt:<8d}")
        except Exception as exc:
            print(f"RPC error {cur}-{tgt}: {exc} – retry in 0.5 s")
            time.sleep(0.5)
            continue  # retry the same chunk
        cur = tgt + 1
    return all_logs


def lending_history(
    wallet: str,
    contract,
    w3: Web3,
    start_block: int,
) -> List[Dict[str, Any]]:
    """Chronological Borrow / Repay / Liquidation events for wallet."""
    latest = w3.eth.block_number
    hist: List[Dict[str, Any]] = []

    for ev_name, ev in [
        ("Borrow", contract.events.Borrow()),
        ("Repay", contract.events.Repay()),
        ("Liquidation", contract.events.LiquidationCall()),
    ]:
        print(f"Scanning {ev_name} events…")
        logs = batched_logs(ev, start_block, latest, user=wallet)
        for lg in logs:
            args = lg["args"]
            hist.append(
                {
                    "type": ev_name,
                    "block": lg["blockNumber"],
                    "tx": lg["transactionHash"].hex(),
                    **{k: args[k] for k in args},
                }
            )
    hist.sort(key=lambda x: x["block"])
    return hist


# --------------------------------------------------------------------------- #
# 4.  Scoring engine
# --------------------------------------------------------------------------- #

@dataclass(slots=True)
class CreditScore:
    wallet: str
    score: int
    risk: str
    factors: Dict[str, int]


class DeFiCreditScorer:
    BASE = 500
    AGE_W = 0.15
    TRANS_W = 0.20
    BAL_W = 0.25
    REPAY_W = 0.30
    DEFI_W = 0.10

    def __init__(self, lending_pool_addr: str, abi_path: str = "yei-pool.json"):
        self.provider = SeiProvider.connect()
        with open(abi_path, "r", encoding="utf-8") as fh:
            abi = json.load(fh)
        self.pool = self.provider.w3.eth.contract(
            address=Web3.to_checksum_address(lending_pool_addr),
            abi=abi,
        )
        print("Connected to Sei & lending pool")

    # ---------- pillar mini-scores --------------------------------------- #

    def _score_age(self, days: int | None) -> int:
        if days is None:
            return -50
        if days > 730:
            return +100
        if days > 365:
            return +60
        if days > 90:
            return +20
        return -30

    def _score_transactions(self, txs: int) -> int:
        if txs > 2_000:
            return +100
        if txs > 300:
            return +60
        if txs > 50:
            return +20
        return -20

    def _score_balances(self, sei_native: float) -> int:
        if sei_native > 5_000:
            return +100
        if sei_native > 500:
            return +60
        if sei_native > 50:
            return +20
        return -30

    def _score_repayment(self, events: List[Dict[str, Any]]) -> int:
        borrows = len([e for e in events if e["type"] == "Borrow"])
        liquid = len([e for e in events if e["type"] == "Liquidation"])
        if borrows == 0:
            return 0
        ratio = liquid / borrows
        if ratio == 0:
            return +100
        if ratio < 0.10:
            return +60
        if ratio < 0.25:
            return 0
        return int(-150 * ratio)

    def _score_defi_extras(self, contracts_touched: int) -> int:
        if contracts_touched > 25:
            return +30
        if contracts_touched > 10:
            return +10
        return 0

    # ---------- public API ---------------------------------------------- #

    def calculate(self, wallet: str) -> CreditScore:
        wallet = Web3.to_checksum_address(wallet)

        # --- metadata & fast early cutoff ------------------------------- #
        first_ts, first_blk = self.provider.first_tx_info(wallet)
        counters = self.provider.counters(wallet)
        days_old = (
            (_dt.datetime.utcnow().replace(tzinfo=_dt.timezone.utc) - first_ts).days
            if first_ts
            else None
        )

        native_bal = get_wallet_balance(wallet)  # reuse working helper

        # For faster testing, use a more recent starting block if wallet has no history
        latest_block = self.provider.w3.eth.block_number
        if first_blk is None:
            # Start from ~7 days ago (assuming ~2s block time = 302,400 blocks per week)
            start_blk = max(0, latest_block - 302_400)
            print(f"   ➜ No transaction history found, scanning from recent block {start_blk}")
        else:
            start_blk = first_blk
            print(f"   ➜ Wallet first seen at block {start_blk}")

        lend_events = lending_history(wallet, self.pool, self.provider.w3, start_blk)

        # --- pillar scores ---------------------------------------------- #
        s_age = self._score_age(days_old)
        s_tx = self._score_transactions(counters.get("transaction_count", 0))
        s_bal = self._score_balances(native_bal)
        s_rep = self._score_repayment(lend_events)
        s_defi = self._score_defi_extras(len(counters.get("unique_addresses", [])))

        raw = (
            self.BASE
            + s_age * self.AGE_W
            + s_tx * self.TRANS_W
            + s_bal * self.BAL_W
            + s_rep * self.REPAY_W
            + s_defi * self.DEFI_W
        )
        final = max(0, min(1000, int(round(raw))))

        risk = (
            "Very Low Risk"
            if final >= 850
            else "Low Risk"
            if final >= 700
            else "Medium Risk"
            if final >= 500
            else "High Risk"
            if final >= 300
            else "Very High Risk"
        )

        return CreditScore(
            wallet=wallet,
            score=final,
            risk=risk,
            factors={
                "Account Age": s_age,
                "Tx Activity": s_tx,
                "Balances": s_bal,
                "Repayment": s_rep,
                "DeFi Extras": s_defi,
            },
        )


# --------------------------------------------------------------------------- #
# 5.  CLI
# --------------------------------------------------------------------------- #

if __name__ == "__main__":
    import argparse

    ap = argparse.ArgumentParser(description="Sei credit score")
    ap.add_argument("wallet", help="wallet address (0x…)")
    ap.add_argument(
        "--pool",
        default="0xA1b2C3d4E5f678901234567890abcdef12345678",
        help="lending-pool contract address",
    )
    ap.add_argument(
        "--recent-only",
        action="store_true",
        help="Only scan recent blocks (last week) for faster testing",
    )
    ns = ap.parse_args()

    scorer = DeFiCreditScorer(lending_pool_addr=ns.pool)
    result = scorer.calculate(ns.wallet)

    print(f"\nWallet: {result.wallet}")
    print(f"Score : {result.score}  ({result.risk})")
    print("Breakdown:")
    for name, pts in result.factors.items():
        print(f"  {name:<15} {pts:+}")
