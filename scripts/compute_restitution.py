#!/usr/bin/env python3
"""Compute borrower restitution and market bad debt from Morpho liquidations.

Outputs machine-readable JSON files under data/:

- restitution-liquidation-events.json
- borrower-restitution-by-borrower-market.json
- borrower-restitution-by-borrower.json
- lender-bad-debt-by-market.json

Set RPC_URL to an archive-capable Ethereum mainnet endpoint. This script never
hard-codes private RPC credentials.
"""

from __future__ import annotations

import json
import os
import subprocess
import time
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from decimal import Decimal, ROUND_HALF_UP, getcontext
from pathlib import Path
from typing import Any

from restitution_config import END_BLOCK, LIQUIDATE_TOPIC0, MARKETS, MORPHO, SNAPSHOT_BLOCK, START_BLOCK, MarketConfig


getcontext().prec = 100


USDS_DECIMALS = Decimal(10) ** 18
MAX_WORKERS = int(os.environ.get("MAX_WORKERS", "8"))
RPC_RETRIES = int(os.environ.get("RPC_RETRIES", "6"))
TEST_MODE = os.environ.get("TEST_MODE", "0") == "1"
MARKET_LIMIT = int(os.environ.get("MARKET_LIMIT", "3" if TEST_MODE else "0"))
POSITION_LIMIT = int(os.environ.get("POSITION_LIMIT", "10" if TEST_MODE else "0"))
USE_CACHED_LOGS = os.environ.get("USE_CACHED_LOGS", "0") == "1"
OUTPUT_PREFIX = os.environ.get("OUTPUT_PREFIX", "test-" if TEST_MODE else "")

def rpc_call(rpc_url: str, method: str, params: list[Any]) -> Any:
    payload = json.dumps({"jsonrpc": "2.0", "id": 1, "method": method, "params": params}).encode()
    req = urllib.request.Request(rpc_url, data=payload, headers={"Content-Type": "application/json"})
    for attempt in range(1, RPC_RETRIES + 1):
        try:
            with urllib.request.urlopen(req, timeout=120) as resp:
                result = json.loads(resp.read().decode())
            if "error" in result:
                code = result["error"].get("code")
                message = result["error"].get("message", "")
                if code == 429 or "rate" in message.lower() or "too many" in message.lower():
                    raise RuntimeError(f"rate limited: {result['error']}")
                raise RuntimeError(f"RPC error for {method}: {result['error']}")
            return result["result"]
        except (urllib.error.HTTPError, urllib.error.URLError, RuntimeError) as exc:
            retryable = isinstance(exc, urllib.error.URLError) or "429" in str(exc) or "rate" in str(exc).lower() or "too many" in str(exc).lower()
            if attempt == RPC_RETRIES or not retryable:
                raise
            delay = min(2**attempt, 30)
            log(f"RPC {method} retry {attempt}/{RPC_RETRIES} after {delay}s: {exc}")
            time.sleep(delay)
    raise RuntimeError(f"unreachable retry exhaustion for {method}")


def log(message: str) -> None:
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    print(f"[{now}] {message}", flush=True)


def hex_int(value: str) -> int:
    return int(value, 16)


def topic_address(topic: str) -> str:
    return "0x" + topic[-40:]


def data_words(data: str) -> list[int]:
    body = data[2:] if data.startswith("0x") else data
    return [int(body[i : i + 64], 16) for i in range(0, len(body), 64) if body[i : i + 64]]


def dec(value: int, decimals: int) -> Decimal:
    return Decimal(value) / (Decimal(10) ** decimals)


def decimal_string(value: Decimal, places: int = 18) -> str:
    quant = Decimal(1).scaleb(-places)
    text = format(value.quantize(quant, rounding=ROUND_HALF_UP), "f")
    return text.rstrip("0").rstrip(".") if "." in text else text


def money_string(value: Decimal) -> str:
    return decimal_string(value, 2)


