# Restitution Technical Methodology

Technical reproduction notes for the generated restitution data used by [`suggested-restitution-plan.md`](suggested-restitution-plan.md).

## Snapshot and Window

| Item | Value |
|---|---:|
| Pre-incident snapshot block | `25030091` |
| DIA scale-change block | `25030092` |
| Liquidation window start | block `25030092`, after transaction index `1` |
| Liquidation window end | block `25030776` |
| Apparent correction block | `25030777` |

The snapshot block is the block immediately before the DIA scale-change transaction.

## Pre-Incident Price Snapshot

Prices are read from the DIA oracle contract [`0xE1A3d58dc6C516Ef18628ce7E13cfE44B4Ac1552`](https://etherscan.io/address/0xE1A3d58dc6C516Ef18628ce7E13cfE44B4Ac1552) with `getValue(string)` at block `25030091`.

Normalization:

```text
USD/USDS per token = DIA raw value / 1e12
```

| Collateral | DIA feed | DIA raw value | USD/USDS per token |
|---|---|---:|---:|
| PEPE | `PEPE/USD` | `4090714` | `0.000004090714` |
| JOE | `JOE/USD` | `13213510296` | `0.013213510296` |
| SPX | `SPX/USD` | `401176412005` | `0.401176412005` |
| MOG | `MOG/USD` | `158148` | `0.000000158148` |
| SHIB | `SHIB/USD` | `6263091` | `0.000006263091` |
| NEIRO | `NEIRO/USD` | `99938041` | `0.000099938041` |
| IMF | `IMF/USD` | `17403738629` | `0.017403738629` |
| NPC | `NPC/USD` | `7601983559` | `0.007601983559` |
| REKT | `REKT/USD` | `150991` | `0.000000150991` |
| APU | `APU/USD` | `30297690` | `0.00003029769` |
| CULT | `CULT/USD` | `198464876` | `0.000198464876` |
| BITCOIN | `BITCOIN/USD` | `21968841306` | `0.021968841306` |
| cbBTC | `cbBTC/USD` | `81411019677641216` | `81411.019677641216` |
| BOBO | `BOBO/USD` | `92474` | `0.000000092474` |

Machine-readable source data: [`data/restitution-price-snapshot-25030091.json`](data/restitution-price-snapshot-25030091.json).

## Borrower Restitution Formula

The borrower-side calculation compensates lost borrower equity, not full collateral value.

For each affected Morpho `Liquidate` event:

```text
net borrower restitution = fairValue(seizedCollateral) - debtClosedInLiquidation

where:
fairValue(seizedCollateral) = seizedAssets * preIncidentCollateralPrice
debtClosedInLiquidation = repaidAssets + badDebtAssets
```

Negative event-level values, if any, are floored at zero before aggregation.

For context and validation, the generation script also reads each borrower-market Morpho position at block `25030091` and computes:

- pre-incident collateral amount/value
- pre-incident borrow amount in USDS
- pre-incident borrow LTV

## Lender Bad-Debt Formula

The base lender-side table is market-level:

```text
market bad debt = sum(badDebtAssets) across incident Liquidate events
```

The per-lender allocation reconstructs candidate suppliers from Morpho `Supply` and `Withdraw` logs for each bad-debt market before block `25030091`, reads each candidate's `position(marketId, lender)` at block `25030091`, keeps candidates with positive `supplyShares`, and allocates market bad debt pro rata:

```text
lender bad debt = market bad debt * lender supplyShares / market totalSupplyShares
```

This uses the pre-incident snapshot as the allocation basis. It allocates the incident-window market bad debt to lenders who held supply shares at the snapshot, regardless of later supply changes during the incident window.

## Generated Totals

Using the block `25030091` price snapshot and event-level borrower formula:

| Metric | Value |
|---|---:|
| Liquidation events | `186` |
| Unique borrowers | `141` |
| Borrower-market rows | `169` |
| Markets | `26` |
| Fair value of seized collateral at block `25030091` prices | `$1,733,173.70` |
| USDS repaid by liquidators | `157.88 USDS` |
| Morpho bad debt | `654,573.91 USDS` |
| Borrower net restitution, event-level formula | `1,078,482.67 USDS` |
| Per-lender allocation rows | `141` |
| Unique snapshot lenders receiving bad-debt allocation | `37` |
| Total allocated lender bad debt | `654,573.91 USDS` |

These totals differ slightly from earlier estimates that used average pre-update/restoration prices. This methodology uses a single pre-incident block price snapshot.

## Generated Files

Canonical generated files:

- [`data/restitution-price-snapshot-25030091.json`](data/restitution-price-snapshot-25030091.json)
- [`data/restitution-price-snapshot-25030091.md`](data/restitution-price-snapshot-25030091.md)
- [`data/restitution-liquidation-events.json`](data/restitution-liquidation-events.json)
- [`data/borrower-restitution-by-borrower-market.json`](data/borrower-restitution-by-borrower-market.json)
- [`data/borrower-restitution-by-borrower-market.md`](data/borrower-restitution-by-borrower-market.md)
- [`data/borrower-restitution-by-borrower.json`](data/borrower-restitution-by-borrower.json)
- [`data/borrower-restitution-by-borrower.md`](data/borrower-restitution-by-borrower.md)
- [`data/lender-bad-debt-by-market.json`](data/lender-bad-debt-by-market.json)
- [`data/lender-bad-debt-by-market.md`](data/lender-bad-debt-by-market.md)
- [`data/lender-bad-debt-by-lender-market.json`](data/lender-bad-debt-by-lender-market.json)
- [`data/lender-bad-debt-by-lender-market.md`](data/lender-bad-debt-by-lender-market.md)
- [`data/lender-bad-debt-by-lender.json`](data/lender-bad-debt-by-lender.json)
- [`data/lender-bad-debt-by-lender.md`](data/lender-bad-debt-by-lender.md)

The lender allocation script can also create non-canonical cache/checkpoint files, including `data/lender-candidates-by-market.json` and `data/lender-positive-positions-by-market.json`. These are intentionally omitted from the canonical data set because they can be reproduced from an archive-capable Ethereum RPC endpoint.

## Regeneration Commands

Use an archive-capable Ethereum mainnet RPC endpoint.

Regenerate the price snapshot:

```bash
RPC_URL=https://mainnet.infura.io/v3/<key> python scripts/restitution_price_snapshot.py
```

Regenerate canonical restitution JSON and markdown tables:

```bash
RPC_URL=https://mainnet.infura.io/v3/<key> python scripts/compute_restitution.py
RPC_URL=https://mainnet.infura.io/v3/<key> python scripts/compute_lender_allocations.py
python scripts/render_restitution_markdown.py
```

For cheap script checks while iterating, use test mode and cached logs when available:

```bash
RPC_URL=https://mainnet.infura.io/v3/<key> TEST_MODE=1 USE_CACHED_LOGS=1 python scripts/compute_restitution.py
RPC_URL=https://mainnet.infura.io/v3/<key> TEST_MODE=1 USE_CACHED_LENDER_CANDIDATES=1 python scripts/compute_lender_allocations.py
TEST_MODE=1 python scripts/render_restitution_markdown.py
```

`TEST_MODE=1` defaults to the first `3` markets, first `10` borrower-market position snapshots, and first `20` lender candidates. The caps can be overridden with `MARKET_LIMIT=<n>`, `POSITION_LIMIT=<n>`, and `LENDER_LIMIT=<n>`. `MAX_WORKERS=<n>` controls RPC concurrency.

In test mode, outputs are prefixed with `test-` by default so canonical full-run JSON files are not overwritten. Override with `OUTPUT_PREFIX=<prefix>` if needed.

## Caveats and Open Items

- USDS values are treated as USD-equivalent for restitution accounting.
- Borrower values use the single block `25030091` DIA price snapshot.
- Event-level net restitution is floored at zero before aggregation.
- Per-lender bad-debt allocation assumes snapshot supply shares at block `25030091` are the intended allocation basis.
- Supplier candidate reconstruction uses Morpho supply/withdraw event history before the snapshot block; generated output should be reviewed for any markets where positive candidate supply shares do not cover market `totalSupplyShares`.
- Per-row lender allocation tables are rounded to two decimals for Markdown display; cent-level residuals are distributed per market so displayed lender rows sum to displayed market bad debt.
