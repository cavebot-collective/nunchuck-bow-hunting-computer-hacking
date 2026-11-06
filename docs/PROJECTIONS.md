# Projection and interpretive-legend contract

## Principle

The experience model is not a visualization. A visualization is an explicitly lossy projection of evidence-backed experience data.

Every visible quantity MUST be traceable backward through its projection and composition to evidence. Every lossy transformation MUST be named.

## Projection contract

A projection is modeled as:

`P(M) -> (X, Y, measure, encodings, filters, aggregation, legend)`

- **X/Y** may be raw dimensions or documented derived functions.
- **measure** states what visual mass/position actually quantifies.
- **encodings** map additional dimensions to texture, shape, opacity, etc.
- **filters** identify excluded population/evidence.
- **aggregation** names dimensions collapsed or normalized away.
- **legend** states licensed and unlicensed interpretations.

Time is optional. It has no privileged axis.

## Interpretive legend

Each production SHOULD state:
- measure represented;
- taxonomy/version used for composite dimensions;
- allocation/normalization rule;
- preserved quantities;
- collapsed dimensions;
- excluded and unclassified mass;
- uncertainty / reconstruction mass;
- interpretations the projection supports;
- interpretations it does not support.

A static production is first-class, not a screenshot of an interactive view. Interactive views generalize independently useful static projections.

## Evidence boundary

Raw evidence records may contain candidate mappings (for example `candidate_concern`) but MUST NOT silently convert those candidates into fractional allocations or derived capability/depth values. Taxonomy resolution and allocation are downstream transformations with provenance.

## Initial visual laboratory

1. **Technology × Concern** — primary non-temporal footprint.
2. **Concern × Depth** — exposure/depth separation; depth is derived and provenance-bearing.
3. **Time × Concern** — career evolution where chronology is relevant.

Golden profiles and synthetic controls should be used to falsify the grammar: structurally different careers collapsing to effectively identical pictures is a visualization failure.