def cast_call(args: list[str], rpc_url: str, block: int | None = None) -> list[str]:
    command = ["cast", *args]
    if block is not None:
        command.extend(["--block", str(block)])
    command.extend(["--rpc-url", rpc_url])
    for attempt in range(1, RPC_RETRIES + 1):
        proc = subprocess.run(command, check=False, capture_output=True, text=True)
        if proc.returncode == 0:
            return [line.strip() for line in proc.stdout.splitlines() if line.strip()]
        combined = f"{proc.stdout}\n{proc.stderr}"
        retryable = "429" in combined or "rate" in combined.lower() or "too many" in combined.lower() or "timeout" in combined.lower()
        if attempt == RPC_RETRIES or not retryable:
            raise subprocess.CalledProcessError(proc.returncode, command, output=proc.stdout, stderr=proc.stderr)
        delay = min(2**attempt, 30)
        log(f"cast retry {attempt}/{RPC_RETRIES} after {delay}s: {' '.join(args[:4])}")
        time.sleep(delay)
    raise RuntimeError("unreachable cast retry exhaustion")


def market_params(market_id: str, rpc_url: str) -> dict[str, str]:
    lines = cast_call(
        [
            "call",
            MORPHO,
            "idToMarketParams(bytes32)(address,address,address,address,uint256)",
            market_id,
        ],
        rpc_url,
    )
    if len(lines) < 5:
        raise RuntimeError(f"Could not decode idToMarketParams for {market_id}: {lines}")
    return {
        "loanToken": lines[0],
        "collateralToken": lines[1],
        "oracle": lines[2],
        "irm": lines[3],
        "lltvRaw": lines[4].split()[0],
    }


def token_decimals(token: str, rpc_url: str) -> int:
    lines = cast_call(["call", token, "decimals()(uint8)"], rpc_url)
    return int(lines[0].split()[0])


def market_state(market_id: str, rpc_url: str) -> dict[str, int]:
    lines = cast_call(
        [
            "call",
            MORPHO,
            "market(bytes32)(uint128,uint128,uint128,uint128,uint128,uint128)",
            market_id,
        ],
        rpc_url,
        block=SNAPSHOT_BLOCK,
    )
    if len(lines) < 6:
        raise RuntimeError(f"Could not decode market state for {market_id}: {lines}")
    names = [
        "totalSupplyAssets",
        "totalSupplyShares",
        "totalBorrowAssets",
        "totalBorrowShares",
        "lastUpdate",
        "fee",
    ]
    return {name: int(line.split()[0]) for name, line in zip(names, lines)}


def position_state(market_id: str, borrower: str, rpc_url: str) -> dict[str, int]:
    lines = cast_call(
        [
            "call",
            MORPHO,
            "position(bytes32,address)(uint256,uint128,uint128)",
            market_id,
            borrower,
        ],
        rpc_url,
        block=SNAPSHOT_BLOCK,
    )
    if len(lines) < 3:
        raise RuntimeError(f"Could not decode position for {market_id}/{borrower}: {lines}")
    return {
        "supplyShares": int(lines[0].split()[0]),
        "borrowShares": int(lines[1].split()[0]),
        "collateral": int(lines[2].split()[0]),
    }


def load_prices() -> dict[str, Decimal]:
    path = Path("data") / f"restitution-price-snapshot-{SNAPSHOT_BLOCK}.json"
    payload = json.loads(path.read_text(encoding="utf-8"))
    return {item["feed"]: Decimal(item["usdPerToken"]) for item in payload["prices"]}


def get_liquidation_logs(rpc_url: str) -> list[dict[str, Any]]:
    return rpc_call(
        rpc_url,
        "eth_getLogs",
        [
            {
                "fromBlock": hex(START_BLOCK),
                "toBlock": hex(END_BLOCK),
                "address": MORPHO,
                "topics": [LIQUIDATE_TOPIC0],
            }
        ],
    )


