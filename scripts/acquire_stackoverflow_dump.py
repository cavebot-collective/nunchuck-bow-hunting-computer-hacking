#!/usr/bin/env python3
"""Acquire a Stack Exchange dump component with resumable, verified publication."""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import http.client
import json
import os
import pathlib
import re
import sys
import tempfile
import urllib.error
import urllib.parse
import urllib.request

BASE = "https://archive.org/download/stackexchange/"
COMPONENTS = {
    "tags": "stackoverflow.com-Tags.7z",
    "posts": "stackoverflow.com-Posts.7z",
}
CHUNK_SIZE = 1024 * 1024
MANIFEST_VERSION = 2
USER_AGENT = "nunchuck-skills-source-acquisition/0.2"


class AcquisitionError(RuntimeError):
    """The requested artifact could not be safely acquired or published."""


def digest(path: pathlib.Path) -> str:
    """Return the SHA-256 of a file, streaming so large dumps stay bounded in RAM."""
    hasher = hashlib.sha256()
    with pathlib.Path(path).open("rb") as stream:
        for chunk in iter(lambda: stream.read(CHUNK_SIZE), b""):
            hasher.update(chunk)
    return hasher.hexdigest()


def _utc_now() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat()


def _normalize_sha256(value: str | None) -> str | None:
    if value is None:
        return None
    normalized = value.strip().lower()
    if not re.fullmatch(r"[0-9a-f]{64}", normalized):
        raise AcquisitionError("--sha256 must contain exactly 64 hexadecimal characters")
    return normalized


def _read_json(path: pathlib.Path) -> dict | None:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError):
        return None
    return value if isinstance(value, dict) else None


def _fsync_directory(directory: pathlib.Path) -> None:
    """Best-effort directory fsync after rename; unsupported on some platforms."""
    if not hasattr(os, "O_DIRECTORY"):
        return
    try:
        descriptor = os.open(directory, os.O_RDONLY | os.O_DIRECTORY)
    except OSError:
        return
    try:
        os.fsync(descriptor)
    except OSError:
        pass
    finally:
        os.close(descriptor)


