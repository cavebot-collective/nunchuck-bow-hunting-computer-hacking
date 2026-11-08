# Stack Overflow dump acquisition

## Sources and commands

Canonical upstream component URLs:

- <https://archive.org/download/stackexchange/stackoverflow.com-Tags.7z>
- <https://archive.org/download/stackexchange/stackoverflow.com-Posts.7z>

Acquire the relatively small taxonomy archive with:

```sh
python scripts/acquire_stackoverflow_dump.py tags
```

Acquire `posts` only on a machine with adequate disk space and bandwidth. Tests use a small local HTTP fixture; they never download the complete Posts archive. An alternate HTTP(S) mirror can be selected with `--url`. The exact requested URL and the final URL after redirects are recorded.

If a SHA-256 value from an independent, trusted source is available, require it with:

```sh
python scripts/acquire_stackoverflow_dump.py tags --sha256 <64-hex-digest>
```

The command always computes SHA-256 over the exact archive bytes it publishes. A supplied `--sha256` is compared before publication. Without that independent value, the manifest says `checksum_status: observed-only` and `authenticity_status: not-independently-established`: the observed digest identifies the bytes locally, but does not prove who served them.

## Files, recovery, and publication

The downloader stages bytes in `<archive>.part` and stores resume metadata in `<archive>.part.json`. A final archive is acquired only when the canonical archive and its `<archive>.manifest.json` both exist and the manifest says `acquisition_status: complete`. “Complete” means HTTP framing and the declared body length were checked and SHA-256 was computed; it does not imply independent authenticity unless `--sha256` was supplied and matched. The archive is moved into place atomically only after these checks pass; the success manifest is then written through its own atomic rename. Failed transfers never write a success manifest.

Resume is attempted only when the partial belongs to the same requested and resolved URL, has a known total size, and has a stable strong ETag or Last-Modified validator. The request sends `Range` and `If-Range`; the response must be HTTP 206, carry the same validator, and cover exactly the remaining byte interval with the same total size. Encoded responses are refused so byte offsets always refer to archive bytes. Fresh responses require a valid Content-Length or correctly terminated chunked framing; close-delimited and ambiguously framed bodies are refused.

Safe partials are retained after a connection interruption, a truncated body, a transient server error, or an ignored/malformed Range response. They are never appended to unless the next response passes all resume checks. A partial is discarded when its metadata is missing or malformed, the URL or representation validator changes or disappears, the total size changes, no validator was available for an incomplete response, or a supplied SHA-256 mismatches. A changed representation must be fetched again from byte zero. If a server ignores Range but returns the same validator and URL, the partial is retained for a later retry; a changed or missing validator causes it to be discarded.

An existing archive without a valid version 2 manifest, with bytes that disagree with its recorded size or SHA-256, or with provenance for a different URL/component is moved to a sibling `.invalid` file before a new fetch begins. Older manifests are not accepted as proof of complete transfer. Inspect or remove quarantined files manually after confirming they are no longer needed.

The manifest records requested and resolved URLs, acquisition start and completion times, response statuses and range offsets, length evidence, validator, byte count, observed SHA-256, and whether an independent expected SHA-256 matched. A manifest checksum is a local integrity record; it is not signed and is not an independent chain of custody.

## Downstream processing

After extraction, run `scripts/extract_stackoverflow_taxonomy.py` on Tags.xml and `scripts/derive_stackoverflow_hypergraph.py` on Posts.xml. These are separate lightweight and heavyweight stages; do not fetch Posts.7z on ordinary pull-request CI.

The availability of a separate TagSynonyms dump component has not been established. The synonym extractor's input remains optional and must be independently sourced and documented.

Tag wiki and excerpt post IDs from Tags.xml reference posts in Posts.xml; extracting their bodies and establishing licensing/redistribution requirements are follow-up tasks. Source data redistribution remains `review` until independently cleared.
