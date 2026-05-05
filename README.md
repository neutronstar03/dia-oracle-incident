# DIA Oracle Scale Incident Documentation

Documentation for the May 5, 2026 DIA oracle scale incident affecting Morpho USDS markets.

## Documentation Flow

1. [What happened](#what-happened)
2. [Markets affected](#markets-affected)
3. [Estimated value loss](#estimated-value-loss)
4. [Specific example: SPX/USDS](#specific-example-spxusds)

Supporting appendices:

- [Appendix A: affected feeds and Morpho markets](morpho-dia-impacted-markets.md)
- [Appendix B: liquidation loss and liquidator extraction estimate](morpho-dia-liquidation-loss-estimate.md)

## What Happened

At block `25030092`, a DIA oracle batch update changed multiple raw DIA feed values to a scale approximately **10,000x lower** than their preceding values.

| Item | Value |
|---|---|
| DIA scale-change update | [`0x738f...574c`](https://etherscan.io/tx/0x738f860b6ed20d60fc968ac53783387732a559b9e21ebdd0bfe5da4c6d09574c) |
| Function called | `setMultipleValues(string[],uint256[])` |
| DIA oracle contract | [`0xE1A3...1552`](https://etherscan.io/address/0xE1A3d58dc6C516Ef18628ce7E13cfE44B4Ac1552) |
| Scale-change block | `25030092` |
| First observed liquidation block | `25030093` |
| Apparent correction/restoration update | [`0x0612...889b`](https://etherscan.io/tx/0x06124fbc8da5a46c34b1ce43a22a82f3a3eef166428482ae99366b1f11a4889b) |
| Correction/restoration block | `25030777` |

DIA also published a CDR configuration post for related meme-token feeds. It lists several of the affected feed keys, including `JOE/USD`, `PEPE/USD`, `MOG/USD`, `SPX/USD`, and `IMF/USD`, and describes consumption through `getValue(key)`.

Reference: [DIA CDR #094: International Meme Fund token price feed](https://forum.diadata.org/t/cdr-094-international-meme-fund-token-price-feed/1028/6)

The observable pattern was:

1. DIA feeds were updated to values roughly `10,000x` lower than their prior scale.
2. Morpho oracle adapters followed the scaled-down DIA values.
3. Affected positions became liquidatable starting in the next block, `25030093`.
4. A later DIA update at block `25030777` restored the previous scale.

## Markets Affected

The affected markets were Morpho USDS debt markets using collateral assets priced by the DIA feeds included in the batch update.

The impacted collateral set appears to include at least:

```text
PEPE, JOE, SPX, MOG, SHIB, NEIRO, IMF, NPC, REKT, APU, CULT, BITCOIN
```

Across the analyzed liquidation window, the affected markets had:

```text
180 liquidation events
149 unique liquidation transactions
139 unique borrowers
```

For the supporting feed-level and market-level evidence, see [Appendix A: affected feeds and Morpho markets](morpho-dia-impacted-markets.md).

## Estimated Value Loss

Across the impacted markets analyzed, the liquidation and extraction estimate is:

| Metric | Estimate |
|---|---:|
| USDS actually repaid by liquidators | `104.43 USDS` |
| USDS bad debt recorded | `352,963.78 USDS` |
| Total USDS debt closed / affected | `353,068.21 USDS` |
| Fair value of seized collateral | `$1,129,468.38` |
| Gross liquidator extraction | `$1,129,363.96` |
| Estimated gas paid by liquidation txs | `$77.26` |
| Net liquidator extraction after gas | `$1,129,286.70` |

Liquidation activity was concentrated among a small number of liquidator callers:

| Liquidator caller | Events | Unique txs | Markets touched | Share of events |
|---|---:|---:|---:|---:|
| [`0xad21...3221`](https://etherscan.io/address/0xad213ae0b710c7bc6c915984d91bad008b2d3221) | 88 | 88 | 17 | `~48.9%` |
| [`0x3633...e95c`](https://etherscan.io/address/0x36331e299247e5d0d3261e1d9852f6e0cffee95c) | 58 | 58 | 21 | `~32.2%` |
| [`0xaba9...78f8`](https://etherscan.io/address/0xaba996f3f6170a85a31d7f8f4b54816e141278f8) | 33 | 2 | 2 | `~18.3%` |
| [`0xe08d...d015`](https://etherscan.io/address/0xe08d97e151473a848c3d9ca3f323cb720472d015) | 1 | 1 | 1 | `~0.6%` |

High-level interpretation:

- Liquidators repaid only about `104 USDS` in aggregate because the scaled-down oracle values made collateral appear almost worthless.
- They received collateral with an estimated fair value of approximately `$1.13M`, using normalized pre-update and post-restoration DIA prices.
- Morpho recorded approximately `352,964 USDS` of bad debt.
- The top two liquidator callers account for approximately `81.1%` of liquidation events.

For methodology, caveats, per-market results, and the full liquidator breakdown, see [Appendix B: liquidation loss and liquidator extraction estimate](morpho-dia-liquidation-loss-estimate.md).

## Specific Example: SPX/USDS

SPX/USDS is a useful worked example because the same pattern appears clearly at the feed, adapter, and liquidation layers. Other affected markets follow the same general pattern, so they are summarized in [Appendix A](morpho-dia-impacted-markets.md) rather than repeated in full here.

### Scope

The DIA feed emitted by the oracle is **`SPX/USD`**, not literally `SPX/USDS`. The affected Morpho markets use SPX collateral against USDS debt, so the `SPX/USD` DIA feed is the relevant collateral price input.

Morpho SPX/USDS market IDs:

- [`0xc7d717f4052ac4e5463dcc58cea0f6b05dd7d8c67e0aee68ebe30a8af09b259f`](https://app.morpho.org/ethereum/market/0xc7d717f4052ac4e5463dcc58cea0f6b05dd7d8c67e0aee68ebe30a8af09b259f)
- [`0x29200655ad6ee4b86a0f4132e86736844479b4f4ff55d0a40fb31e8264fb811c`](https://app.morpho.org/ethereum/market/0x29200655ad6ee4b86a0f4132e86736844479b4f4ff55d0a40fb31e8264fb811c)

Morpho SPX/USDS oracle adapter:

[`0xdA63266b5184D08DbFBace96267837c45D7D34dA`](https://etherscan.io/address/0xdA63266b5184D08DbFBace96267837c45D7D34dA)

### SPX/USD DIA Timeline

| Block | Time UTC | Transaction | DIA raw value | Human if `/1e8` |
|---:|---|---|---:|---:|
| 25028975 | 2026-05-05 13:02:26 | [`0x4c3e...4c7d`](https://etherscan.io/tx/0x4c3e148f37c69603e95113e2c5021a31f934a40a7ef3787cc1954d797f244c7d) | `409057079812` | `4090.57079812` |
| 25029259 | 2026-05-05 13:59:06 | [`0x6d62...0756`](https://etherscan.io/tx/0x6d62f42fbe2e03bde651895914ea4bbfe1f52344c3676570b485734730a40756) | `404789551173` | `4047.89551173` |
| 25029466 | 2026-05-05 14:41:07 | [`0x1d52...0c31`](https://etherscan.io/tx/0x1d52de9db4f394ebbc5a24b9ef8422333ae21beb0e2c83ad9112bcb944330c31) | `400565701307` | `4005.65701307` |
| 25029622 | 2026-05-05 15:12:42 | [`0x557f...9c4b5`](https://etherscan.io/tx/0x557f5b6e93a6cb70e1f6ee14ba5fd914997f197f31cd0d7695e47f4b9fe9c4b5) | `405427576686` | `4054.27576686` |
| 25030060 | 2026-05-05 16:40:29 | [`0xb076...faa9`](https://etherscan.io/tx/0xb076b1c93cdad669b8cefe7d6faaa1757f71f5ec373712ada11a8a46f39ffaa9) | `401176412005` | `4011.76412005` |
| **25030092** | **2026-05-05 16:46:49** | **[`0x738f...574c`](https://etherscan.io/tx/0x738f860b6ed20d60fc968ac53783387732a559b9e21ebdd0bfe5da4c6d09574c)** | **`40064813`** | **`0.40064813`** |
| 25030777 | 2026-05-05 19:04:04 | [`0x0612...889b`](https://etherscan.io/tx/0x06124fbc8da5a46c34b1ce43a22a82f3a3eef166428482ae99366b1f11a4889b) | `402704905465` | `4027.04905465` |

The SPX/USD raw DIA value moved from `401176412005` to `40064813`, a drop factor of approximately `10013x`.

### Morpho Adapter Impact

The Morpho SPX/USDS oracle adapter output followed the DIA value directly.

| Block | Adapter output |
|---:|---:|
| 25030060 | `4011764120050000000000000000000000000000000000` |
| 25030092 | `400648130000000000000000000000000000000000` |
| 25030777 | `4027049054650000000000000000000000000000000000` |

Therefore, Morpho's effective SPX collateral valuation also dropped by approximately **10,000x**.

### SPX Liquidation Evidence

The DIA scale-change update occurred in block `25030092`. The first observed SPX/USDS Morpho liquidations began in the next block, `25030093`.

Observed SPX liquidation counts before the later correction:

- Market [`0xc7d717f4052ac4e5463dcc58cea0f6b05dd7d8c67e0aee68ebe30a8af09b259f`](https://app.morpho.org/ethereum/market/0xc7d717f4052ac4e5463dcc58cea0f6b05dd7d8c67e0aee68ebe30a8af09b259f): **16 liquidation events**
- Market [`0x29200655ad6ee4b86a0f4132e86736844479b4f4ff55d0a40fb31e8264fb811c`](https://app.morpho.org/ethereum/market/0x29200655ad6ee4b86a0f4132e86736844479b4f4ff55d0a40fb31e8264fb811c): **8 liquidation events**

Example SPX liquidation transactions in block `25030093`:

- [`0xd7332dd154064863e65d4c5b70666ce567c53823dd952c4d26fe473ceae34350`](https://etherscan.io/tx/0xd7332dd154064863e65d4c5b70666ce567c53823dd952c4d26fe473ceae34350)
- [`0xaf8c51f017331b810b4904a8ea91a6281532d1b795b445909827932a06b2792a`](https://etherscan.io/tx/0xaf8c51f017331b810b4904a8ea91a6281532d1b795b445909827932a06b2792a)
- [`0x148ea18c55096bd21de220ba600ba2f2646d766e579ec1bdafdaf459ed71a2c0`](https://etherscan.io/tx/0x148ea18c55096bd21de220ba600ba2f2646d766e579ec1bdafdaf459ed71a2c0)
- [`0xed2b8dc94ec3f0a404c5c42083ae57f24fa743271e4d3320a895cb2bec0d4487`](https://etherscan.io/tx/0xed2b8dc94ec3f0a404c5c42083ae57f24fa743271e4d3320a895cb2bec0d4487)

For all other affected markets, the documentation keeps the details in appendices to avoid repeating the same pattern market-by-market.
