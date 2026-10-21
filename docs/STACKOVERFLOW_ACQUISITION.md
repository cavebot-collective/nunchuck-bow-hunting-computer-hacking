# Stack Overflow dump acquisition

Canonical upstream component URLs:

- https://archive.org/download/stackexchange/stackoverflow.com-Tags.7z
- https://archive.org/download/stackexchange/stackoverflow.com-Posts.7z

Run `python scripts/acquire_stackoverflow_dump.py tags` for the relatively small taxonomy archive. Run `python scripts/acquire_stackoverflow_dump.py posts` only on a machine with adequate disk and bandwidth. The downloader writes `.part` files and resumes via HTTP Range; it fails closed if the server ignores the requested offset. Use `--sha256` with an independently established expected digest to enforce archive identity.

The script records the observed SHA-256, source URL, retrieval time, and byte count. Observed digests alone attest the downloaded bytes, not upstream authenticity. Preserve manifests and archive identities between runs.

After extraction, run `scripts/extract_stackoverflow_taxonomy.py` on Tags.xml, and `scripts/derive_stackoverflow_hypergraph.py` on Posts.xml. These are distinct lightweight and heavyweight stages; do not fetch Posts.7z on ordinary pull-request CI.

The availability of a separate TagSynonyms dump component has not been established. The synonym extractor's input remains optional and must be independently sourced and documented.

Tag wiki and excerpt post IDs from Tags.xml reference posts in Posts.xml; extracting their bodies and establishing licensing/redistribution requirements are follow-up tasks. Source data redistribution remains `review` until independently cleared.
