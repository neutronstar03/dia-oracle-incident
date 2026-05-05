# DIA Oracle Scale Incident Documentation

Documentation for the May 5, 2026 DIA oracle scale incident affecting Morpho USDS markets.

## Documents

- [SPX/USDS incident breakdown](#spxusds-incident-breakdown) — detailed walkthrough of the SPX/USDS market impact.
- [Broader impacted markets](morpho-dia-impacted-markets.md) — related evidence for other Morpho USDS collateral markets affected by the same DIA batch update.

## Incident Summary

The DIA oracle update associated with the scale issue is:

[`0x738f860b6ed20d60fc968ac53783387732a559b9e21ebdd0bfe5da4c6d09574c`](https://etherscan.io/tx/0x738f860b6ed20d60fc968ac53783387732a559b9e21ebdd0bfe5da4c6d09574c)

It updated DIA feeds through `setMultipleValues(string[],uint256[])`. For `SPX/USD`, the raw value moved from the normal `~4.0e11` range to `~4.0e7`, an approximately **10,000x drop**. Morpho liquidations began in the **next block**.

The same batch update appears to have affected other Morpho USDS markets. See [Broader impacted markets](morpho-dia-impacted-markets.md) for the multi-market analysis.

## Key References

| Item | Value |
|---|---|
| DIA scale-change update | [`0x738f...574c`](https://etherscan.io/tx/0x738f860b6ed20d60fc968ac53783387732a559b9e21ebdd0bfe5da4c6d09574c) |
| Apparent correction update | [`0x0612...889b`](https://etherscan.io/tx/0x06124fbc8da5a46c34b1ce43a22a82f3a3eef166428482ae99366b1f11a4889b) |
| DIA oracle contract | [`0xE1A3...1552`](https://etherscan.io/address/0xE1A3d58dc6C516Ef18628ce7E13cfE44B4Ac1552) |
| Morpho SPX/USDS oracle adapter | [`0xdA63...4dA`](https://etherscan.io/address/0xdA63266b5184D08DbFBace96267837c45D7D34dA) |
| Scale-change update block | `25030092` |
| First observed liquidation block | `25030093` |
| Correction block | `25030777` |

## SPX/USDS Incident Breakdown

### Scope

The DIA feed emitted by the oracle is **`SPX/USD`**, not literally `SPX/USDS`. The affected Morpho markets use SPX collateral against USDS debt, so the `SPX/USD` DIA feed is the relevant collateral price input.

### Morpho SPX/USDS Market IDs

- `0xc7d717f4052ac4e5463dcc58cea0f6b05dd7d8c67e0aee68ebe30a8af09b259f`
- `0x29200655ad6ee4b86a0f4132e86736844479b4f4ff55d0a40fb31e8264fb811c`

## Transaction Comparison

### Earlier Normal SPX Update

| Field | Value |
|---|---|
| Transaction | [`0x6d62...0756`](https://etherscan.io/tx/0x6d62f42fbe2e03bde651895914ea4bbfe1f52344c3676570b485734730a40756) |
| Function | `setValue(string,uint128,uint128)` |
| Feed | `SPX/USD` |
| Raw value | `404789551173` |
| Human-readable value if `/1e8` | `4047.89551173` |

This was consistent with the previous SPX/USD DIA values.

### Scale-Change Update

| Field | Value |
|---|---|
| Transaction | [`0x738f...574c`](https://etherscan.io/tx/0x738f860b6ed20d60fc968ac53783387732a559b9e21ebdd0bfe5da4c6d09574c) |
| Function | `setMultipleValues(string[],uint256[])` |
| Feed | `SPX/USD` |
| Raw value | `40064813` |
| Human-readable value if `/1e8` | `0.40064813` |

This is approximately a **10,000x drop** from the immediately preceding normal value.

## SPX/USD DIA Timeline

| Block | Time UTC | Transaction | DIA raw value | Human if `/1e8` |
|---:|---|---|---:|---:|
| 25028975 | 2026-05-05 13:02:26 | [`0x4c3e...4c7d`](https://etherscan.io/tx/0x4c3e148f37c69603e95113e2c5021a31f934a40a7ef3787cc1954d797f244c7d) | `409057079812` | `4090.57079812` |
| 25029259 | 2026-05-05 13:59:06 | [`0x6d62...0756`](https://etherscan.io/tx/0x6d62f42fbe2e03bde651895914ea4bbfe1f52344c3676570b485734730a40756) | `404789551173` | `4047.89551173` |
| 25029466 | 2026-05-05 14:41:07 | [`0x1d52...0c31`](https://etherscan.io/tx/0x1d52de9db4f394ebbc5a24b9ef8422333ae21beb0e2c83ad9112bcb944330c31) | `400565701307` | `4005.65701307` |
| 25029622 | 2026-05-05 15:12:42 | [`0x557f...9c4b5`](https://etherscan.io/tx/0x557f5b6e93a6cb70e1f6ee14ba5fd914997f197f31cd0d7695e47f4b9fe9c4b5) | `405427576686` | `4054.27576686` |
| 25030060 | 2026-05-05 16:40:29 | [`0xb076...faa9`](https://etherscan.io/tx/0xb076b1c93cdad669b8cefe7d6faaa1757f71f5ec373712ada11a8a46f39ffaa9) | `401176412005` | `4011.76412005` |
| **25030092** | **2026-05-05 16:46:49** | **[`0x738f...574c`](https://etherscan.io/tx/0x738f860b6ed20d60fc968ac53783387732a559b9e21ebdd0bfe5da4c6d09574c)** | **`40064813`** | **`0.40064813`** |
| 25030777 | 2026-05-05 19:04:04 | [`0x0612...889b`](https://etherscan.io/tx/0x06124fbc8da5a46c34b1ce43a22a82f3a3eef166428482ae99366b1f11a4889b) | `402704905465` | `4027.04905465` |

## Scale Change

| Point | Raw DIA value |
|---|---:|
| Immediately before scale-change transaction | `401176412005` |
| After scale-change transaction | `40064813` |
| Later correction/restoration | `402704905465` |

Drop factor: `~10013x`.

This strongly suggests a decimal or scaling error, with the DIA raw value changing from the prior `~4.0e11` scale to a `~4.0e7` scale.

## Morpho Oracle Adapter Impact

The Morpho SPX/USDS oracle adapter output followed the DIA value directly.

| Block | Adapter output |
|---:|---:|
| 25030060 | `4011764120050000000000000000000000000000000000` |
| 25030092 | `400648130000000000000000000000000000000000` |
| 25030777 | `4027049054650000000000000000000000000000000000` |

Therefore, Morpho's effective SPX collateral valuation also dropped by approximately **10,000x**.

## Liquidation Evidence

The DIA scale-change update occurred in block `25030092`. The first observed SPX/USDS Morpho liquidations began in the next block, `25030093`.

Observed liquidation counts before the later correction:

- Market `0xc7d717f4052ac4e5463dcc58cea0f6b05dd7d8c67e0aee68ebe30a8af09b259f`: **16 liquidation events**
- Market `0x29200655ad6ee4b86a0f4132e86736844479b4f4ff55d0a40fb31e8264fb811c`: **8 liquidation events**

Example liquidation transactions in block `25030093`:

- [`0xd7332dd154064863e65d4c5b70666ce567c53823dd952c4d26fe473ceae34350`](https://etherscan.io/tx/0xd7332dd154064863e65d4c5b70666ce567c53823dd952c4d26fe473ceae34350)
- [`0xaf8c51f017331b810b4904a8ea91a6281532d1b795b445909827932a06b2792a`](https://etherscan.io/tx/0xaf8c51f017331b810b4904a8ea91a6281532d1b795b445909827932a06b2792a)
- [`0x148ea18c55096bd21de220ba600ba2f2646d766e579ec1bdafdaf459ed71a2c0`](https://etherscan.io/tx/0x148ea18c55096bd21de220ba600ba2f2646d766e579ec1bdafdaf459ed71a2c0)
- [`0xed2b8dc94ec3f0a404c5c42083ae57f24fa743271e4d3320a895cb2bec0d4487`](https://etherscan.io/tx/0xed2b8dc94ec3f0a404c5c42083ae57f24fa743271e4d3320a895cb2bec0d4487)

## Conclusion

For the Morpho **SPX/USDS** markets, the transaction associated with the oracle scale issue is [`0x738f...574c`](https://etherscan.io/tx/0x738f860b6ed20d60fc968ac53783387732a559b9e21ebdd0bfe5da4c6d09574c).

It updated DIA `SPX/USD` from the normal raw value scale around `4.0e11` to `4.0e7`, causing an approximately **10,000x lower collateral price** in the Morpho oracle adapter. Liquidations started in the **next block**, which is strong evidence that the oracle update directly caused positions to become liquidatable.

For evidence that the incident extended beyond SPX/USDS, continue to [Broader impacted markets](morpho-dia-impacted-markets.md).
