# Source registry

`sources.yaml` is the canonical backlog and implementation registry for dataset integrations.

## Status

- **candidate** — worth investigating; no working collector is claimed.
- **implementing** — acquisition work exists but is not yet a reliable packaged source.
- **implemented** — reproducible acquisition and packaging exists.
- **blocked** — useful source with a documented access, licensing, or technical blocker.
- **retired** — intentionally no longer acquired.

A candidate entry is intentionally cheap: add identity, source kind, rationale, and known acquisition/licensing constraints. Do not require a collector or force the source into a premature common ontology.

## Packaging rule

Acquisition preserves source semantics. Each implemented collector emits an immutable raw snapshot plus a manifest with provenance, retrieval time, record count where meaningful, hashes, and redistribution status.

Normalization, competency decomposition, cross-source entity resolution, and visualization are downstream products and must not overwrite raw source data.
