#!/usr/bin/env python3
"""Allocate market-level Morpho bad debt to pre-incident suppliers.

Outputs machine-readable JSON files under data/:

- lender-bad-debt-by-lender-market.json
- lender-bad-debt-by-lender.json

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

from restitution_config import MARKETS, MORPHO, SNAPSHOT_BLOCK


getcontext().prec = 100


USDS_DECIMALS = Decimal(10) ** 18
MAX_WORKERS = int(os.environ.get("MAX_WORKERS", "4"))
RPC_RETRIES = int(os.environ.get("RPC_RETRIES", "6"))
TEST_MODE = os.environ.get("TEST_MODE", "0") == "1"
MARKET_LIMIT = int(os.environ.get("MARKET_LIMIT", "3" if TEST_MODE else "0"))
LENDER_LIMIT = int(os.environ.get("LENDER_LIMIT", "20" if TEST_MODE else "0"))
OUTPUT_PREFIX = os.environ.get("OUTPUT_PREFIX", "test-" if TEST_MODE else "")
USE_CACHED_LENDER_CANDIDATES = os.environ.get("USE_CACHED_LENDER_CANDIDATES", "0") == "1"
USE_CACHED_LENDER_POSITIONS = os.environ.get("USE_CACHED_LENDER_POSITIONS", "1") == "1"

# Morpho Blue events used to identify addresses that ever supplied/withdrew in a market.
# Supply(bytes32 indexed id,address indexed caller,address indexed onBehalf,uint256 assets,uint256 shares)
SUPPLY_TOPIC0 = "0xedf8870433c83823eb071d3df1caa8d008f12f6440918c20d75a3602cda30fe0"
# Withdraw(bytes32 indexed id,address indexed caller,address indexed onBehalf,address receiver,uint256 assets,uint256 shares)
WITHDRAW_TOPIC0 = "0xa56fc0ad5702ec05ce63666221f796fb62437c32db1aa1aa075fc6484cf58fbf"


def log(message: str) -> None:
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    print(f"[{now}] {message}", flush=True)


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
                raise RuntimeError(f"RPC error {code}: {message}")
            return result["result"]
        except (urllib.error.HTTPError, urllib.error.URLError, RuntimeError) as exc:
            retryable = "429" in str(exc) or "rate" in str(exc).lower() or "too many" in str(exc).lower() or "timeout" in str(exc).lower()
            if attempt == RPC_RETRIES or not retryable:
                raise
            delay = min(2**attempt, 30)
            log(f"RPC {method} retry {attempt}/{RPC_RETRIES} after {delay}s: {exc}")
            time.sleep(delay)
    raise RuntimeError(f"unreachable retry exhaustion for {method}")


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
        # Public/archive RPC endpoints can intermittently fail historical eth_call
        # requests with provider-specific messages that do not always include
        # obvious rate-limit keywords. Retry any non-zero cast exit here; a
        # genuinely permanent failure will still surface after RPC_RETRIES.
        if attempt == RPC_RETRIES:
            raise subprocess.CalledProcessError(proc.returncode, command, output=proc.stdout, stderr=proc.stderr)
        delay = min(2**attempt, 30)
        log(f"cast retry {attempt}/{RPC_RETRIES} after {delay}s: {' '.join(args[:4])}; {combined.strip()[:200]}")
        time.sleep(delay)
    raise RuntimeError("unreachable cast retry exhaustion")


def decimal_string(value: Decimal, places: int = 18) -> str:
    quant = Decimal(1).scaleb(-places)
    text = format(value.quantize(quant, rounding=ROUND_HALF_UP), "f")
    return text.rstrip("0").rstrip(".") if "." in text else text


def money_string(value: Decimal) -> str:
    return decimal_string(value, 2)


def topic_address(topic: str) -> str:
    return "0x" + topic[-40:]


def market_topic(market_id: str) -> str:
    return "0x" + market_id[2:].rjust(64, "0")


def get_logs_splitting(rpc_url: str, params: dict[str, Any], from_block: int, to_block: int) -> list[dict[str, Any]]:
    query = {**params, "fromBlock": hex(from_block), "toBlock": hex(to_block)}
    try:
        return rpc_call(rpc_url, "eth_getLogs", [query])
    except Exception as exc:
        message = str(exc).lower()
        splittable = from_block < to_block and (
            "too many" in message
            or "limit" in message
            or "more than" in message
            or "timeout" in message
            or "response size" in message
            or "query returned" in message
        )
        if not splittable:
            raise
        mid = (from_block + to_block) // 2
        return get_logs_splitting(rpc_url, params, from_block, mid) + get_logs_splitting(rpc_url, params, mid + 1, to_block)


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
    names = ["totalSupplyAssets", "totalSupplyShares", "totalBorrowAssets", "totalBorrowShares", "lastUpdate", "fee"]
    return {name: int(line.split()[0]) for name, line in zip(names, lines)}


def position_state(market_id: str, lender: str, rpc_url: str) -> dict[str, int]:
    lines = cast_call(
        [
            "call",
            MORPHO,
            "position(bytes32,address)(uint256,uint128,uint128)",
            market_id,
            lender,
        ],
        rpc_url,
        block=SNAPSHOT_BLOCK,
    )
    return {"supplyShares": int(lines[0].split()[0]), "borrowShares": int(lines[1].split()[0]), "collateral": int(lines[2].split()[0])}


def load_market_bad_debt() -> list[dict[str, Any]]:
    path = Path("data") / f"{OUTPUT_PREFIX}lender-bad-debt-by-market.json"
    if not path.exists() and OUTPUT_PREFIX:
        path = Path("data") / "lender-bad-debt-by-market.json"
    payload = json.loads(path.read_text(encoding="utf-8"))
    rows = [row for row in payload["rows"] if Decimal(row["badDebtUsds"]) > 0]
    if MARKET_LIMIT > 0:
        rows = rows[:MARKET_LIMIT]
    return rows


def load_cached_candidates() -> dict[str, list[str]] | None:
    path = Path("data") / f"{OUTPUT_PREFIX}lender-candidates-by-market.json"
    if not path.exists():
        return None
    payload = json.loads(path.read_text(encoding="utf-8"))
    return {row["marketId"]: row["candidateLenders"] for row in payload["rows"]}


def write_candidate_cache(rows: list[dict[str, Any]]) -> None:
    path = Path("data") / f"{OUTPUT_PREFIX}lender-candidates-by-market.json"
    path.write_text(json.dumps({"snapshotBlock": SNAPSHOT_BLOCK, "rows": rows}, indent=2) + "\n", encoding="utf-8")
    log(f"Wrote {path}")


def lender_positions_cache_path() -> Path:
    return Path("data") / f"{OUTPUT_PREFIX}lender-positive-positions-by-market.json"


def load_lender_positions_cache() -> dict[str, dict[str, Any]]:
    path = lender_positions_cache_path()
    if not USE_CACHED_LENDER_POSITIONS or not path.exists():
        return {}
    payload = json.loads(path.read_text(encoding="utf-8"))
    rows = {row["marketId"]: row for row in payload.get("rows", [])}
    log(f"Loaded cached positive lender positions for {len(rows)} markets from {path}")
    return rows


def write_lender_positions_cache(rows_by_market: dict[str, dict[str, Any]]) -> None:
    path = lender_positions_cache_path()
    rows = sorted(rows_by_market.values(), key=lambda row: Decimal(row["badDebtUsds"]), reverse=True)
    path.write_text(json.dumps({"snapshotBlock": SNAPSHOT_BLOCK, "rows": rows}, indent=2) + "\n", encoding="utf-8")
    log(f"Checkpointed positive lender positions for {len(rows)} markets to {path}")


def candidate_lenders_for_market(rpc_url: str, market_id: str) -> list[str]:
    params = {
        "address": MORPHO,
        "topics": [[SUPPLY_TOPIC0, WITHDRAW_TOPIC0], market_topic(market_id)],
    }
    logs = get_logs_splitting(rpc_url, params, 0, SNAPSHOT_BLOCK)
    candidates = sorted({topic_address(item["topics"][3]).lower() for item in logs if len(item.get("topics", [])) >= 4})
    log(f"Candidate suppliers {market_id[:10]}...: {len(candidates)} from {len(logs)} logs")
    return candidates


def main() -> None:
    rpc_url = os.environ.get("RPC_URL")
    if not rpc_url:
        raise SystemExit("Set RPC_URL to an archive-capable Ethereum mainnet endpoint")

    out_dir = Path("data")
    out_dir.mkdir(exist_ok=True)
    market_rows = load_market_bad_debt()
    log(
        "Starting lender allocation with "
        f"markets={len(market_rows)}, MAX_WORKERS={MAX_WORKERS}, TEST_MODE={TEST_MODE}, "
        f"LENDER_LIMIT={LENDER_LIMIT or 'none'}, OUTPUT_PREFIX='{OUTPUT_PREFIX}'"
    )

    cached = load_cached_candidates() if USE_CACHED_LENDER_CANDIDATES else None
    candidate_cache_rows: list[dict[str, Any]] = []
    candidates_by_market: dict[str, list[str]] = {}

    for row in market_rows:
        market_id = row["marketId"]
        if cached and market_id in cached:
            candidates = cached[market_id]
            log(f"Loaded cached candidate suppliers {market_id[:10]}...: {len(candidates)}")
        else:
            candidates = candidate_lenders_for_market(rpc_url, market_id)
        if LENDER_LIMIT > 0:
            candidates = candidates[:LENDER_LIMIT]
        candidates_by_market[market_id] = candidates
        candidate_cache_rows.append({"marketId": market_id, "collateral": row["collateral"], "lltv": row["lltv"], "candidateLenderCount": len(candidates), "candidateLenders": candidates})

    write_candidate_cache(candidate_cache_rows)

    lender_market_rows: list[dict[str, Any]] = []
    total_allocated = Decimal(0)
    positions_cache = load_lender_positions_cache()

    for market_index, market_row in enumerate(market_rows, start=1):
        market_id = market_row["marketId"]
        cfg = MARKETS[market_id]
        bad_debt = Decimal(market_row["badDebtUsds"])
        if market_id in positions_cache:
            cached_row = positions_cache[market_id]
            state = cached_row["marketState"]
            positive_positions = [(item["lender"], int(item["supplySharesRaw"])) for item in cached_row["positivePositions"]]
            log(
                f"Using cached lender positions for market {market_index}/{len(market_rows)} "
                f"{cfg.collateral} {cfg.lltv}: {len(positive_positions)} positive lenders"
            )
        else:
            state = market_state(market_id, rpc_url)
            candidates = candidates_by_market[market_id]
            log(f"Reading lender positions for market {market_index}/{len(market_rows)} {cfg.collateral} {cfg.lltv}: {len(candidates)} candidates")

            positive_positions: list[tuple[str, int]] = []
            completed = 0
            with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
                futures = {executor.submit(position_state, market_id, lender, rpc_url): lender for lender in candidates}
                for future in as_completed(futures):
                    lender = futures[future]
                    position = future.result()
                    completed += 1
                    supply_shares = position["supplyShares"]
                    if supply_shares > 0:
                        positive_positions.append((lender, supply_shares))
                    if completed == 1 or completed % 25 == 0 or completed == len(candidates):
                        log(f"  lender positions {completed}/{len(candidates)}")

            positions_cache[market_id] = {
                "marketId": market_id,
                "collateral": cfg.collateral,
                "lltv": cfg.lltv,
                "badDebtUsds": money_string(bad_debt),
                "marketState": state,
                "positiveLenderCount": len(positive_positions),
                "positivePositions": [
                    {"lender": lender, "supplySharesRaw": str(supply_shares)} for lender, supply_shares in sorted(positive_positions)
                ],
            }
            write_lender_positions_cache(positions_cache)

        total_supply_shares = Decimal(state["totalSupplyShares"])
        positive_supply_shares = sum(Decimal(shares) for _, shares in positive_positions)
        if total_supply_shares == 0:
            log(f"  WARNING market has zero totalSupplyShares at snapshot: {market_id}")
            continue
        if positive_supply_shares != total_supply_shares:
            diff_pct = (positive_supply_shares - total_supply_shares) / total_supply_shares * Decimal(100)
            log(f"  candidate positive supply shares coverage: {decimal_string(diff_pct, 6)}% vs market total")

        market_allocations: list[dict[str, Any]] = []
        for lender, supply_shares_int in positive_positions:
            supply_shares = Decimal(supply_shares_int)
            loss = bad_debt * supply_shares / total_supply_shares
            market_allocations.append(
                {
                    "lender": lender,
                    "marketId": market_id,
                    "collateral": cfg.collateral,
                    "lltv": cfg.lltv,
                    "snapshotBlock": SNAPSHOT_BLOCK,
                    "marketBadDebtUsds": money_string(bad_debt),
                    "lenderSupplySharesRaw": str(supply_shares_int),
                    "marketTotalSupplySharesRaw": str(state["totalSupplyShares"]),
                    "lenderSupplySharePct": decimal_string(supply_shares / total_supply_shares * Decimal(100), 8),
                    "lenderBadDebtUsdsRaw": decimal_string(loss),
                    "lenderBadDebtUsds": money_string(loss),
                }
            )

        # Make two-decimal per-lender rows sum exactly to the two-decimal market
        # bad-debt amount by distributing any cent-level rounding residual.
        rounded_sum = sum(Decimal(row["lenderBadDebtUsds"]) for row in market_allocations)
        residual_cents = int(((bad_debt - rounded_sum) * Decimal(100)).to_integral_value(rounding=ROUND_HALF_UP))
        if residual_cents > 0:
            market_allocations.sort(key=lambda row: Decimal(row["lenderBadDebtUsdsRaw"]) - Decimal(row["lenderBadDebtUsds"]), reverse=True)
            for row in market_allocations[:residual_cents]:
                row["lenderBadDebtUsds"] = money_string(Decimal(row["lenderBadDebtUsds"]) + Decimal("0.01"))
        elif residual_cents < 0:
            market_allocations.sort(key=lambda row: Decimal(row["lenderBadDebtUsds"]) - Decimal(row["lenderBadDebtUsdsRaw"]), reverse=True)
            for row in market_allocations[: abs(residual_cents)]:
                row["lenderBadDebtUsds"] = money_string(Decimal(row["lenderBadDebtUsds"]) - Decimal("0.01"))

        total_allocated += sum(Decimal(row["lenderBadDebtUsds"]) for row in market_allocations)
        lender_market_rows.extend(market_allocations)

    by_lender: dict[str, dict[str, Any]] = {}
    for row in lender_market_rows:
        lender = row["lender"]
        if lender not in by_lender:
            by_lender[lender] = {"lender": lender, "marketCount": set(), "lenderBadDebtUsds": Decimal(0)}
        by_lender[lender]["marketCount"].add(row["marketId"])
        by_lender[lender]["lenderBadDebtUsds"] += Decimal(row["lenderBadDebtUsds"])

    lender_rows = []
    for row in by_lender.values():
        lender_rows.append({"lender": row["lender"], "marketCount": len(row["marketCount"]), "lenderBadDebtUsds": money_string(row["lenderBadDebtUsds"])})

    lender_market_rows.sort(key=lambda r: Decimal(r["lenderBadDebtUsds"]), reverse=True)
    lender_rows.sort(key=lambda r: Decimal(r["lenderBadDebtUsds"]), reverse=True)

    summary = {
        "snapshotBlock": SNAPSHOT_BLOCK,
        "allocationBasis": "Pro rata by lender supplyShares at the pre-incident snapshot block.",
        "marketCount": len(market_rows),
        "lenderMarketCount": len(lender_market_rows),
        "lenderCount": len(lender_rows),
        "totalMarketBadDebtUsds": money_string(sum(Decimal(row["badDebtUsds"]) for row in market_rows)),
        "totalAllocatedBadDebtUsds": money_string(total_allocated),
    }

    outputs = {
        f"{OUTPUT_PREFIX}lender-bad-debt-by-lender-market.json": {"summary": summary, "rows": lender_market_rows},
        f"{OUTPUT_PREFIX}lender-bad-debt-by-lender.json": {"summary": summary, "rows": lender_rows},
    }
    for filename, payload in outputs.items():
        path = out_dir / filename
        path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        log(f"Wrote {path}")

    log("Completed lender allocation")
    print(json.dumps(summary, indent=2), flush=True)


if __name__ == "__main__":
    main()
