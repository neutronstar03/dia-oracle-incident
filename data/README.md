# Generated Restitution Data

This directory contains generated inputs and tables for [`../suggested-restitution-plan.md`](../suggested-restitution-plan.md).

Canonical full-run files:

- `restitution-price-snapshot-25030091.json` / `.md`: DIA pre-incident price snapshot.
- `restitution-liquidation-events.json`: decoded incident liquidation events with event-level restitution values.
- `borrower-restitution-by-borrower-market.json` / `.md`: borrower restitution grouped by borrower and market.
- `borrower-restitution-by-borrower.json` / `.md`: borrower restitution grouped by borrower.
- `lender-bad-debt-by-market.json` / `.md`: lender-side bad debt grouped by market.
- `lender-bad-debt-by-lender-market.json` / `.md`: market bad debt allocated to snapshot lenders by market.
- `lender-bad-debt-by-lender.json` / `.md`: allocated lender bad debt grouped by lender.

The lender allocation script may create intermediate cache/checkpoint files such as `lender-candidates-by-market.json` and `lender-positive-positions-by-market.json`. Those files are intentionally not part of the canonical data set: they are reproducibility aids for interrupted RPC runs and can be regenerated from an archive-capable Ethereum RPC endpoint.

Temporary test-mode files are prefixed with `test-` and are safe to delete after script checks.

Regeneration commands are documented in [`../restitution-technical-methodology.md`](../restitution-technical-methodology.md).