def cached_liquidation_logs() -> list[dict[str, Any]] | None:
    path = Path("data") / "restitution-liquidation-events.json"
    if not path.exists():
        return None
    payload = json.loads(path.read_text(encoding="utf-8"))
    logs = []
    for event in payload.get("events", []):
        # Rebuild only the fields used downstream enough to avoid an eth_getLogs
        # call in test mode. This cache path is for script checks, not canonical
        # full recomputation.
        market_topic = "0x" + event["marketId"][2:].rjust(64, "0")
        caller_topic = "0x" + event["caller"][2:].rjust(64, "0")
        borrower_topic = "0x" + event["borrower"][2:].rjust(64, "0")
        words = [
            int(event["repaidAssetsRaw"]),
            int(event["repaidSharesRaw"]),
            int(event["seizedAssetsRaw"]),
            int(event["badDebtAssetsRaw"]),
            int(event["badDebtSharesRaw"]),
        ]
        logs.append(
            {
                "blockNumber": hex(event["blockNumber"]),
                "transactionIndex": hex(event["transactionIndex"]),
                "logIndex": hex(event["logIndex"]),
                "transactionHash": event["transactionHash"],
                "topics": [LIQUIDATE_TOPIC0, market_topic, caller_topic, borrower_topic],
                "data": "0x" + "".join(f"{word:064x}" for word in words),
            }
        )
    return logs


