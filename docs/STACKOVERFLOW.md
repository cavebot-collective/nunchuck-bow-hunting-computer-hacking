# Stack Overflow source products

The canonical Stack Overflow integration is the complete data dump, not a popularity-limited API sample.

## Preserve

- complete tag vocabulary
- tag usage counts when available
- tag synonyms
- tag wiki/excerpt semantic material when present in the upstream dump/source
- each question's complete tag set as a source-faithful hyperedge

## Derive without replacing source data

For every question tag set, emit unordered combinations of size 2 through 5 and aggregate their frequencies. Preserve the original question-level hyperedges so downstream work can distinguish true higher-order co-occurrence from pairwise projections.

Keep three evidence classes independently addressable:

1. taxonomy evidence — names, synonyms, wiki/excerpt semantics
2. relational evidence — question-level tag hyperedges and derived 2-5 combinations
3. prevalence evidence — marginal and combination frequencies

No frequency threshold determines taxonomy membership. Long-tail curated tags remain first-class evidence.
