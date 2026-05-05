# Agent Notes

This repository documents and verifies an Ethereum mainnet incident. Agents may use the following local tools for read-only chain analysis and documentation support:

- Bun
- Python
- Foundry CLI, especially `cast`

Prefer `cast` for Ethereum mainnet reads when practical. If an RPC endpoint fails, try another public endpoint before changing the decoding logic. Endpoints that have been useful for this repo include:

1. `https://ethereum-rpc.publicnode.com`
2. `https://cloudflare-eth.com`
3. `https://rpc.flashbots.net`

Notes from prior work:

- `cast` is available in the environment.
- Flashbots JSON-RPC worked for `eth_getLogs` during prior checks.
- PublicNode returned `403` for at least one Python JSON-RPC request, although it may still work through `cast` for some methods.