def _atomic_write_json(path: pathlib.Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(
        prefix=f".{path.name}.", suffix=".tmp", dir=path.parent
    )
    temporary = pathlib.Path(temporary_name)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as stream:
            json.dump(value, stream, indent=2, sort_keys=True)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
        _fsync_directory(path.parent)
    finally:
        temporary.unlink(missing_ok=True)


def _manifest_path(path: pathlib.Path) -> pathlib.Path:
    return path.with_name(path.name + ".manifest.json")


def _partial_paths(path: pathlib.Path) -> tuple[pathlib.Path, pathlib.Path]:
    return (
        path.with_name(path.name + ".part"),
        path.with_name(path.name + ".part.json"),
    )


def _unused_path(path: pathlib.Path) -> pathlib.Path:
    candidate = path.with_name(path.name + ".invalid")
    number = 1
    while candidate.exists():
        candidate = path.with_name(path.name + f".invalid.{number}")
        number += 1
    return candidate


def _quarantine(path: pathlib.Path) -> pathlib.Path | None:
    if not path.exists():
        return None
    destination = _unused_path(path)
    os.replace(path, destination)
    return destination


def _quarantine_cache(path: pathlib.Path) -> None:
    manifest = _manifest_path(path)
    # Remove the success marker first so an interrupted quarantine cannot leave a
    # manifest claiming that the artifact still at the canonical path is usable.
    if _quarantine(manifest):
        print(f"Quarantined invalid acquisition manifest: {manifest.name}", file=sys.stderr)
    if _quarantine(path):
        print(f"Quarantined invalid cached artifact: {path.name}", file=sys.stderr)


def _discard_partial(partial: pathlib.Path, metadata_path: pathlib.Path) -> None:
    partial.unlink(missing_ok=True)
    metadata_path.unlink(missing_ok=True)


def _valid_digest(value: object) -> bool:
    return isinstance(value, str) and re.fullmatch(r"[0-9a-f]{64}", value) is not None


def _verified_cache(
    path: pathlib.Path, url: str, component: str
) -> dict | None:
    manifest_path = _manifest_path(path)
    if not path.exists() and not manifest_path.exists():
        return None
    manifest = _read_json(manifest_path) if path.exists() else None
    valid = bool(
        manifest
        and manifest.get("manifest_version") == MANIFEST_VERSION
        and manifest.get("acquisition_status") == "complete"
        and manifest.get("transport_integrity") == "verified"
        and manifest.get("source_url") == url
        and manifest.get("component") == component
        and manifest.get("file") == path.name
        and type(manifest.get("bytes")) is int
        and _valid_digest(manifest.get("sha256"))
        and isinstance(manifest.get("transport"), dict)
        and manifest["transport"].get("expected_total_bytes") == manifest.get("bytes")
        and isinstance(manifest["transport"].get("response_history"), list)
        and bool(manifest["transport"]["response_history"])
    )
    if valid:
        actual_size = path.stat().st_size
        actual_digest = digest(path)
        valid = actual_size == manifest["bytes"] and actual_digest == manifest["sha256"]
        recorded_expected = manifest.get("expected_sha256")
        if recorded_expected is not None:
            valid = valid and _valid_digest(recorded_expected)
            valid = valid and recorded_expected == actual_digest
            valid = valid and manifest.get("checksum_status") == "matched"
            valid = valid and manifest.get("authenticity_status") == "matched-user-supplied-sha256"
        else:
            valid = valid and manifest.get("checksum_status") == "observed-only"
            valid = valid and manifest.get("authenticity_status") == "not-independently-established"
    if not valid:
        _quarantine_cache(path)
        return None
    return manifest


def _content_length(headers) -> int | None:
    values = headers.get_all("Content-Length", [])
    if not values:
        return None
    if len(values) != 1 or re.fullmatch(r"[0-9]+", values[0].strip()) is None:
        raise AcquisitionError("response has an invalid Content-Length header")
    return int(values[0])


def _header_value(headers, name: str) -> str:
    values = headers.get_all(name, [])
    if len(values) > 1:
        raise AcquisitionError(f"response has multiple {name} headers")
    return values[0] if values else ""


def _is_chunked(headers) -> bool:
    encodings = headers.get_all("Transfer-Encoding", [])
    if not encodings:
        return False
    tokens = [token.strip().lower() for value in encodings for token in value.split(",")]
    if tokens != ["chunked"]:
        raise AcquisitionError("response has an unsupported Transfer-Encoding")
    return True


def _validator(headers) -> dict | None:
    etag = _header_value(headers, "ETag")
    if etag:
        etag = etag.strip()
        if etag.startswith('"') and etag.endswith('"') and not etag.lower().startswith("w/"):
            return {"header": "ETag", "value": etag}
    modified = _header_value(headers, "Last-Modified")
    if modified:
        return {"header": "Last-Modified", "value": modified.strip()}
    return None


def _parse_content_range(value: str) -> tuple[int, int, int] | None:
    match = re.fullmatch(r"bytes (\d+)-(\d+)/(\d+)", value.strip())
    if not match:
        return None
    start, end, total = (int(part) for part in match.groups())
    if start > end or end >= total:
        return None
    return start, end, total


def _load_partial(
    partial: pathlib.Path, metadata_path: pathlib.Path, url: str, component: str
) -> dict | None:
    if not partial.exists():
        metadata_path.unlink(missing_ok=True)
        return None
    metadata = _read_json(metadata_path)
    try:
        size = partial.stat().st_size
    except OSError:
        _discard_partial(partial, metadata_path)
        return None
    structurally_valid = bool(
        metadata
        and metadata.get("metadata_version") == 2
        and metadata.get("source_url") == url
        and metadata.get("component") == component
        and isinstance(metadata.get("resolved_url"), str)
        and isinstance(metadata.get("started_at"), str)
        and type(metadata.get("total_bytes")) is int
        and metadata["total_bytes"] > 0
        and type(metadata.get("response_history")) is list
        and bool(metadata["response_history"])
        and metadata.get("length_evidence")
        and type(metadata.get("body_complete")) is bool
        and 0 < size <= metadata["total_bytes"]
    )
    if not structurally_valid:
        _discard_partial(partial, metadata_path)
        return None
    if metadata["body_complete"] and size != metadata["total_bytes"]:
        _discard_partial(partial, metadata_path)
        return None
    if not metadata["body_complete"]:
        validator = metadata.get("validator")
        if not (
            isinstance(validator, dict)
            and validator.get("header") in ("ETag", "Last-Modified")
            and isinstance(validator.get("value"), str)
            and validator["value"]
        ):
            _discard_partial(partial, metadata_path)
            return None
    return metadata


def _record_attempt(metadata: dict, status: int, range_start: int | None) -> None:
    metadata["response_history"].append(
        {
            "http_status": status,
            "range_start": range_start,
            "content_length_bytes": metadata.get("response_content_length"),
            "content_range": metadata.get("response_content_range"),
            "length_evidence": metadata.get("length_evidence"),
            "validator": metadata.get("validator"),
            "observed_at": _utc_now(),
        }
    )


def _make_manifest(
    *,
    path: pathlib.Path,
    url: str,
    resolved_url: str,
    component: str,
    expected_sha256: str | None,
    observed_sha256: str,
    byte_count: int,
    metadata: dict,
) -> dict:
    checksum_status = "matched" if expected_sha256 else "observed-only"
    return {
        "manifest_version": MANIFEST_VERSION,
        "acquisition_status": "complete",
        "source_id": "stackoverflow-data-dump",
        "component": component,
        "source_url": url,
        "resolved_url": resolved_url,
        "acquisition_started_at": metadata["started_at"],
        "retrieved_at": _utc_now(),
        "file": path.name,
        "bytes": byte_count,
        "sha256": observed_sha256,
        "expected_sha256": expected_sha256,
        "checksum_status": checksum_status,
        "authenticity_status": (
            "matched-user-supplied-sha256"
            if expected_sha256
            else "not-independently-established"
        ),
        "transport_integrity": "verified",
        "transport": {
            "expected_total_bytes": metadata["total_bytes"],
            "length_evidence": metadata["length_evidence"],
            "range_resumed": any(
                attempt["range_start"] is not None
                for attempt in metadata["response_history"]
            ),
            "response_history": metadata["response_history"],
            "validator": metadata.get("validator"),
            "content_encoding": "identity",
        },
        "redistribution": "review",
        "acquisition_method": "HTTP with validated Range resume",
    }


def _publish(
    *,
    partial: pathlib.Path,
    metadata_path: pathlib.Path,
    path: pathlib.Path,
    url: str,
    component: str,
    expected_sha256: str | None,
    metadata: dict,
) -> dict:
    byte_count = partial.stat().st_size
    if byte_count != metadata["total_bytes"]:
        raise AcquisitionError(
            f"refusing to publish {byte_count} bytes; expected {metadata['total_bytes']}"
        )
    observed_sha256 = digest(partial)
    if expected_sha256 and observed_sha256 != expected_sha256:
        _discard_partial(partial, metadata_path)
        raise AcquisitionError(
            "SHA-256 mismatch: "
            f"expected {expected_sha256}, got {observed_sha256}; "
            "the untrusted partial was discarded"
        )

    manifest = _make_manifest(
        path=path,
        url=url,
        resolved_url=metadata["resolved_url"],
        component=component,
        expected_sha256=expected_sha256,
        observed_sha256=observed_sha256,
        byte_count=byte_count,
        metadata=metadata,
    )
    with partial.open("rb+") as stream:
        os.fsync(stream.fileno())
    os.replace(partial, path)
    _fsync_directory(path.parent)
    try:
        _atomic_write_json(_manifest_path(path), manifest)
    except OSError as exc:
        raise AcquisitionError(
            f"artifact was moved to {path} but its success manifest could not be "
            "published; it is not a verified cache and will be quarantined next run"
        ) from exc
    metadata_path.unlink(missing_ok=True)
    return manifest


def _resume_complete_partial(
    *,
    partial: pathlib.Path,
    metadata_path: pathlib.Path,
    path: pathlib.Path,
    url: str,
    component: str,
    expected_sha256: str | None,
    metadata: dict,
) -> dict:
    return _publish(
        partial=partial,
        metadata_path=metadata_path,
        path=path,
        url=url,
        component=component,
        expected_sha256=expected_sha256,
        metadata=metadata,
    )


def acquire(
    url: str,
    path: pathlib.Path,
    expected_sha256: str | None = None,
    component: str | None = None,
) -> dict:
    """Acquire one artifact and return its manifest only after verified publication.

    A partial is resumed only when its URL, resolved URL, known total length, and
    stable HTTP validator still agree. Any successful result has a complete
    transport length and observed SHA-256. A supplied SHA-256 is an additional
    independent identity check; without one, authenticity is explicitly unverified.
    """
    path = pathlib.Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    expected_sha256 = _normalize_sha256(expected_sha256)
    component = component or "custom"
    parsed_url = urllib.parse.urlparse(url)
    if parsed_url.scheme not in ("http", "https") or not parsed_url.netloc:
        raise AcquisitionError("source URL must use HTTP or HTTPS")

    cached = _verified_cache(path, url, component)
    if cached:
        if expected_sha256 and cached["sha256"] != expected_sha256:
            raise AcquisitionError(
                f"cached SHA-256 mismatch: expected {expected_sha256}, "
                f"got {cached['sha256']}; cached artifact and provenance were retained"
            )
        if expected_sha256 and cached.get("expected_sha256") != expected_sha256:
            cached["expected_sha256"] = expected_sha256
            cached["checksum_status"] = "matched"
            cached["authenticity_status"] = "matched-user-supplied-sha256"
            cached["checksum_validated_at"] = _utc_now()
            _atomic_write_json(_manifest_path(path), cached)
        return cached

    partial, metadata_path = _partial_paths(path)
    metadata = _load_partial(partial, metadata_path, url, component)
    if metadata and metadata["body_complete"]:
        return _resume_complete_partial(
            partial=partial,
            metadata_path=metadata_path,
            path=path,
            url=url,
            component=component,
            expected_sha256=expected_sha256,
            metadata=metadata,
        )

    offset = partial.stat().st_size if metadata else 0
    headers = {
        "User-Agent": USER_AGENT,
        "Accept-Encoding": "identity",
    }
    if offset:
        headers["Range"] = f"bytes={offset}-"
        headers["If-Range"] = metadata["validator"]["value"]
    request = urllib.request.Request(url, headers=headers)

    try:
        response = urllib.request.urlopen(request, timeout=120)
    except urllib.error.HTTPError as exc:
        if offset and exc.code == 416:
            content_range = _header_value(exc.headers, "Content-Range")
            match = re.fullmatch(r"bytes \*/(\d+)", content_range.strip())
            if (
                _validator(exc.headers) != metadata.get("validator")
                or exc.geturl() != metadata["resolved_url"]
            ):
                _discard_partial(partial, metadata_path)
                raise AcquisitionError(
                    "range validation response changed or lost its validator; partial discarded"
                ) from exc
            if match and int(match.group(1)) != metadata["total_bytes"]:
                _discard_partial(partial, metadata_path)
                raise AcquisitionError(
                    "range validation reports a different archive length; partial discarded"
                ) from exc
            if match and int(match.group(1)) == offset == metadata["total_bytes"]:
                metadata["response_content_length"] = None
                metadata["response_content_range"] = content_range
                metadata["length_evidence"] = "content-range-unsatisfied"
                _record_attempt(metadata, 416, offset)
                metadata["body_complete"] = True
                _atomic_write_json(metadata_path, metadata)
                return _resume_complete_partial(
                    partial=partial,
                    metadata_path=metadata_path,
                    path=path,
                    url=url,
                    component=component,
                    expected_sha256=expected_sha256,
                    metadata=metadata,
                )
        raise AcquisitionError(f"HTTP request failed with status {exc.code}") from exc
    except (OSError, urllib.error.URLError) as exc:
        raise AcquisitionError(f"HTTP request failed: {exc}") from exc

    with response:
        status = response.getcode()
        resolved_url = response.geturl()
        try:
            content_encoding = _header_value(
                response.headers, "Content-Encoding"
            ).strip().lower()
            if content_encoding not in ("", "identity"):
                raise AcquisitionError(
                    f"refusing encoded response ({content_encoding}); byte ranges must address the archive bytes"
                )
            response_validator = _validator(response.headers)
            content_length = _content_length(response.headers)
            chunked = _is_chunked(response.headers)
            if content_length is not None and chunked:
                raise AcquisitionError(
                    "response contains both Content-Length and Transfer-Encoding; "
                    "body framing is ambiguous"
                )

            if offset:
                if status == 200:
                    if (
                        response_validator != metadata.get("validator")
                        or resolved_url != metadata["resolved_url"]
                    ):
                        _discard_partial(partial, metadata_path)
                        detail = "partial discarded because the representation validator changed or disappeared"
                    else:
                        detail = "validated partial retained for a later Range retry"
                    raise AcquisitionError(
                        f"server ignored or declined Range at byte {offset}; {detail}"
                    )
                if status != 206:
                    raise AcquisitionError(
                        f"expected HTTP 206 for Range resume, received {status}; partial retained"
                    )
                if response_validator != metadata.get("validator"):
                    _discard_partial(partial, metadata_path)
                    raise AcquisitionError(
                        "resume validator changed or disappeared; partial discarded"
                    )
                if resolved_url != metadata["resolved_url"]:
                    _discard_partial(partial, metadata_path)
                    raise AcquisitionError(
                        "resolved source URL changed during resume; partial discarded"
                    )
                content_range = _parse_content_range(
                    _header_value(response.headers, "Content-Range")
                )
                if content_range is None:
                    raise AcquisitionError(
                        "malformed Content-Range response; existing partial retained"
                    )
                start, end, total = content_range
                if start != offset or end != total - 1:
                    raise AcquisitionError(
                        "Content-Range does not exactly cover the requested remainder; "
                        "existing partial retained"
                    )
                if total != metadata["total_bytes"]:
                    _discard_partial(partial, metadata_path)
                    raise AcquisitionError(
                        "archive length changed during resume; partial discarded"
                    )
                expected_body_bytes = end - start + 1
                if content_length is not None and content_length != expected_body_bytes:
                    raise AcquisitionError(
                        "Content-Length disagrees with Content-Range; existing partial retained"
                    )
                total_bytes = total
                mode = "ab"
                metadata["response_content_length"] = content_length
                metadata["response_content_range"] = _header_value(
                    response.headers, "Content-Range"
                )
                metadata["length_evidence"] = (
                    "content-range+content-length"
                    if content_length is not None
                    else "content-range"
                )
            else:
                if status != 200:
                    raise AcquisitionError(
                        f"expected HTTP 200 for a fresh download, received {status}"
                    )
                if content_length is None and not chunked:
                    raise AcquisitionError(
                        "response has no verifiable body length or chunked framing"
                    )
                if content_length is not None and content_length <= 0:
                    raise AcquisitionError("response declared an empty archive")
                total_bytes = content_length
                expected_body_bytes = content_length
                mode = "wb"
                metadata = {
                    "metadata_version": 2,
                    "source_url": url,
                    "component": component,
                    "resolved_url": resolved_url,
                    "started_at": _utc_now(),
                    "total_bytes": total_bytes,
                    "validator": response_validator,
                    "response_history": [],
                    "response_content_length": content_length,
                    "response_content_range": None,
                    "length_evidence": (
                        "content-length" if content_length is not None else "chunked-framing"
                    ),
                    "body_complete": False,
                }

            if total_bytes is None:
                # A complete chunked response can be checked at this invocation, but
                # cannot be resumed after interruption without a known representation size.
                if offset:
                    raise AcquisitionError("resumed response has no known total length")
            elif total_bytes <= 0:
                raise AcquisitionError("response describes an empty archive")

            _record_attempt(metadata, status, offset if offset else None)
            _atomic_write_json(metadata_path, metadata)
            transferred = 0
            with partial.open(mode) as stream:
                try:
                    while True:
                        try:
                            chunk = response.read(CHUNK_SIZE)
                        except http.client.IncompleteRead as exc:
                            if exc.partial:
                                stream.write(exc.partial)
                                transferred += len(exc.partial)
                            raise AcquisitionError(
                                "truncated HTTP body; received bytes retained only as a resumable partial"
                            ) from exc
                        if not chunk:
                            break
                        stream.write(chunk)
                        transferred += len(chunk)
                finally:
                    stream.flush()
                    os.fsync(stream.fileno())

        except AcquisitionError:
            raise
        except (OSError, http.client.HTTPException, urllib.error.URLError) as exc:
            raise AcquisitionError(
                f"download interrupted; partial bytes retained where resumable: {exc}"
            ) from exc

    if expected_body_bytes is not None and transferred != expected_body_bytes:
        raise AcquisitionError(
            f"incomplete HTTP body: received {transferred} of {expected_body_bytes} bytes; "
            "partial retained where resumable"
        )
    final_size = partial.stat().st_size
    if total_bytes is not None and final_size != total_bytes:
        raise AcquisitionError(
            f"incomplete archive: received {final_size} of {total_bytes} bytes; "
            "partial retained where resumable"
        )
    if total_bytes is None:
        # A cleanly terminated chunked response has no declared total. The measured
        # size becomes the completed total for the manifest and future cache checks.
        total_bytes = final_size
        metadata["total_bytes"] = total_bytes
    if total_bytes <= 0:
        _discard_partial(partial, metadata_path)
        raise AcquisitionError("refusing to publish an empty archive")
    metadata["body_complete"] = True
    _atomic_write_json(metadata_path, metadata)

    return _publish(
        partial=partial,
        metadata_path=metadata_path,
        path=path,
        url=url,
        component=component,
        expected_sha256=expected_sha256,
        metadata=metadata,
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("component", choices=COMPONENTS)
    parser.add_argument("--out", default="data/raw/stackoverflow")
    parser.add_argument(
        "--url", help="Explicit HTTP(S) mirror URL; the requested and resolved URLs are recorded"
    )
    parser.add_argument(
        "--sha256", help="Expected SHA-256 of the archive, from an independent trusted source"
    )
    args = parser.parse_args()

    output = pathlib.Path(args.out)
    output.mkdir(parents=True, exist_ok=True)
    filename = COMPONENTS[args.component]
    url = args.url or BASE + filename
    manifest = acquire(
        url,
        output / filename,
        expected_sha256=args.sha256,
        component=args.component,
    )
    print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    try:
        main()
    except AcquisitionError as exc:
        raise SystemExit(f"acquisition failed: {exc}") from exc
