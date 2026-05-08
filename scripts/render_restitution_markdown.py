#!/usr/bin/env python3
"""Render restitution JSON outputs as markdown tables."""

from __future__ import annotations

import json
import os
from pathlib import Path


DATA = Path("data")
OUTPUT_PREFIX = os.environ.get("OUTPUT_PREFIX", "test-" if os.environ.get("TEST_MODE", "0") == "1" else "")


def load(name: str):
    return json.loads((DATA / f"{OUTPUT_PREFIX}{name}").read_text(encoding="utf-8"))


def exists(name: str) -> bool:
    return (DATA / f"{OUTPUT_PREFIX}{name}").exists()


def addr_link(addr: str) -> str:
    return f"[`{addr[:6]}...{addr[-4:]}`](https://etherscan.io/address/{addr})"


def tx_link(tx: str) -> str:
    return f"[`{tx[:6]}...{tx[-4:]}`](https://etherscan.io/tx/{tx})"


def market_link(market_id: str) -> str:
    return f"[`{market_id[:8]}...{market_id[-6:]}`](https://app.morpho.org/ethereum/market/{market_id})"


def money(value: str) -> str:
    return f"`{float(value):,.2f}`"


def pct(value: str) -> str:
    return f"`{float(value):,.2f}%`"


def render_borrower() -> None:
    if not exists("borrower-restitution-by-borrower.json"):
        return
    payload = load("borrower-restitution-by-borrower.json")
    lines = [
        "| Borrower | Markets | Events | Pre collateral USD | Pre borrow USDS | Pre borrow LTV | Seized value USD | Debt offset USDS | Net restitution USDS |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for row in payload["rows"]:
        lines.append(
            "| "
            + " | ".join(
                [
                    addr_link(row["borrower"]),
                    str(row["marketCount"]),
                    str(row["eventCount"]),
                    money(row["preIncidentCollateralUsd"]),
                    money(row["preIncidentBorrowUsds"]),
                    pct(row["preIncidentBorrowLtvPct"]),
                    money(row["seizedCollateralUsd"]),
                    money(row["debtClosedUsds"]),
                    money(row["borrowerRestitutionUsds"]),
                ]
            )
            + " |"
        )
    (DATA / f"{OUTPUT_PREFIX}borrower-restitution-by-borrower.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def render_borrower_market() -> None:
    if not exists("borrower-restitution-by-borrower-market.json"):
        return
    payload = load("borrower-restitution-by-borrower-market.json")
    lines = [
        "| Borrower | Collateral | LLTV | Market | Pre collateral | Pre borrow USDS | Pre borrow LTV | Events | Seized value USD | Debt offset USDS | Net restitution USDS | First tx |",
        "|---|---|---:|---|---:|---:|---:|---:|---:|---:|---:|---|",
    ]
    for row in payload["rows"]:
        lines.append(
            "| "
            + " | ".join(
                [
                    addr_link(row["borrower"]),
                    row["collateral"],
                    row["lltv"],
                    market_link(row["marketId"]),
                    f"`{float(row['preIncidentCollateralTokens']):,.6f}`",
                    money(row["preIncidentBorrowUsds"]),
                    pct(row["preIncidentBorrowLtvPct"]),
                    str(row["eventCount"]),
                    money(row["seizedCollateralUsd"]),
                    money(row["debtClosedUsds"]),
                    money(row["borrowerRestitutionUsds"]),
                    tx_link(row["firstTransactionHash"]),
                ]
            )
            + " |"
        )
    (DATA / f"{OUTPUT_PREFIX}borrower-restitution-by-borrower-market.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def render_bad_debt_market() -> None:
    if not exists("lender-bad-debt-by-market.json"):
        return
    payload = load("lender-bad-debt-by-market.json")
    lines = [
        "| Collateral | LLTV | Market | Events | Borrowers | Repaid USDS | Bad debt USDS | Debt closed USDS |",
        "|---|---:|---|---:|---:|---:|---:|---:|",
    ]
    for row in payload["rows"]:
        lines.append(
            "| "
            + " | ".join(
                [
                    row["collateral"],
                    row["lltv"],
                    market_link(row["marketId"]),
                    str(row["eventCount"]),
                    str(row["borrowerCount"]),
                    money(row["repaidUsds"]),
                    money(row["badDebtUsds"]),
                    money(row["debtClosedUsds"]),
                ]
            )
            + " |"
        )
    (DATA / f"{OUTPUT_PREFIX}lender-bad-debt-by-market.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def render_lender_market() -> None:
    if not exists("lender-bad-debt-by-lender-market.json"):
        return
    payload = load("lender-bad-debt-by-lender-market.json")
    lines = [
        "| Lender | Collateral | LLTV | Market | Supply share | Market bad debt USDS | Lender bad debt USDS |",
        "|---|---|---:|---|---:|---:|---:|",
    ]
    for row in payload["rows"]:
        lines.append(
            "| "
            + " | ".join(
                [
                    addr_link(row["lender"]),
                    row["collateral"],
                    row["lltv"],
                    market_link(row["marketId"]),
                    pct(row["lenderSupplySharePct"]),
                    money(row["marketBadDebtUsds"]),
                    money(row["lenderBadDebtUsds"]),
                ]
            )
            + " |"
        )
    (DATA / f"{OUTPUT_PREFIX}lender-bad-debt-by-lender-market.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def render_lender() -> None:
    if not exists("lender-bad-debt-by-lender.json"):
        return
    payload = load("lender-bad-debt-by-lender.json")
    lines = [
        "| Lender | Markets | Lender bad debt USDS |",
        "|---|---:|---:|",
    ]
    for row in payload["rows"]:
        lines.append(
            "| "
            + " | ".join(
                [
                    addr_link(row["lender"]),
                    str(row["marketCount"]),
                    money(row["lenderBadDebtUsds"]),
                ]
            )
            + " |"
        )
    (DATA / f"{OUTPUT_PREFIX}lender-bad-debt-by-lender.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    render_borrower()
    render_borrower_market()
    render_bad_debt_market()
    render_lender_market()
    render_lender()
    print(f"Wrote markdown restitution tables with OUTPUT_PREFIX='{OUTPUT_PREFIX}'")


if __name__ == "__main__":
    main()
