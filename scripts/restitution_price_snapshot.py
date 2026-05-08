#!/usr/bin/env python3
"""Capture pre-incident DIA prices for restitution calculations.

This script intentionally does not hard-code private RPC credentials. Set RPC_URL
to an archive-capable Ethereum mainnet endpoint, for example:

  RPC_URL=https://mainnet.infura.io/v3/<key> python scripts/restitution_price_snapshot.py

It uses `cast call` so ABI encoding/decoding stays aligned with the rest of this
repository's verification workflow.
"""

from __future__ import annotations

import json
import os
import re
import subprocess
from decimal import Decimal, getcontext
from pathlib import Path

from restitution_config import DIA_ORACLE, PRICE_FEEDS, SNAPSHOT_BLOCK


getcontext().prec = 80


DEFAULT_RPC_URL = "https://ethereum-rpc.publicnode.com"
RAW_PRICE_DECIMALS = Decimal(10) ** 12


def decimal_string(value: Decimal, places: int = 18) -> str:
    text = format(value, f".{places}f")
    return text.rstrip("0").rstrip(".") if "." in text else text


def cast_get_value(feed: str, rpc_url: str) -> tuple[int, int]:
    proc = subprocess.run(
        [
            "cast",
            "call",
            DIA_ORACLE,
            "getValue(string)(uint128,uint128)",
            feed,
            "--block",
            str(SNAPSHOT_BLOCK),
            "--rpc-url",
            rpc_url,
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    # cast prints each decoded return on its own line, often followed by a
    # scientific notation helper in brackets. Keep the leading integer only.
    ints = []
    for line in proc.stdout.splitlines():
        match = re.match(r"^\s*(\d+)", line)
        if match:
            ints.append(int(match.group(1)))
    if len(ints) < 2:
        raise RuntimeError(f"Could not parse cast output for {feed}: {proc.stdout!r}")
    return ints[0], ints[1]


def main() -> None:
    rpc_url = os.environ.get("RPC_URL", DEFAULT_RPC_URL)
    out_dir = Path("data")
    out_dir.mkdir(exist_ok=True)

    prices = []
    for cfg in PRICE_FEEDS:
        raw_value, dia_timestamp = cast_get_value(cfg.feed, rpc_url)
        usd_per_token = Decimal(raw_value) / RAW_PRICE_DECIMALS
        prices.append(
            {
                "collateral": cfg.collateral,
                "feed": cfg.feed,
                "snapshotBlock": SNAPSHOT_BLOCK,
                "diaRawValue": str(raw_value),
                "diaTimestamp": dia_timestamp,
                "normalization": "diaRawValue / 1e12",
                "usdPerToken": decimal_string(usd_per_token),
            }
        )

    payload = {
        "snapshotBlock": SNAPSHOT_BLOCK,
        "diaOracle": DIA_ORACLE,
        "normalization": "USD per token = DIA raw value / 1e12",
        "prices": prices,
    }

    json_path = out_dir / f"restitution-price-snapshot-{SNAPSHOT_BLOCK}.json"
    json_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")

    md_path = out_dir / f"restitution-price-snapshot-{SNAPSHOT_BLOCK}.md"
    lines = [
        "| Collateral | DIA feed | DIA raw value | USD/USDS per token |",
        "|---|---|---:|---:|",
    ]
    for item in prices:
        lines.append(
            f"| {item['collateral']} | `{item['feed']}` | `{item['diaRawValue']}` | `{item['usdPerToken']}` |"
        )
    md_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"Wrote {json_path}")
    print(f"Wrote {md_path}")


if __name__ == "__main__":
    main()
