# Appendix A: Affected DIA Feeds and Morpho Markets

Supporting evidence for the [DIA Oracle Scale Incident Documentation](README.md). This appendix lists the affected DIA feeds, the corresponding Morpho USDS markets, and observed liquidation activity during the scale-change window.

## Contents

- [DIA feed scale drops](#dia-feed-scale-drops)
- [Confirmed Morpho USDS markets with liquidations](#confirmed-morpho-usds-markets-with-liquidations)
- [First example liquidations](#first-example-liquidations)
- [Interpretation](#interpretation)

## DIA Feed Scale Drops

The DIA batch update at block `25030092` changed many feeds from their prior raw value scale to values approximately **10,000x lower**. The apparent correction/restoration update occurred at block `25030777`.

DIA's CDR #094 configuration post lists several of these affected feed keys, including `JOE/USD`, `PEPE/USD`, `MOG/USD`, `SPX/USD`, and `IMF/USD`, and describes reading the values through `getValue(key)`.

Reference: [DIA CDR #094: International Meme Fund token price feed](https://forum.diadata.org/t/cdr-094-international-meme-fund-token-price-feed/1028/6)

All values below are raw DIA values read from `getValue(string)`.

| Feed | Before scale-change update | Scale-change update, block 25030092 | After correction, block 25030777 | Approx. drop |
|---|---:|---:|---:|---:|
| `PEPE/USD` | `4090714` | `406` | `4089398` | ~10,076x |
| `JOE/USD` | `13213510296` | `1316032` | `11432311697` | ~10,040x |
| `MOG/USD` | `158148` | `15` | `156082` | ~10,543x |
| `SPX/USD` | `401176412005` | `40064813` | `402704905465` | ~10,013x |
| `SHIB/USD` | `6263091` | `625` | `6283645` | ~10,021x |
| `NEIRO/USD` | `99938041` | `10085` | `101085089` | ~9,910x |
| `IMF/USD` | `17403738629` | `1731423` | `10243967368` | ~10,052x |
| `NPC/USD` | `7601983559` | `754989` | `7592651987` | ~10,069x |
| `REKT/USD` | `150991` | `15` | `147786` | ~10,066x |
| `APU/USD` | `30297690` | `3025` | `29458585` | ~10,016x |
| `CULT/USD` | `198464876` | `19880` | `178513969` | ~9,983x |
| `BITCOIN/USD` | `21968841306` | `2175845` | `20178174755` | ~10,096x |
| `cbBTC/USD` | `81411019677641216` | `8126254324654` | `81697066977326896` | ~10,018x |
| `wstETH/USD` | `2932555237748118` | `291848106216` | `2920824556852812` | ~10,048x |
| `ETH/USD` | `2366981603531590` | `236246563686` | `2372153366119403` | ~10,019x |
| `sUSDS/USD` | `1095340653051` | `109539337` | `1095218218654` | ~10,000x |

Additional related DIA update observed in the same window:

| Feed | Before update, block 25030091 | Scale-change update | Later value in window | Approx. drop |
|---|---:|---:|---:|---:|
| `BOBO/USD` | `92474` | `9` at block `25030121` | `9` at block `25030322` | ~10,275x |

## Confirmed Morpho USDS Markets With Liquidations

The table below counts Morpho `Liquidate` events from immediately after the DIA scale-change update through the correction window. The window begins in the same block as the DIA update because one PEPE liquidation occurred after the DIA update transaction in block `25030092`.

```text
from block 25030092, transactionIndex > 1, through block 25030776
```

| Collateral | LLTV | Morpho market | Liquidation events |
|---|---:|---|---:|
| PEPE | 62.5% | [`0xcbc21405c11c8eb13f1741bfba2a72dfbdab3cb525b79dc5b61148b1183b79a0`](https://app.morpho.org/ethereum/market/0xcbc21405c11c8eb13f1741bfba2a72dfbdab3cb525b79dc5b61148b1183b79a0) | 1 |
| PEPE | 77% | [`0x5ffdf15c5a4d7c6affb3f12634eeda1a20e60b92c0eb547f61754f656b55841e`](https://app.morpho.org/ethereum/market/0x5ffdf15c5a4d7c6affb3f12634eeda1a20e60b92c0eb547f61754f656b55841e) | 20 |
| JOE | 77% | [`0xef9f1e3e71483c9c9b61d2e27452e26507e52b547775ca899277b35585ef7b01`](https://app.morpho.org/ethereum/market/0xef9f1e3e71483c9c9b61d2e27452e26507e52b547775ca899277b35585ef7b01) | 14 |
| JOE | 62.5% | [`0x38d28aa002b2961f734763f6afeeb78a36a9b947cb12b988c35a5bb4bde0d1c7`](https://app.morpho.org/ethereum/market/0x38d28aa002b2961f734763f6afeeb78a36a9b947cb12b988c35a5bb4bde0d1c7) | 6 |
| SPX | 77% | [`0xc7d717f4052ac4e5463dcc58cea0f6b05dd7d8c67e0aee68ebe30a8af09b259f`](https://app.morpho.org/ethereum/market/0xc7d717f4052ac4e5463dcc58cea0f6b05dd7d8c67e0aee68ebe30a8af09b259f) | 16 |
| SPX | 62.5% | [`0x29200655ad6ee4b86a0f4132e86736844479b4f4ff55d0a40fb31e8264fb811c`](https://app.morpho.org/ethereum/market/0x29200655ad6ee4b86a0f4132e86736844479b4f4ff55d0a40fb31e8264fb811c) | 8 |
| MOG | 62.5% | [`0x44f51e6b7356132597872e40c8d4a5bb2f1fc2c99e7292ee3b3953d9074086b6`](https://app.morpho.org/ethereum/market/0x44f51e6b7356132597872e40c8d4a5bb2f1fc2c99e7292ee3b3953d9074086b6) | 10 |
| MOG | 77% | [`0x3f1d5c88c72432b04f2074499fe217468af49ddaa98bcb6ec80b08f76a82c6ec`](https://app.morpho.org/ethereum/market/0x3f1d5c88c72432b04f2074499fe217468af49ddaa98bcb6ec80b08f76a82c6ec) | 41 |
| SHIB | 62.5% | [`0xbd5cff99f6a6988399f1f95835186a46e4642c615bf6364c33027504514791f8`](https://app.morpho.org/ethereum/market/0xbd5cff99f6a6988399f1f95835186a46e4642c615bf6364c33027504514791f8) | 1 |
| SHIB | 77% | [`0x1a01594467db83fefd93ad9028e3c13ca7f8499f7086afefb667966f6a2b3b11`](https://app.morpho.org/ethereum/market/0x1a01594467db83fefd93ad9028e3c13ca7f8499f7086afefb667966f6a2b3b11) | 1 |
| NEIRO | 77% | [`0xc26fb49a683ba55846974fe8283d63ab40dff0788c5ef4e79990426f080b60ec`](https://app.morpho.org/ethereum/market/0xc26fb49a683ba55846974fe8283d63ab40dff0788c5ef4e79990426f080b60ec) | 1 |
| NEIRO | 62.5% | [`0x5fbb467c8f4f3a64ec8c3a58d04febbcce3eaec510f4dfaec5b1b57c8f189a14`](https://app.morpho.org/ethereum/market/0x5fbb467c8f4f3a64ec8c3a58d04febbcce3eaec510f4dfaec5b1b57c8f189a14) | 1 |
| IMF | 62.5% | [`0xa5a49fa08443783f5a5cdc99b604033378f65148ec5cb6b2e718e801c4e7fe08`](https://app.morpho.org/ethereum/market/0xa5a49fa08443783f5a5cdc99b604033378f65148ec5cb6b2e718e801c4e7fe08) | 9 |
| IMF | 77% | [`0x0976b2b8e796994ef3e2fcc6c2f808c420917d531bb9cfaa4537773ca6860e1c`](https://app.morpho.org/ethereum/market/0x0976b2b8e796994ef3e2fcc6c2f808c420917d531bb9cfaa4537773ca6860e1c) | 5 |
| NPC | 77% | [`0xce3a5f1bd26a980be6db1b7acc1a082413bb948d9b19fb4a92cfe5108ff2f275`](https://app.morpho.org/ethereum/market/0xce3a5f1bd26a980be6db1b7acc1a082413bb948d9b19fb4a92cfe5108ff2f275) | 1 |
| NPC | 62.5% | [`0x604e98b52f2375c5d3c6e92766c14174eb45ffbb61d36091f21277ae8930e42c`](https://app.morpho.org/ethereum/market/0x604e98b52f2375c5d3c6e92766c14174eb45ffbb61d36091f21277ae8930e42c) | 1 |
| REKT | 77% | [`0xa7ed1d25d22232695244bf63fdee33688d6d3540e569dd3d88919a7982ed1d7a`](https://app.morpho.org/ethereum/market/0xa7ed1d25d22232695244bf63fdee33688d6d3540e569dd3d88919a7982ed1d7a) | 4 |
| REKT | 62.5% | [`0x973b23002efe233943715a2dfb98b66a0434d4b192b00bb4924230b3916433f7`](https://app.morpho.org/ethereum/market/0x973b23002efe233943715a2dfb98b66a0434d4b192b00bb4924230b3916433f7) | 2 |
| APU | 62.5% | [`0x37997b3cf7cea3555abb101f94f39963e8256be71408165937d4fb7642039ac7`](https://app.morpho.org/ethereum/market/0x37997b3cf7cea3555abb101f94f39963e8256be71408165937d4fb7642039ac7) | 2 |
| APU | 77% | [`0x347aa5f94a12dd46d3e17e542ca1c4033bd6952bde4b22af3caa33c82e52451a`](https://app.morpho.org/ethereum/market/0x347aa5f94a12dd46d3e17e542ca1c4033bd6952bde4b22af3caa33c82e52451a) | 3 |
| CULT | 62.5% | [`0xb1115c39bd889bbf0295e1482a50a3c3582bd08668fd73bedcbc26c3cb939225`](https://app.morpho.org/ethereum/market/0xb1115c39bd889bbf0295e1482a50a3c3582bd08668fd73bedcbc26c3cb939225) | 7 |
| CULT | 77% | [`0x0655e0c8686d94d9e0c0d2b78d7f99492676e52d712db5ac061b3c78da4b7587`](https://app.morpho.org/ethereum/market/0x0655e0c8686d94d9e0c0d2b78d7f99492676e52d712db5ac061b3c78da4b7587) | 7 |
| BITCOIN | 62.5% | [`0x9bdf55afe3832abff223c7d10b2af529b395ec2489e32d872156421c32ec7a5f`](https://app.morpho.org/ethereum/market/0x9bdf55afe3832abff223c7d10b2af529b395ec2489e32d872156421c32ec7a5f) | 11 |
| BITCOIN | 77% | [`0x81b97c7305aca46c62f2ffce63a09c6a4d647163e25f31c44fadcbeab838b3f8`](https://app.morpho.org/ethereum/market/0x81b97c7305aca46c62f2ffce63a09c6a4d647163e25f31c44fadcbeab838b3f8) | 9 |
| cbBTC | 86% | [`0x2910f6b4ff92dacd6987a6bf74a4c6d15ed1f3acbde6d04fc8cf41c43bb5dbbf`](https://app.morpho.org/ethereum/market/0x2910f6b4ff92dacd6987a6bf74a4c6d15ed1f3acbde6d04fc8cf41c43bb5dbbf) | 2 |
| BOBO | 62.5% | [`0x74812bbebc266a8054473a62722aeab79ed54fd9f7f23ddb88dfe6af35ef6eb5`](https://app.morpho.org/ethereum/market/0x74812bbebc266a8054473a62722aeab79ed54fd9f7f23ddb88dfe6af35ef6eb5) | 3 |

Total counted liquidations across the markets above during this window: **186 liquidation events**. All `186` decoded markets use USDS as the loan asset; no WETH-, cbBTC-, or wstETH-denominated loan markets were present in the Morpho `Liquidate` logs for this window.

## First Example Liquidations

Examples of early liquidations after the scale-change update:

| Market | First observed liquidation block | Example liquidation transaction |
|---|---:|---|
| PEPE 77% | 25030092 | [`0x2cf791f65e96359acc6e955bdec3d4504886339f85b05f52db85d61d481052e8`](https://etherscan.io/tx/0x2cf791f65e96359acc6e955bdec3d4504886339f85b05f52db85d61d481052e8) |
| JOE 77% | 25030093 | [`0x8c91ce992b0db3c0dbb5df139cf64836ed48d7c74d48dab91fbac6088011c265`](https://etherscan.io/tx/0x8c91ce992b0db3c0dbb5df139cf64836ed48d7c74d48dab91fbac6088011c265) |
| SPX 77% | 25030093 | [`0xaf8c51f017331b810b4904a8ea91a6281532d1b795b445909827932a06b2792a`](https://etherscan.io/tx/0xaf8c51f017331b810b4904a8ea91a6281532d1b795b445909827932a06b2792a) |
| SPX 62.5% | 25030093 | [`0xd7332dd154064863e65d4c5b70666ce567c53823dd952c4d26fe473ceae34350`](https://etherscan.io/tx/0xd7332dd154064863e65d4c5b70666ce567c53823dd952c4d26fe473ceae34350) |
| cbBTC 86% | 25030094 | [`0xeae7fbcb2b1d13d07fe56697abf98b70227b1212e545a830f87249a4e9783f02`](https://etherscan.io/tx/0xeae7fbcb2b1d13d07fe56697abf98b70227b1212e545a830f87249a4e9783f02) |
| PEPE 62.5% | 25030100 | [`0xc2aad10fbf710e11b1011051726cd3b471238d0f1771c174751072523df24543`](https://etherscan.io/tx/0xc2aad10fbf710e11b1011051726cd3b471238d0f1771c174751072523df24543) |
| BOBO 62.5% | 25030122 | [`0xa8c08b01aecd3916110d57b2017816c4d77f67d36905408418668623bffbdd43`](https://etherscan.io/tx/0xa8c08b01aecd3916110d57b2017816c4d77f67d36905408418668623bffbdd43) |

## Interpretation

The evidence indicates that the incident was not limited to SPX/USDS. The DIA batch update pushed many DIA feeds down by approximately **10,000x**, and Morpho liquidations began immediately after.

The common pattern was:

1. DIA batch update at block `25030092` sets oracle feed values about `10,000x` lower.
2. Morpho adapter prices follow the scaled-down DIA values.
3. Positions become liquidatable immediately after the update: first in block `25030092` after the DIA update transaction, then more broadly in block `25030093`.
4. A later DIA update at block `25030777` restores the prior scale.

Return to the [main incident overview](README.md) or continue to [Appendix B: liquidation loss and liquidator extraction estimate](morpho-dia-liquidation-loss-estimate.md).
