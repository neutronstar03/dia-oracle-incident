# Suggested Restitution Plan

This document explains how affected borrowers and lenders can be made whole after the DIA oracle scale incident affecting Morpho USDS markets.

The plan separates losses into two categories:

1. **Borrower net collateral/equity loss**: collateral value taken in incident liquidations, minus the USDS debt that was already owed and closed by those liquidations.
2. **Lender bad debt**: USDS debt recorded by Morpho as bad debt during the same incident liquidations.

Technical reproduction details, scripts, formulas, and regeneration commands are maintained separately in [`restitution-technical-methodology.md`](restitution-technical-methodology.md).

## High-Level Results

Using the pre-incident price snapshot at block `25030091`, the generated restitution dataset currently gives:

| Category | Amount |
|---|---:|
| **Total suggested restitution** | **`1,733,056.58 USDS`** |
| Borrower net restitution | `1,078,482.67 USDS` |
| Lender bad debt, market-level | `654,573.91 USDS` |
| USDS repaid by liquidators | `157.88 USDS` |
| Fair value of seized collateral | `$1,733,173.70` |

Counts:

| Metric | Count |
|---|---:|
| Liquidation events | `186` |
| Unique borrowers | `141` |
| Borrower-market rows | `169` |
| Affected markets with liquidations | `26` |

## Price Snapshot

The restitution calculations price seized collateral with DIA values read immediately before the incident, at block `25030091`. Selected snapshot prices:

| Collateral | USD/USDS per token |
|---|---:|
| PEPE | `0.000004090714` |
| SPX | `0.401176412005` |
| BITCOIN | `0.021968841306` |
| CULT | `0.000198464876` |
| JOE | `0.013213510296` |

The full asset price table is in [`data/restitution-price-snapshot-25030091.md`](data/restitution-price-snapshot-25030091.md).

## Borrower Restitution

Borrowers should **not** receive the full value of seized collateral. They already had USDS debt before the incident, so that debt must be subtracted.

In plain terms:

```text
borrower net restitution = seized collateral value - debt offset
```

Where:

- `Seized value USD` is the fair value of collateral seized during incident liquidations, priced with the pre-incident block `25030091` DIA values.
- `Debt offset USDS` is the USDS debt closed by the liquidation, equal to `repaidAssets + badDebtAssets`.
- `Net restitution USDS` is the estimated amount owed back to the borrower.

This calculation floors each liquidation event at zero before aggregation. In other words, if a single event closed slightly more debt than the fair value of collateral seized, it does not create a negative borrower claim. This is a policy choice and is arguable; aggregating before flooring would reduce borrower restitution by only about `40.69 USDS`, so the difference is immaterial relative to the total.

The table also includes pre-incident context:

- `Pre collateral USD` / `Pre collateral`: borrower collateral immediately before the incident, shown as USD value in the borrower aggregate table and collateral-token amount in the borrower-market table.
- `Pre borrow USDS`: borrower USDS debt immediately before the incident.
- `Pre borrow LTV`: pre-incident borrow loan-to-value.

Full generated borrower tables:

- [Borrower restitution aggregated by borrower](data/borrower-restitution-by-borrower.md)
- [Borrower restitution by borrower and market](data/borrower-restitution-by-borrower-market.md)

### Top Borrower Restitution Rows

Shown 15 of 141 borrower rows. The full table is in [`data/borrower-restitution-by-borrower.md`](data/borrower-restitution-by-borrower.md). Rows are sorted by largest net restitution amount:

