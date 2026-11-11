# Source registry

`sources.yaml` is the canonical backlog and implementation registry for dataset integrations.

## Status

- **candidate** — worth investigating; no working collector is claimed.
- **implementing** — acquisition work exists but is not yet a reliable packaged source.
- **implemented** — reproducible acquisition and packaging exists.
- **blocked** — useful source with a documented access, licensing, or technical blocker.
- **retired** — intentionally no longer acquired.

A candidate entry is intentionally cheap: add identity, source kind, rationale, and known acquisition/licensing constraints. Do not require a collector or force the source into a premature common ontology.

Researched candidates may also include `priority`, `technical_feasibility`, `acquisition`, `coverage`, `granularity`, `identifiers`, `relationships`, `evidence_types`, `independence`, `cadence`, `access_cost`, `terms_risk`, `rights`, `constraints`, and a `research` link. These source-specific fields are documented findings, not a promise that an adapter exists. The evidence and references are in [SOURCE_LANDSCAPE_RESEARCH.md](SOURCE_LANDSCAPE_RESEARCH.md).

Keep technical feasibility, access conditions, and reuse rights distinct. A public page, API, or download can make data technically observable without establishing a complete bulk route or permission to retain and redistribute a corpus. The `redistribution` field is a screening summary, not a license grant; follow the source-specific terms and rights notes.

## Packaging rule

Acquisition preserves source semantics. Each implemented collector emits an immutable raw snapshot plus a manifest with provenance, retrieval time, record count where meaningful, hashes, and redistribution status.

Normalization, competency decomposition, cross-source entity resolution, and visualization are downstream products and must not overwrite raw source data.

Every adapter should retain source-native identifiers, relation direction and type, exact endpoint or file and query/filters, retrieval time, upstream version, and governing reuse terms alongside content hashes. A hash establishes local byte identity, not upstream authenticity, licensing, or permission to redistribute.
