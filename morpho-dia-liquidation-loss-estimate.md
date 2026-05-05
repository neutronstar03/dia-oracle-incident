# Appendix B: Liquidation Loss and Liquidator Extraction Estimate

Supporting estimate for the [DIA Oracle Scale Incident Documentation](README.md). This appendix quantifies liquidation amounts, bad debt, seized collateral value, and liquidator concentration across the affected Morpho USDS markets.

## Contents

- [Scope](#scope)
- [Methodology](#methodology)
- [Aggregate results](#aggregate-results)
- [Liquidator count](#liquidator-count)
- [Key ratios](#key-ratios)
- [Per-market results](#per-market-results)
- [Important caveats](#important-caveats)
- [Conclusion](#conclusion)

## Scope

This estimates the liquidation amounts and liquidator extraction for the DIA oracle incident affecting Morpho USDS markets.

DIA scale-change update:

[`0x738f860b6ed20d60fc968ac53783387732a559b9e21ebdd0bfe5da4c6d09574c`](https://etherscan.io/tx/0x738f860b6ed20d60fc968ac53783387732a559b9e21ebdd0bfe5da4c6d09574c)

- Block / transaction index: `25030092 / 1`

Apparent correction/restoration update:

[`0x06124fbc8da5a46c34b1ce43a22a82f3a3eef166428482ae99366b1f11a4889b`](https://etherscan.io/tx/0x06124fbc8da5a46c34b1ce43a22a82f3a3eef166428482ae99366b1f11a4889b)

- Block / transaction index: `25030777 / 163`

These block and transaction-index values are confirmed from transaction metadata and DIA `OracleUpdate(string,uint128,uint128)` logs.

Liquidation window analyzed:

```text
from block 25030092, transactionIndex > 1, through block 25030776
```

This starts immediately after the DIA scale-change update at block `25030092`, transaction index `1`, and ends immediately before the apparent correction at block `25030777`. The first observed liquidation was in the same block as the DIA update, at transaction index `2`; the previous window started at block `25030093` and missed that PEPE liquidation.

A later BOBO scale-change update occurred inside the same window at block `25030121`, transaction index `222`. BOBO is therefore tracked separately from the original batch transaction.

## Methodology

For each affected Morpho market, Morpho `Liquidate` events were decoded:

```text
Liquidate(
  bytes32 indexed id,
  address indexed caller,
  address indexed borrower,
  uint256 repaidAssets,
  uint256 repaidShares,
  uint256 seizedAssets,
  uint256 badDebtAssets,
  uint256 badDebtShares
)
```

Because all decoded liquidations in this window use USDS as the loan asset:

- `repaidAssets` = USDS actually repaid by liquidators.
- `badDebtAssets` = USDS bad debt recorded by Morpho.
- `seizedAssets` = collateral tokens seized by liquidators.

For seized collateral fair value in the original batch markets, this estimate uses the average of:

1. the last normal DIA price before the scale-change update, and
2. the corrected DIA price after restoration.

For these meme-token DIA feeds, this estimate uses:

```text
fair USD/token = DIA raw value / 1e12
```

This normalization is supported by DIA's CDR #094 configuration post, which states that `getValue(key)` returns the most recent USD price and gives `MOG/USD` as an example with 12 decimal places.

Reference: [DIA CDR #094: International Meme Fund token price feed](https://forum.diadata.org/t/cdr-094-international-meme-fund-token-price-feed/1028/6)

This is an estimate, but the event-level USDS repaid, bad debt, and seized token amounts are exact on-chain values.

## Aggregate Results

Across the full Morpho `Liquidate` log audit for the window:

```text
Unique liquidation transactions: 155
Liquidation events: 186
Unique borrowers: 141
Unique liquidator callers: 6
```

All `186` events are USDS loan markets. The original meme-token valuation table below accounts for `181` events. The remaining `5` events are `2` cbBTC-collateral events from the initial DIA batch and `3` BOBO-collateral events after the later BOBO update; these extra events recorded approximately zero bad debt.

Estimated totals:

| Metric | Estimate |
|---|---:|
| USDS actually repaid by liquidators, all 186 events | `157.93 USDS` |
| USDS bad debt recorded, all 186 events | `654,573.81 USDS` |
| Total USDS debt closed / affected, all 186 events | `654,731.74 USDS` |
| Fair value of seized collateral | `$1,707,958.14` |
| Gross liquidator extraction | `$1,707,800.25` |
| Estimated gas paid by original liquidation txs | `$77.26` |
| Net liquidator extraction after known gas | `$1,707,722.99` |

The fair-value and extraction totals above are the original meme-token valuation totals. The cbBTC events add about `$93` of seized-collateral value using the average of pre-update and restored cbBTC DIA prices. The BOBO events add about `$385` using the pre-update BOBO DIA value, but BOBO did not have a matching restoration update in the block `25030777` batch, so it is kept separate from the main fair-value estimate.

The revised totals include this same-block PEPE 77% liquidation:

| Field | Value |
|---|---|
| Transaction | [`0x2cf791f6...52e8`](https://etherscan.io/tx/0x2cf791f65e96359acc6e955bdec3d4504886339f85b05f52db85d61d481052e8) |
| Block / transaction index | `25030092 / 2` |
| Morpho market | [`0x5ffdf15c5a4d7c6affb3f12634eeda1a20e60b92c0eb547f61754f656b55841e`](https://app.morpho.org/ethereum/market/0x5ffdf15c5a4d7c6affb3f12634eeda1a20e60b92c0eb547f61754f656b55841e) |
| Repaid assets | `53.461622 USDS` |
| Bad debt assets | `301,610.036656 USDS` |
| Seized assets | `141,438,101,701.052464 PEPE` |
| Fair PEPE price used | `$0.000004090056` |
| Fair seized collateral | `$578,489.76` |
| Gross extraction | `$578,436.29` |

## Liquidator Count

The liquidations were not all performed by one address.

Across the same window:

```text
186 liquidation events
155 unique liquidation transactions
141 unique borrowers
6 unique Morpho Liquidate callers / liquidator addresses
```

Liquidator caller breakdown:

| Liquidator caller | Events | Unique txs | Markets touched | Share of events |
|---|---:|---:|---:|---:|
| [`0xad213ae0b710c7bc6c915984d91bad008b2d3221`](https://etherscan.io/address/0xad213ae0b710c7bc6c915984d91bad008b2d3221) | 88 | 88 | 17 | `~47.3%` |
| [`0x36331e299247e5d0d3261e1d9852f6e0cffee95c`](https://etherscan.io/address/0x36331e299247e5d0d3261e1d9852f6e0cffee95c) | 62 | 62 | 23 | `~33.3%` |
| [`0xaba996f3f6170a85a31d7f8f4b54816e141278f8`](https://etherscan.io/address/0xaba996f3f6170a85a31d7f8f4b54816e141278f8) | 33 | 2 | 2 | `~17.7%` |
| [`0xbd32122bad41a09f2405bb374a83877d8245079c`](https://etherscan.io/address/0xbd32122bad41a09f2405bb374a83877d8245079c) | 1 | 1 | 1 | `~0.5%` |
| [`0x211f4039d132f2cc22f656330c315e52a576c0bc`](https://etherscan.io/address/0x211f4039d132f2cc22f656330c315e52a576c0bc) | 1 | 1 | 1 | `~0.5%` |
| [`0xe08d97e151473a848c3d9ca3f323cb720472d015`](https://etherscan.io/address/0xe08d97e151473a848c3d9ca3f323cb720472d015) | 1 | 1 | 1 | `~0.5%` |

Interpretation:

- The liquidation activity was concentrated among a small number of callers.
- The top two callers account for about `80.6%` of liquidation events.
- The third caller performed `33` liquidation events but only used `2` transactions, implying bundled / batched execution.
- This supports describing the extraction as concentrated liquidator / MEV activity rather than ordinary dispersed liquidations.

## Key Ratios

The most useful high-level ratios for the original meme-token valuation estimate are:

| Ratio | Value |
|---|---:|
| Gross extraction / USDS actually repaid | `~1,081,628%` |
| Net extraction / USDS actually repaid | `~1,081,579%` |
| Gross extraction / USDS bad debt | `~2.61x` |
| Gross extraction / total USDS debt affected | `~2.61x` |
| Gross extraction / fair seized collateral value | `~100.0%` |
| Bad debt / fair seized collateral value | `~38.3%` |

Interpretation:

- Liquidators paid only about `158 USDS` in aggregate because the scaled-down oracle values made collateral appear almost worthless.
- They received collateral whose fair value was approximately `$1.708M` using normalized pre/corrected DIA prices.
- Morpho recorded approximately `654,574 USDS` of bad debt.
- A rough split of the combined economic harm is about:
  - `~72.3%` captured by liquidators / MEV as collateral extraction.
  - `~27.7%` left as Morpho bad debt / lender-side loss.

## Per-Market Results

The first table is the original meme-token valuation set. The addendum below it lists the extra cbBTC and BOBO liquidations found by the full-window Morpho log audit.

| Collateral | LLTV | Events | Repaid USDS | Bad debt USDS | Seized fair value | Gross extraction | Extraction / repaid | First observed liquidation |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| PEPE | 62.5% | 1 | `0.00` | `0.00` | `$1.61` | `$1.61` | `1,135,001.9%` | [`0xc2aad10f...`](https://etherscan.io/tx/0xc2aad10fbf710e11b1011051726cd3b471238d0f1771c174751072523df24543) |
| PEPE | 77% | 20 | `85.08` | `470,294.07` | `$920,611.37` | `$920,526.28` | `1,081,933.2%` | [`0x2cf791f6...`](https://etherscan.io/tx/0x2cf791f65e96359acc6e955bdec3d4504886339f85b05f52db85d61d481052e8) |
| JOE | 77% | 14 | `3.24` | `5,338.43` | `$32,594.91` | `$32,591.67` | `1,005,670.7%` | [`0x8c91ce99...`](https://etherscan.io/tx/0x8c91ce992b0db3c0dbb5df139cf64836ed48d7c74d48dab91fbac6088011c265) |
| JOE | 62.5% | 6 | `7.54` | `22,386.04` | `$79,577.26` | `$79,569.72` | `1,054,964.8%` | [`0xec053a47...`](https://etherscan.io/tx/0xec053a47cdcd654267057d0862f029b9266aba010f680568ba1f5f45a69d7cf1) |
| SPX | 77% | 16 | `14.89` | `16,226.40` | `$160,468.94` | `$160,454.05` | `1,077,479.0%` | [`0xaf8c51f0...`](https://etherscan.io/tx/0xaf8c51f017331b810b4904a8ea91a6281532d1b795b445909827932a06b2792a) |
| SPX | 62.5% | 8 | `13.41` | `38,885.90` | `$151,628.43` | `$151,615.02` | `1,130,295.6%` | [`0xd7332dd1...`](https://etherscan.io/tx/0xd7332dd154064863e65d4c5b70666ce567c53823dd952c4d26fe473ceae34350) |
| MOG | 62.5% | 10 | `3.80` | `16,936.01` | `$44,853.54` | `$44,849.73` | `1,180,106.6%` | [`0x08c2d72f...`](https://etherscan.io/tx/0x08c2d72f40e776d1b48208f07e316322dc123d1cd393358422209707d79e2bf4) |
| MOG | 77% | 41 | `7.96` | `9,791.84` | `$89,540.77` | `$89,532.81` | `1,124,962.7%` | [`0x9bb25b9e...`](https://etherscan.io/tx/0x9bb25b9e930df0dfc9e3d761dfb3ddcbe6a20311000eb111807554c44d93b82d) |
| SHIB | 62.5% | 1 | `0.00` | `0.00` | `$2.37` | `$2.37` | `1,130,873.4%` | [`0x7a63f4a5...`](https://etherscan.io/tx/0x7a63f4a5873a73bdc4eb1c0c65d6cc8ca42e6540a61d0f7c16394f3d0f96de45) |
| SHIB | 77% | 1 | `0.00` | `0.00` | `$0.67` | `$0.67` | `1,078,029.8%` | [`0xd8e67540...`](https://etherscan.io/tx/0xd8e675400b768a15cf45c989079241964fcd406b802d6e113fd1305023886240) |
| NEIRO | 77% | 1 | `0.00` | `0.00` | `$0.47` | `$0.47` | `1,069,984.9%` | [`0x54cc4ac4...`](https://etherscan.io/tx/0x54cc4ac42ef6b3e34d9476ed5b0e9ae552cec0527a14f8d5e73e7f334e8dcd30) |
| NEIRO | 62.5% | 1 | `0.00` | `0.00` | `$0.60` | `$0.60` | `1,122,434.1%` | [`0x946a5216...`](https://etherscan.io/tx/0x946a5216fd03cb12cec0b7718d51db10ed98ea0861cad24ae477baf50365584b) |
| IMF | 62.5% | 9 | `3.37` | `10,673.52` | `$30,324.02` | `$30,320.65` | `899,516.8%` | [`0x0205055e...`](https://etherscan.io/tx/0x0205055eb04c2cccefcfe32176c18a64ce82cf7307bfe0bf6dad8683baed37bd) |
| IMF | 77% | 5 | `0.12` | `1.05` | `$1,038.58` | `$1,038.46` | `857,483.2%` | [`0x374c51b3...`](https://etherscan.io/tx/0x374c51b3f98f7b776e3c6d5d95081fc70ba41dc4251ba53b0f8bea8251f86a24) |
| NPC | 77% | 1 | `0.00` | `0.00` | `$11.44` | `$11.44` | `1,080,761.3%` | [`0x7b5c0305...`](https://etherscan.io/tx/0x7b5c030578d4beb9379a0da9352d9812af436d800e4c6424dfc2ededb2d39726) |
| NPC | 62.5% | 1 | `0.00` | `0.00` | `$1.59` | `$1.59` | `1,133,738.8%` | [`0xf87143a1...`](https://etherscan.io/tx/0xf87143a1b86731008ac9975e2554bc132d426459b2f3f8fbec9c192213dcaa07) |
| REKT | 77% | 4 | `1.01` | `765.07` | `$10,833.09` | `$10,832.08` | `1,069,635.1%` | [`0x19dfce96...`](https://etherscan.io/tx/0x19dfce9678ad0164eadf9eca8e83650c5ebfa63c83b6411958fb39cfbd5c1f9f) |
| REKT | 62.5% | 2 | `1.44` | `7,783.31` | `$16,143.76` | `$16,142.33` | `1,122,067.1%` | [`0x2c8777cf...`](https://etherscan.io/tx/0x2c8777cfaddd2d380c40a85535efcd4332cc4717d71a67b6cb0fb7d6b82855dc) |
| APU | 62.5% | 2 | `0.18` | `663.05` | `$1,990.73` | `$1,990.55` | `1,112,809.3%` | [`0x95b1408c...`](https://etherscan.io/tx/0x95b1408ceba7877afe9e36915f9b60ef319090b9b91c3fce4349bb63bb7372cd) |
| APU | 77% | 3 | `0.36` | `262.41` | `$3,853.81` | `$3,853.45` | `1,060,809.8%` | [`0xd43062e4...`](https://etherscan.io/tx/0xd43062e43cfd8aad943a651250bdb43a7146419bfbf1fef3333769a27bce10a9) |
| CULT | 62.5% | 7 | `1.50` | `5,277.96` | `$16,046.93` | `$16,045.43` | `1,068,226.2%` | [`0x0c606874...`](https://etherscan.io/tx/0x0c6068743a491e5341ea9d11a7bd5858ea3f7135542db0ffedb8ae9ffa6424a7) |
| CULT | 77% | 7 | `5.12` | `22,761.94` | `$52,098.02` | `$52,092.90` | `1,018,308.7%` | [`0xdd63acb4...`](https://etherscan.io/tx/0xdd63acb4cf994ee5af480add84461b34d453cbc6f22219c4a480712d2518018b) |
| BITCOIN | 62.5% | 11 | `8.24` | `25,648.72` | `$89,964.01` | `$89,955.77` | `1,091,190.9%` | [`0x862bb63e...`](https://etherscan.io/tx/0x862bb63ec982bd39d9bbf9813e6784b94590559c3a6f89066e767fda2f3dfe5e) |
| BITCOIN | 77% | 9 | `0.61` | `878.07` | `$6,371.23` | `$6,370.62` | `1,040,206.1%` | [`0xff767588...`](https://etherscan.io/tx/0xff7675881a7bc837d11a69287af87b10e88c5c50fedafbeb2fd0bac05b675d7c) |

Additional decoded Morpho liquidations in the same window:

| Collateral | LLTV | Events | Repaid USDS | Bad debt USDS | Seized collateral | Valuation note | First observed liquidation |
|---|---:|---:|---:|---:|---:|---|---|
| cbBTC | 86% | 2 | `0.0089` | `0.00` | `0.00114442 cbBTC` | About `$93.33` using average pre-update/restored DIA price | [`0xeae7fbcb...`](https://etherscan.io/tx/0xeae7fbcb2b1d13d07fe56697abf98b70227b1212e545a830f87249a4e9783f02) |
| BOBO | 62.5% | 3 | `0.0332` | `0.00` | `4,158,718,614.26 BOBO` | About `$384.57` using pre-update DIA price; no matching block `25030777` restoration update | [`0xa8c08b01...`](https://etherscan.io/tx/0xa8c08b01aecd3916110d57b2017816c4d77f67d36905408418668623bffbdd43) |

## Important Caveats

1. The `repaidAssets` and `badDebtAssets` numbers are exact event-decoded on-chain values for all decoded Morpho liquidations in the window.
2. The seized collateral value is an estimate using normalized DIA prices.
3. The word "MEV" here is used loosely as liquidator extraction. A full MEV accounting would require tracing bundles, swaps, hedges, and private orderflow.
4. Gas cost is carried over from the prior estimate and is small relative to the extraction. The revised gross extraction values are the primary figures; net-after-gas should be treated as approximate.

## Conclusion

The liquidations appear to have affected roughly:

```text
654,732 USDS of debt
```

with approximately:

```text
$1.708M of fair-value collateral seized
```

The resulting gross liquidator extraction is approximately:

```text
$1.708M
```

while Morpho recorded approximately:

```text
654,574 USDS of bad debt
```

This supports the interpretation that the DIA oracle scale-change update caused both substantial lender-side losses and substantial liquidator / MEV extraction.

Return to the [main incident overview](README.md) or [Appendix A: affected DIA feeds and Morpho markets](morpho-dia-impacted-markets.md).