| Borrower | Markets | Events | Pre collateral USD | Pre borrow USDS | Pre borrow LTV | Seized value USD | Debt offset USDS | Net restitution USDS |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| [`0x339b...5b1a`](https://etherscan.io/address/0x339b07af597a2c6128d067633611baf3f0725b1a) | 1 | 1 | `578,582.82` | `301,585.62` | `52.12%` | `578,582.82` | `301,663.50` | `276,919.32` |
| [`0x66de...8e91`](https://etherscan.io/address/0x66de18b35d535883b1561f5f58876d565e518e91) | 1 | 2 | `330,325.83` | `165,232.87` | `50.02%` | `330,325.83` | `165,275.55` | `165,050.28` |
| [`0x14ed...4564`](https://etherscan.io/address/0x14edf4a73e5d8a48ed1ed1c3b0933b5f25004564) | 1 | 1 | `112,761.86` | `24,465.02` | `21.70%` | `112,761.86` | `24,471.76` | `88,290.10` |
| [`0xfb2e...2fd9`](https://etherscan.io/address/0xfb2e9d84a36068d541da5eed27b17a38441d2fd9) | 1 | 1 | `78,895.39` | `7,966.44` | `10.10%` | `78,895.39` | `8,006.76` | `70,888.63` |
| [`0xb334...2396`](https://etherscan.io/address/0xb3343e623d7a6860881ed9b178ecb22796812396) | 1 | 1 | `37,705.30` | `3,407.43` | `9.04%` | `37,705.30` | `3,410.14` | `34,295.16` |
| [`0xebf7...1768`](https://etherscan.io/address/0xebf712753fe79098f9591e691b9a866e16661768) | 1 | 1 | `43,937.68` | `12,344.02` | `28.09%` | `43,937.68` | `12,350.30` | `31,587.38` |
| [`0xec78...a2c6`](https://etherscan.io/address/0xec785bb5efcc1393de44eef261a298962b35a2c6) | 1 | 1 | `46,557.13` | `15,111.05` | `32.46%` | `46,557.13` | `15,118.79` | `31,438.34` |
| [`0x0b53...bc9a`](https://etherscan.io/address/0x0b5305f909b57f483e0b2c9614cc625943c4bc9a) | 1 | 1 | `49,163.06` | `20,212.25` | `41.11%` | `49,163.06` | `20,350.60` | `28,812.46` |
| [`0xad39...c769`](https://etherscan.io/address/0xad399d2d5a4823788a33e3ce47922ab86f47c769) | 1 | 1 | `35,191.50` | `6,683.98` | `18.99%` | `35,191.50` | `6,687.40` | `28,504.09` |
| [`0x55d5...4e8c`](https://etherscan.io/address/0x55d578950d3f21364537cd561149313627054e8c) | 1 | 1 | `28,548.35` | `1,370.89` | `4.80%` | `28,548.35` | `1,371.98` | `27,176.37` |
| [`0x9e62...3e4c`](https://etherscan.io/address/0x9e62af47ac686c7254083e607882ce8349c63e4c) | 2 | 2 | `39,139.56` | `15,189.58` | `38.81%` | `39,139.56` | `15,194.70` | `23,944.85` |
| [`0x1208...4d2b`](https://etherscan.io/address/0x1208ec710852c271526a2db652074c1762f64d2b) | 3 | 3 | `22,013.25` | `1,026.99` | `4.67%` | `22,013.26` | `1,027.63` | `20,985.62` |
| [`0xacc6...596a`](https://etherscan.io/address/0xacc6bf34c7235ef8c8adb9546e494193c28d596a) | 1 | 1 | `24,294.88` | `3,869.02` | `15.93%` | `24,294.88` | `3,870.82` | `20,424.06` |
| [`0x4bb9...4d8a`](https://etherscan.io/address/0x4bb985905601304808528d66ef15c5ef1ead4d8a) | 1 | 1 | `20,770.31` | `1,146.12` | `5.52%` | `20,770.31` | `1,147.03` | `19,623.28` |
| [`0x4c43...6c98`](https://etherscan.io/address/0x4c434b565497acdd971d9d4e2129c6f48c936c98) | 1 | 1 | `33,493.54` | `14,535.33` | `43.40%` | `33,493.54` | `14,539.00` | `18,954.55` |

## Lender Restitution

Lenders are affected through Morpho bad debt. The current generated lender table is market-level:

```text
market lender loss = sum(badDebtAssets) across incident liquidations
```

Full generated lender tables:

- [Lender bad debt by market](data/lender-bad-debt-by-market.md)
- [Lender bad debt by lender](data/lender-bad-debt-by-lender.md)
- [Lender bad debt by lender and market](data/lender-bad-debt-by-lender-market.md)

### Top Lender Bad-Debt Markets

Shown 15 of 26 market rows. The full table is in [`data/lender-bad-debt-by-market.md`](data/lender-bad-debt-by-market.md). Rows are sorted by largest market bad debt:

| Collateral | LLTV | Market | Events | Borrowers | Repaid USDS | Bad debt USDS | Debt closed USDS |
|---|---:|---|---:|---:|---:|---:|---:|
| PEPE | 77% | [`0x5ffdf1...55841e`](https://app.morpho.org/ethereum/market/0x5ffdf15c5a4d7c6affb3f12634eeda1a20e60b92c0eb547f61754f656b55841e) | 20 | 15 | `85.09` | `470,294.08` | `470,379.17` |
| SPX | 62.5% | [`0x292006...fb811c`](https://app.morpho.org/ethereum/market/0x29200655ad6ee4b86a0f4132e86736844479b4f4ff55d0a40fb31e8264fb811c) | 8 | 8 | `13.41` | `38,885.91` | `38,899.31` |
| BITCOIN | 62.5% | [`0x9bdf55...ec7a5f`](https://app.morpho.org/ethereum/market/0x9bdf55afe3832abff223c7d10b2af529b395ec2489e32d872156421c32ec7a5f) | 11 | 11 | `8.23` | `25,648.72` | `25,656.97` |
| CULT | 77% | [`0x0655e0...4b7587`](https://app.morpho.org/ethereum/market/0x0655e0c8686d94d9e0c0d2b78d7f99492676e52d712db5ac061b3c78da4b7587) | 7 | 5 | `5.11` | `22,761.95` | `22,767.06` |
| JOE | 62.5% | [`0x38d28a...e0d1c7`](https://app.morpho.org/ethereum/market/0x38d28aa002b2961f734763f6afeeb78a36a9b947cb12b988c35a5bb4bde0d1c7) | 6 | 6 | `7.54` | `22,386.04` | `22,393.58` |
| MOG | 62.5% | [`0x44f51e...4086b6`](https://app.morpho.org/ethereum/market/0x44f51e6b7356132597872e40c8d4a5bb2f1fc2c99e7292ee3b3953d9074086b6) | 10 | 10 | `3.81` | `16,936.03` | `16,939.80` |
| SPX | 77% | [`0xc7d717...9b259f`](https://app.morpho.org/ethereum/market/0xc7d717f4052ac4e5463dcc58cea0f6b05dd7d8c67e0aee68ebe30a8af09b259f) | 16 | 15 | `14.89` | `16,226.43` | `16,241.29` |
| IMF | 62.5% | [`0xa5a49f...e7fe08`](https://app.morpho.org/ethereum/market/0xa5a49fa08443783f5a5cdc99b604033378f65148ec5cb6b2e718e801c4e7fe08) | 9 | 8 | `3.37` | `10,673.52` | `10,676.89` |
| MOG | 77% | [`0x3f1d5c...82c6ec`](https://app.morpho.org/ethereum/market/0x3f1d5c88c72432b04f2074499fe217468af49ddaa98bcb6ec80b08f76a82c6ec) | 41 | 33 | `7.95` | `9,791.85` | `9,799.79` |
| REKT | 62.5% | [`0x973b23...6433f7`](https://app.morpho.org/ethereum/market/0x973b23002efe233943715a2dfb98b66a0434d4b192b00bb4924230b3916433f7) | 2 | 2 | `1.44` | `7,783.32` | `7,784.75` |
| JOE | 77% | [`0xef9f1e...ef7b01`](https://app.morpho.org/ethereum/market/0xef9f1e3e71483c9c9b61d2e27452e26507e52b547775ca899277b35585ef7b01) | 14 | 14 | `3.23` | `5,338.44` | `5,341.65` |
| CULT | 62.5% | [`0xb1115c...939225`](https://app.morpho.org/ethereum/market/0xb1115c39bd889bbf0295e1482a50a3c3582bd08668fd73bedcbc26c3cb939225) | 7 | 7 | `1.50` | `5,277.96` | `5,279.47` |
| BITCOIN | 77% | [`0x81b97c...38b3f8`](https://app.morpho.org/ethereum/market/0x81b97c7305aca46c62f2ffce63a09c6a4d647163e25f31c44fadcbeab838b3f8) | 9 | 9 | `0.61` | `878.06` | `878.68` |
| REKT | 77% | [`0xa7ed1d...ed1d7a`](https://app.morpho.org/ethereum/market/0xa7ed1d25d22232695244bf63fdee33688d6d3540e569dd3d88919a7982ed1d7a) | 4 | 4 | `1.01` | `765.08` | `766.09` |
| APU | 62.5% | [`0x37997b...039ac7`](https://app.morpho.org/ethereum/market/0x37997b3cf7cea3555abb101f94f39963e8256be71408165937d4fb7642039ac7) | 2 | 2 | `0.18` | `663.05` | `663.23` |

Per-lender bad-debt allocation uses each lender's Morpho supply shares at the pre-incident snapshot block and allocates each market's bad debt pro rata. This allocation should be reviewed before final publication.

### Top Lender Allocation Rows

Shown 15 of 37 lender rows. The full table is in [`data/lender-bad-debt-by-lender.md`](data/lender-bad-debt-by-lender.md). Rows are sorted by largest lender bad-debt allocation:

| Lender | Markets | Lender bad debt USDS |
|---|---:|---:|
| [`0x2e87...984d`](https://etherscan.io/address/0x2e87d6bfa3f2a932e0c70a32607c0b839404984d) | 10 | `142,372.65` |
| [`0xf704...1353`](https://etherscan.io/address/0xf7044e57bcd224cca81378c5d636194d228f1353) | 1 | `124,878.16` |
| [`0x39f4...bebc`](https://etherscan.io/address/0x39f434f2beaba6df1f200350813c19f5d6d0bebc) | 1 | `79,484.96` |
| [`0x7c09...808e`](https://etherscan.io/address/0x7c09c02aa9eea0c61368cb66cec65d2f0b07808e) | 6 | `66,408.99` |
| [`0xc766...6c54`](https://etherscan.io/address/0xc7666afe71d4699a9331092ccfd055846f9c6c54) | 12 | `43,911.46` |
| [`0x25d3...d449`](https://etherscan.io/address/0x25d385fcab771e36a826bbfb47e2ddaa2f19d449) | 8 | `36,134.20` |
| [`0xdef1...d43d`](https://etherscan.io/address/0xdef1fce2df6270fdf7e1214343bebbab8583d43d) | 11 | `33,282.75` |
| [`0xb39d...ea3f`](https://etherscan.io/address/0xb39d9d81ce88aa1679f0570af6e452d50358ea3f) | 12 | `20,901.31` |
| [`0x240d...6606`](https://etherscan.io/address/0x240d6ce8edf36fdc534c920238512b9c0ca96606) | 1 | `17,641.64` |
| [`0x48cd...4955`](https://etherscan.io/address/0x48cd090c9e8a9954b0955c8b87754031d90c4955) | 5 | `16,395.80` |
| [`0xde0e...d253`](https://etherscan.io/address/0xde0ea31b4084b428ca85205a5e6dbaf16818d253) | 1 | `14,593.70` |
| [`0x60a3...6dbd`](https://etherscan.io/address/0x60a36588d8ed7a8bb886659d17b36b34e81e6dbd) | 1 | `13,886.52` |
| [`0x579e...2ccc`](https://etherscan.io/address/0x579ea162eda350ff57b7ef4b34bd72f749d92ccc) | 8 | `10,235.45` |
| [`0xbbc9...00e0`](https://etherscan.io/address/0xbbc901782e2409751ac7bb7c6a778080570600e0) | 3 | `8,925.60` |
| [`0x0424...9596`](https://etherscan.io/address/0x0424ece0ea139f2df634fe5eb97a2c8a49289596) | 1 | `7,087.29` |

## Small cbBTC and BOBO Rows

The headline totals include the small cbBTC and BOBO rows found in the liquidation window. They are not material to the result:

| Collateral | Events | Borrowers | Seized value USD | Bad debt USDS | Borrower restitution USDS |
|---|---:|---:|---:|---:|---:|
| cbBTC | 2 | 2 | `93.17` | `0.00` | `93.16` |
| BOBO | 3 | 3 | `384.58` | `0.00` | `384.54` |

They were previously discussed separately because cbBTC was negligible and BOBO did not follow the same initial-batch/restoration pattern as the main DIA batch. Since together they add only about `477.70 USDS` of borrower restitution and no lender bad debt, including them in the headline totals does not materially change the plan.

## Notes

- USDS is treated as USD-equivalent for these calculations.
- Borrower restitution uses the block `25030091` DIA prices, not post-incident or average prices.
- Borrower and lender losses are listed separately to avoid mixing borrower equity restoration with lender bad-debt restoration.