def main() -> None:
    rpc_url = os.environ.get("RPC_URL")
    if not rpc_url:
        raise SystemExit(
            "Set RPC_URL to an archive-capable Ethereum mainnet endpoint, e.g. "
            "RPC_URL=https://mainnet.infura.io/v3/<key> python scripts/compute_restitution.py"
        )
    out_dir = Path("data")
    out_dir.mkdir(exist_ok=True)
    prices = load_prices()

    selected_markets = dict(MARKETS)
    if MARKET_LIMIT > 0:
        selected_markets = dict(list(selected_markets.items())[:MARKET_LIMIT])

    log(
        "Starting restitution computation with "
        f"MAX_WORKERS={MAX_WORKERS}, TEST_MODE={TEST_MODE}, "
        f"MARKET_LIMIT={MARKET_LIMIT or 'none'}, POSITION_LIMIT={POSITION_LIMIT or 'none'}, "
        f"USE_CACHED_LOGS={USE_CACHED_LOGS}, OUTPUT_PREFIX='{OUTPUT_PREFIX}'"
    )
    log(f"Loading market params/state for {len(selected_markets)} markets")

    def load_market(item: tuple[str, MarketConfig]) -> tuple[str, dict[str, Any]]:
        market_id, cfg = item
        params = market_params(market_id, rpc_url)
        collateral_decimals = token_decimals(params["collateralToken"], rpc_url)
        state = market_state(market_id, rpc_url)
        return market_id, {
            **params,
            **state,
            "collateral": cfg.collateral,
            "lltv": cfg.lltv,
            "feed": cfg.feed,
            "collateralDecimals": collateral_decimals,
            "preIncidentUsdPerToken": decimal_string(prices[cfg.feed]),
        }

    params_by_market: dict[str, dict[str, Any]] = {}
    completed_markets = 0
    with ThreadPoolExecutor(max_workers=min(MAX_WORKERS, len(selected_markets))) as executor:
        futures = {executor.submit(load_market, item): item for item in selected_markets.items()}
        for future in as_completed(futures):
            market_id, params = future.result()
            params_by_market[market_id] = params
            completed_markets += 1
            log(
                f"Market setup {completed_markets}/{len(selected_markets)} "
                f"{params['collateral']} {params['lltv']}"
            )

    raw_logs = cached_liquidation_logs() if USE_CACHED_LOGS else None
    if raw_logs is not None:
        log(f"Loaded {len(raw_logs)} cached Liquidate logs from data/restitution-liquidation-events.json")
    else:
        log(f"Fetching Liquidate logs from block {START_BLOCK} to {END_BLOCK}")
        raw_logs = get_liquidation_logs(rpc_url)
    log(f"Fetched {len(raw_logs)} raw Liquidate logs; decoding affected markets")
    events: list[dict[str, Any]] = []

    for raw_log in raw_logs:
        block_number = hex_int(raw_log["blockNumber"])
        tx_index = hex_int(raw_log["transactionIndex"])
        if block_number == START_BLOCK and tx_index <= 1:
            continue

        market_id = raw_log["topics"][1].lower()
        if market_id not in selected_markets:
            continue

        words = data_words(raw_log["data"])
        if len(words) != 5:
            raise RuntimeError(f"Unexpected Liquidate data word count: {len(words)} in {raw_log['transactionHash']}")

        repaid_assets, repaid_shares, seized_assets, bad_debt_assets, bad_debt_shares = words
        cfg = selected_markets[market_id]
        params = params_by_market[market_id]
        price = prices[cfg.feed]
        collateral_decimals = int(params["collateralDecimals"])

        seized_tokens = dec(seized_assets, collateral_decimals)
        seized_usd = seized_tokens * price
        repaid_usds = Decimal(repaid_assets) / USDS_DECIMALS
        bad_debt_usds = Decimal(bad_debt_assets) / USDS_DECIMALS
        debt_closed_usds = repaid_usds + bad_debt_usds
        restitution = seized_usd - debt_closed_usds
        if restitution < 0:
            restitution = Decimal(0)

        events.append(
            {
                "blockNumber": block_number,
                "transactionIndex": tx_index,
                "logIndex": hex_int(raw_log["logIndex"]),
                "transactionHash": raw_log["transactionHash"],
                "marketId": market_id,
                "borrower": topic_address(raw_log["topics"][3]),
                "caller": topic_address(raw_log["topics"][2]),
                "collateral": cfg.collateral,
                "lltv": cfg.lltv,
                "feed": cfg.feed,
                "collateralToken": params["collateralToken"],
                "collateralDecimals": collateral_decimals,
                "preIncidentUsdPerToken": decimal_string(price),
                "repaidAssetsRaw": str(repaid_assets),
                "repaidSharesRaw": str(repaid_shares),
                "seizedAssetsRaw": str(seized_assets),
                "badDebtAssetsRaw": str(bad_debt_assets),
                "badDebtSharesRaw": str(bad_debt_shares),
                "seizedCollateralTokens": decimal_string(seized_tokens),
                "seizedCollateralUsd": money_string(seized_usd),
                "repaidUsds": money_string(repaid_usds),
                "badDebtUsds": money_string(bad_debt_usds),
                "debtClosedUsds": money_string(debt_closed_usds),
                "borrowerRestitutionUsds": money_string(restitution),
            }
        )

    log(f"Decoded {len(events)} affected liquidation events")

    if POSITION_LIMIT > 0:
        ordered_pairs = []
        seen_pairs = set()
        for event in events:
            pair = (event["borrower"], event["marketId"])
            if pair not in seen_pairs:
                seen_pairs.add(pair)
                ordered_pairs.append(pair)
        allowed = set(ordered_pairs[:POSITION_LIMIT])
        events = [event for event in events if (event["borrower"], event["marketId"]) in allowed]
        log(f"POSITION_LIMIT active: reduced to {len(allowed)} borrower-market rows and {len(events)} events")

    by_borrower_market: dict[tuple[str, str], dict[str, Any]] = {}
    by_borrower: dict[str, dict[str, Any]] = {}
    by_market: dict[str, dict[str, Any]] = {}

    for event in events:
        market_id = event["marketId"]
        borrower = event["borrower"]
        key = (borrower, market_id)
        if key not in by_borrower_market:
            by_borrower_market[key] = {
                "borrower": borrower,
                "marketId": market_id,
                "collateral": event["collateral"],
                "lltv": event["lltv"],
                "eventCount": 0,
                "firstTransactionHash": event["transactionHash"],
                "firstBlockNumber": event["blockNumber"],
                "seizedCollateralTokens": Decimal(0),
                "seizedCollateralUsd": Decimal(0),
                "repaidUsds": Decimal(0),
                "badDebtUsds": Decimal(0),
                "debtClosedUsds": Decimal(0),
                "borrowerRestitutionUsds": Decimal(0),
            }
        row = by_borrower_market[key]
        row["eventCount"] += 1
        row["seizedCollateralTokens"] += Decimal(event["seizedCollateralTokens"])
        row["seizedCollateralUsd"] += Decimal(event["seizedCollateralUsd"])
        row["repaidUsds"] += Decimal(event["repaidUsds"])
        row["badDebtUsds"] += Decimal(event["badDebtUsds"])
        row["debtClosedUsds"] += Decimal(event["debtClosedUsds"])
        row["borrowerRestitutionUsds"] += Decimal(event["borrowerRestitutionUsds"])

        if borrower not in by_borrower:
            by_borrower[borrower] = {
                "borrower": borrower,
                "marketCount": set(),
                "eventCount": 0,
                "seizedCollateralUsd": Decimal(0),
                "repaidUsds": Decimal(0),
                "badDebtUsds": Decimal(0),
                "debtClosedUsds": Decimal(0),
                "borrowerRestitutionUsds": Decimal(0),
            }
        brow = by_borrower[borrower]
        brow["marketCount"].add(market_id)
        brow["eventCount"] += 1
        brow["seizedCollateralUsd"] += Decimal(event["seizedCollateralUsd"])
        brow["repaidUsds"] += Decimal(event["repaidUsds"])
        brow["badDebtUsds"] += Decimal(event["badDebtUsds"])
        brow["debtClosedUsds"] += Decimal(event["debtClosedUsds"])
        brow["borrowerRestitutionUsds"] += Decimal(event["borrowerRestitutionUsds"])

        if market_id not in by_market:
            by_market[market_id] = {
                "marketId": market_id,
                "collateral": event["collateral"],
                "lltv": event["lltv"],
                "eventCount": 0,
                "borrowerCount": set(),
                "repaidUsds": Decimal(0),
                "badDebtUsds": Decimal(0),
                "debtClosedUsds": Decimal(0),
            }
        mrow = by_market[market_id]
        mrow["eventCount"] += 1
        mrow["borrowerCount"].add(borrower)
        mrow["repaidUsds"] += Decimal(event["repaidUsds"])
        mrow["badDebtUsds"] += Decimal(event["badDebtUsds"])
        mrow["debtClosedUsds"] += Decimal(event["debtClosedUsds"])

    log(f"Reading {len(by_borrower_market)} pre-incident borrower positions at block {SNAPSHOT_BLOCK}")

    def enrich_position(item: tuple[tuple[str, str], dict[str, Any]]) -> tuple[tuple[str, str], dict[str, Any]]:
        (borrower, market_id), row = item
        params = params_by_market[market_id]
        cfg = selected_markets[market_id]
        position = position_state(market_id, borrower, rpc_url)
        price = prices[cfg.feed]
        collateral_decimals = int(params["collateralDecimals"])
        pre_collateral_tokens = dec(position["collateral"], collateral_decimals)
        pre_collateral_usd = pre_collateral_tokens * price

        total_borrow_shares = Decimal(params["totalBorrowShares"])
        if total_borrow_shares == 0:
            pre_borrow_usds = Decimal(0)
        else:
            pre_borrow_assets = Decimal(position["borrowShares"]) * Decimal(params["totalBorrowAssets"]) / total_borrow_shares
            pre_borrow_usds = pre_borrow_assets / USDS_DECIMALS

        if pre_collateral_usd == 0:
            pre_borrow_ltv = Decimal(0)
        else:
            pre_borrow_ltv = pre_borrow_usds / pre_collateral_usd * Decimal(100)

        row["preIncidentCollateralTokens"] = pre_collateral_tokens
        row["preIncidentCollateralUsd"] = pre_collateral_usd
        row["preIncidentBorrowUsds"] = pre_borrow_usds
        row["preIncidentBorrowLtvPct"] = pre_borrow_ltv
        row["preIncidentBorrowSharesRaw"] = str(position["borrowShares"])
        row["preIncidentCollateralRaw"] = str(position["collateral"])
        return (borrower, market_id), row

    enriched_rows: dict[tuple[str, str], dict[str, Any]] = {}
    completed = 0
    total_positions = len(by_borrower_market)
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = [executor.submit(enrich_position, item) for item in by_borrower_market.items()]
        for future in as_completed(futures):
            key, row = future.result()
            enriched_rows[key] = row
            completed += 1
            if completed == 1 or completed % 10 == 0 or completed == total_positions:
                log(f"Position snapshots {completed}/{total_positions}")

    by_borrower_market = enriched_rows

    for row in by_borrower_market.values():
        brow = by_borrower[row["borrower"]]
        brow.setdefault("preIncidentCollateralUsd", Decimal(0))
        brow.setdefault("preIncidentBorrowUsds", Decimal(0))
        brow["preIncidentCollateralUsd"] += row["preIncidentCollateralUsd"]
        brow["preIncidentBorrowUsds"] += row["preIncidentBorrowUsds"]

    for brow in by_borrower.values():
        pre_collateral_usd = brow.get("preIncidentCollateralUsd", Decimal(0))
        pre_borrow_usds = brow.get("preIncidentBorrowUsds", Decimal(0))
        brow["preIncidentBorrowLtvPct"] = Decimal(0) if pre_collateral_usd == 0 else pre_borrow_usds / pre_collateral_usd * Decimal(100)

    def stringify_row(row: dict[str, Any]) -> dict[str, Any]:
        out: dict[str, Any] = {}
        for k, v in row.items():
            if isinstance(v, Decimal):
                if k.endswith("Usd") or k.endswith("Usds"):
                    out[k] = money_string(v)
                elif k.endswith("Pct"):
                    out[k] = decimal_string(v, 4)
                else:
                    out[k] = decimal_string(v)
            elif isinstance(v, set):
                out[k] = len(v)
            else:
                out[k] = v
        return out

    borrower_market_rows = [stringify_row(v) for v in by_borrower_market.values()]
    borrower_market_rows.sort(key=lambda r: Decimal(r["borrowerRestitutionUsds"]), reverse=True)

    borrower_rows = [stringify_row(v) for v in by_borrower.values()]
    borrower_rows.sort(key=lambda r: Decimal(r["borrowerRestitutionUsds"]), reverse=True)

    market_rows = [stringify_row(v) for v in by_market.values()]
    market_rows.sort(key=lambda r: Decimal(r["badDebtUsds"]), reverse=True)

    summary = {
        "snapshotBlock": SNAPSHOT_BLOCK,
        "liquidationWindow": {"fromBlock": START_BLOCK, "toBlock": END_BLOCK},
        "eventCount": len(events),
        "borrowerCount": len(by_borrower),
        "borrowerMarketCount": len(by_borrower_market),
        "marketCount": len(by_market),
        "totalBorrowerRestitutionUsds": money_string(sum(Decimal(e["borrowerRestitutionUsds"]) for e in events)),
        "totalBadDebtUsds": money_string(sum(Decimal(e["badDebtUsds"]) for e in events)),
        "totalRepaidUsds": money_string(sum(Decimal(e["repaidUsds"]) for e in events)),
        "totalSeizedCollateralUsd": money_string(sum(Decimal(e["seizedCollateralUsd"]) for e in events)),
    }

    files = {
        f"{OUTPUT_PREFIX}restitution-liquidation-events.json": {"summary": summary, "events": events},
        f"{OUTPUT_PREFIX}borrower-restitution-by-borrower-market.json": {"summary": summary, "rows": borrower_market_rows},
        f"{OUTPUT_PREFIX}borrower-restitution-by-borrower.json": {"summary": summary, "rows": borrower_rows},
        f"{OUTPUT_PREFIX}lender-bad-debt-by-market.json": {"summary": summary, "rows": market_rows},
    }
    for filename, payload in files.items():
        (out_dir / filename).write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        log(f"Wrote {out_dir / filename}")

    log("Completed restitution computation")
    print(json.dumps(summary, indent=2), flush=True)


if __name__ == "__main__":
    main()
