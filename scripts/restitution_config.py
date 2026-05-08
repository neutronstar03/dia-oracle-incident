"""Static configuration for restitution data generation."""

from __future__ import annotations

from dataclasses import dataclass


MORPHO = "0xBBBBBbbBBb9cC5e90e3b3Af64bdAF62C37EEFFCb"
DIA_ORACLE = "0xE1A3d58dc6C516Ef18628ce7E13cfE44B4Ac1552"

START_BLOCK = 25_030_092
END_BLOCK = 25_030_776
SNAPSHOT_BLOCK = 25_030_091

# Liquidate(bytes32,address,address,uint256,uint256,uint256,uint256,uint256)
LIQUIDATE_TOPIC0 = "0xa4946ede45d0c6f06a0f5ce92c9ad3b4751452d2fe0e25010783bcab57a67e41"


@dataclass(frozen=True)
class MarketConfig:
    collateral: str
    lltv: str
    feed: str


@dataclass(frozen=True)
class FeedConfig:
    collateral: str
    feed: str


MARKETS: dict[str, MarketConfig] = {
    "0xcbc21405c11c8eb13f1741bfba2a72dfbdab3cb525b79dc5b61148b1183b79a0": MarketConfig("PEPE", "62.5%", "PEPE/USD"),
    "0x5ffdf15c5a4d7c6affb3f12634eeda1a20e60b92c0eb547f61754f656b55841e": MarketConfig("PEPE", "77%", "PEPE/USD"),
    "0xef9f1e3e71483c9c9b61d2e27452e26507e52b547775ca899277b35585ef7b01": MarketConfig("JOE", "77%", "JOE/USD"),
    "0x38d28aa002b2961f734763f6afeeb78a36a9b947cb12b988c35a5bb4bde0d1c7": MarketConfig("JOE", "62.5%", "JOE/USD"),
    "0xc7d717f4052ac4e5463dcc58cea0f6b05dd7d8c67e0aee68ebe30a8af09b259f": MarketConfig("SPX", "77%", "SPX/USD"),
    "0x29200655ad6ee4b86a0f4132e86736844479b4f4ff55d0a40fb31e8264fb811c": MarketConfig("SPX", "62.5%", "SPX/USD"),
    "0x44f51e6b7356132597872e40c8d4a5bb2f1fc2c99e7292ee3b3953d9074086b6": MarketConfig("MOG", "62.5%", "MOG/USD"),
    "0x3f1d5c88c72432b04f2074499fe217468af49ddaa98bcb6ec80b08f76a82c6ec": MarketConfig("MOG", "77%", "MOG/USD"),
    "0xbd5cff99f6a6988399f1f95835186a46e4642c615bf6364c33027504514791f8": MarketConfig("SHIB", "62.5%", "SHIB/USD"),
    "0x1a01594467db83fefd93ad9028e3c13ca7f8499f7086afefb667966f6a2b3b11": MarketConfig("SHIB", "77%", "SHIB/USD"),
    "0xc26fb49a683ba55846974fe8283d63ab40dff0788c5ef4e79990426f080b60ec": MarketConfig("NEIRO", "77%", "NEIRO/USD"),
    "0x5fbb467c8f4f3a64ec8c3a58d04febbcce3eaec510f4dfaec5b1b57c8f189a14": MarketConfig("NEIRO", "62.5%", "NEIRO/USD"),
    "0xa5a49fa08443783f5a5cdc99b604033378f65148ec5cb6b2e718e801c4e7fe08": MarketConfig("IMF", "62.5%", "IMF/USD"),
    "0x0976b2b8e796994ef3e2fcc6c2f808c420917d531bb9cfaa4537773ca6860e1c": MarketConfig("IMF", "77%", "IMF/USD"),
    "0xce3a5f1bd26a980be6db1b7acc1a082413bb948d9b19fb4a92cfe5108ff2f275": MarketConfig("NPC", "77%", "NPC/USD"),
    "0x604e98b52f2375c5d3c6e92766c14174eb45ffbb61d36091f21277ae8930e42c": MarketConfig("NPC", "62.5%", "NPC/USD"),
    "0xa7ed1d25d22232695244bf63fdee33688d6d3540e569dd3d88919a7982ed1d7a": MarketConfig("REKT", "77%", "REKT/USD"),
    "0x973b23002efe233943715a2dfb98b66a0434d4b192b00bb4924230b3916433f7": MarketConfig("REKT", "62.5%", "REKT/USD"),
    "0x37997b3cf7cea3555abb101f94f39963e8256be71408165937d4fb7642039ac7": MarketConfig("APU", "62.5%", "APU/USD"),
    "0x347aa5f94a12dd46d3e17e542ca1c4033bd6952bde4b22af3caa33c82e52451a": MarketConfig("APU", "77%", "APU/USD"),
    "0xb1115c39bd889bbf0295e1482a50a3c3582bd08668fd73bedcbc26c3cb939225": MarketConfig("CULT", "62.5%", "CULT/USD"),
    "0x0655e0c8686d94d9e0c0d2b78d7f99492676e52d712db5ac061b3c78da4b7587": MarketConfig("CULT", "77%", "CULT/USD"),
    "0x9bdf55afe3832abff223c7d10b2af529b395ec2489e32d872156421c32ec7a5f": MarketConfig("BITCOIN", "62.5%", "BITCOIN/USD"),
    "0x81b97c7305aca46c62f2ffce63a09c6a4d647163e25f31c44fadcbeab838b3f8": MarketConfig("BITCOIN", "77%", "BITCOIN/USD"),
    "0x2910f6b4ff92dacd6987a6bf74a4c6d15ed1f3acbde6d04fc8cf41c43bb5dbbf": MarketConfig("cbBTC", "86%", "cbBTC/USD"),
    "0x74812bbebc266a8054473a62722aeab79ed54fd9f7f23ddb88dfe6af35ef6eb5": MarketConfig("BOBO", "62.5%", "BOBO/USD"),
}


PRICE_FEEDS = [
    FeedConfig("PEPE", "PEPE/USD"),
    FeedConfig("JOE", "JOE/USD"),
    FeedConfig("SPX", "SPX/USD"),
    FeedConfig("MOG", "MOG/USD"),
    FeedConfig("SHIB", "SHIB/USD"),
    FeedConfig("NEIRO", "NEIRO/USD"),
    FeedConfig("IMF", "IMF/USD"),
    FeedConfig("NPC", "NPC/USD"),
    FeedConfig("REKT", "REKT/USD"),
    FeedConfig("APU", "APU/USD"),
    FeedConfig("CULT", "CULT/USD"),
    FeedConfig("BITCOIN", "BITCOIN/USD"),
    FeedConfig("cbBTC", "cbBTC/USD"),
    FeedConfig("BOBO", "BOBO/USD"),
]
