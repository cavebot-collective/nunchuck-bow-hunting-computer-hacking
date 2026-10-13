# Synthetic-control acceptance criteria

These fixtures exist to test semantics before real-profile uncertainty is introduced.

## Invariants

1. **Conservation:** for every event, allocated concern-hours sum to event hours.
2. **No duration substitution:** phases have labels but no fabricated calendar duration.
3. **No technology inflation:** number of named technologies is never itself a capability/depth measure.
4. **No transfer laundering:** inherited/transfer evidence may affect a derived capability interpretation, but cannot increase direct technology hours.
5. **Projection honesty:** each rendered projection identifies what it aggregates away.
6. **Static sufficiency:** each primary projection must remain interpretable without interaction.

## Failure cases

The visual grammar fails if:
- backend-specialist and true-full-stack are visually indistinguishable in Technology × Concern;
- shallow-technology-hopper appears unambiguously deeper merely because more technologies are named;
- systems-veteran-new-rust is presented as having more than 700 direct Rust hours;
- omitting time makes the backend specialist's short UI excursion look like persistent full-stack balance;
- including time unnecessarily makes a lifetime Technology × Concern comparison materially harder to read;
- uncertainty/evidence status becomes visually confounded with capability magnitude.

## Projection-specific expectations

### Technology × Concern
Best initial static comparison. Preserve allocated hours; collapse chronology. Must expose what each technology was used *for*.

### Concern × Depth
Requires an explicit derived-depth function/version. Hours are an input, not depth. Until that function exists, implementations should render depth as unavailable rather than inventing it.

### Time × Concern
Use when evolution, transitions, excursions, or recency are the question. It is not the default representation of a career.
