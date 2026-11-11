#!/usr/bin/env python3
"""Deterministic local HTTP tests for Stack Overflow dump acquisition."""

import hashlib
import http.server
import json
import pathlib
import socketserver
import tempfile
import threading
import time
import unittest
from unittest.mock import patch

from scripts import acquire_stackoverflow_dump as acquisition


PAYLOAD = bytes((index * 37 + index // 11) % 251 for index in range(768 * 1024 + 239))
ETAG = '"fixture-v1"'
CHUNK_SIZE = 64 * 1024


class FixtureState:
    def __init__(self):
        self.mode = "normal"
        self.requests = []
        self.body_prefix = CHUNK_SIZE + 71
        self.gate = False
        self.response_started = threading.Event()
        self.release_response = threading.Event()


class Handler(http.server.BaseHTTPRequestHandler):
    state = None
    protocol_version = "HTTP/1.1"

    def log_message(self, *_args):
        pass

    def do_GET(self):
        state = type(self).state
        range_header = self.headers.get("Range")
        state.requests.append(
            {
                "range": range_header,
                "if_range": self.headers.get("If-Range"),
                "accept_encoding": self.headers.get("Accept-Encoding"),
            }
        )
        if state.mode in ("interrupt", "truncate") and not range_header:
            self.send_response(200)
            declared_length = len(PAYLOAD) + 19 if state.mode == "truncate" else len(PAYLOAD)
            self.send_header("Content-Length", str(declared_length))
            self.send_header("ETag", ETAG)
            self.end_headers()
            self.wfile.write(PAYLOAD[: state.body_prefix])
            self.wfile.flush()
            self.close_connection = True
            return

        if range_header and state.mode in ("ignore-range", "changed-range"):
            data = PAYLOAD
            self.send_response(200)
            self.send_header("Content-Length", str(len(data)))
            self.send_header("ETag", '"fixture-v2"' if state.mode == "changed-range" else ETAG)
            self.end_headers()
            try:
                self.wfile.write(data)
            except OSError:
                pass
            return

        if range_header and state.mode == "malformed-range":
            start = int(range_header.removeprefix("bytes=").split("-", 1)[0])
            data = PAYLOAD[start:]
            self.send_response(206)
            self.send_header("Content-Range", "this is not a valid range")
            self.send_header("Content-Length", str(len(data)))
            self.send_header("ETag", ETAG)
            self.end_headers()
            try:
                self.wfile.write(data)
            except OSError:
                pass
            return

        if range_header:
            start = int(range_header.removeprefix("bytes=").split("-", 1)[0])
            if start >= len(PAYLOAD):
                self.send_response(416)
                self.send_header("Content-Range", f"bytes */{len(PAYLOAD)}")
                self.send_header("Content-Length", "0")
                self.send_header("ETag", ETAG)
                self.end_headers()
                return
            data = PAYLOAD[start:]
            self.send_response(206)
            self.send_header(
                "Content-Range", f"bytes {start}-{len(PAYLOAD) - 1}/{len(PAYLOAD)}"
            )
        else:
            data = PAYLOAD
            self.send_response(200)

        self.send_header("Content-Length", str(len(data)))
        self.send_header("ETag", ETAG)
        self.end_headers()
        if state.gate and not range_header:
            self.wfile.flush()
            state.response_started.set()
            state.release_response.wait(timeout=10)
        self.wfile.write(data)


class Server(socketserver.ThreadingMixIn, http.server.HTTPServer):
    daemon_threads = True
    allow_reuse_address = True

    def handle_error(self, _request, _client_address):
        # A rejected Range response can make the client close before this fixture
        # finishes writing the deliberately ignored full-body response.
        pass


class StackOverflowAcquisitionTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp_dir.cleanup)
        self.root = pathlib.Path(self.temp_dir.name)
        self.state = FixtureState()
        Handler.state = self.state
        self.server = Server(("127.0.0.1", 0), Handler)
        self.addCleanup(self._stop_server)
        self.server_thread = threading.Thread(
            target=self.server.serve_forever, daemon=True
        )
        self.server_thread.start()
        self.url = f"http://127.0.0.1:{self.server.server_port}/fixture.7z"
        self.path = self.root / "fixture.7z"
        self.chunk_patch = patch.object(acquisition, "CHUNK_SIZE", CHUNK_SIZE)
        self.chunk_patch.start()
        self.addCleanup(self.chunk_patch.stop)

    def _stop_server(self):
        self.state.release_response.set()
        self.server.shutdown()
        self.server.server_close()
        self.server_thread.join(timeout=5)

    @property
    def partial(self):
        return self.path.with_name(self.path.name + ".part")

    @property
    def partial_metadata(self):
        return self.path.with_name(self.path.name + ".part.json")

    @property
    def manifest_path(self):
        return self.path.with_name(self.path.name + ".manifest.json")

    def seed_interrupted_partial(self):
        self.state.mode = "interrupt"
        with self.assertRaises(acquisition.AcquisitionError):
            acquisition.acquire(self.url, self.path, component="fixture")
        self.assertGreater(self.partial.stat().st_size, 0)
        self.assertLess(self.partial.stat().st_size, len(PAYLOAD))
        self.assertTrue(self.partial_metadata.exists())
        self.assertFalse(self.path.exists())
        self.assertFalse(self.manifest_path.exists())

    def start_acquisition_thread(self, **kwargs):
        result = {}

        def target():
            try:
                result["manifest"] = acquisition.acquire(
                    self.url, self.path, component="fixture", **kwargs
                )
            except BaseException as exc:  # captured for assertion on the main test thread
                result["error"] = exc

        thread = threading.Thread(target=target, daemon=True)
        thread.start()
        return thread, result

    def test_fresh_download_writes_complete_manifest_and_observed_hash(self):
        manifest = acquisition.acquire(self.url, self.path, component="fixture")

        self.assertEqual(self.path.read_bytes(), PAYLOAD)
        self.assertEqual(manifest["acquisition_status"], "complete")
        self.assertEqual(manifest["transport_integrity"], "verified")
        self.assertEqual(manifest["bytes"], len(PAYLOAD))
        self.assertEqual(manifest["sha256"], hashlib.sha256(PAYLOAD).hexdigest())
        self.assertEqual(manifest["checksum_status"], "observed-only")
        self.assertEqual(manifest["authenticity_status"], "not-independently-established")
        self.assertEqual(manifest["transport"]["response_history"][0]["http_status"], 200)
        self.assertEqual(json.loads(self.manifest_path.read_text())["sha256"], manifest["sha256"])
        self.assertFalse(self.partial.exists())
        self.assertFalse(self.partial_metadata.exists())
        self.assertEqual(self.state.requests[0]["accept_encoding"], "identity")

    def test_interrupted_transfer_retains_resumable_bytes_without_success_marker(self):
        self.seed_interrupted_partial()

        self.assertEqual(self.partial.read_bytes(), PAYLOAD[: self.partial.stat().st_size])
        self.assertFalse(self.manifest_path.exists())
        self.assertFalse(self.path.exists())

    def test_range_resume_uses_exact_offset_validator_and_finishes(self):
        self.seed_interrupted_partial()
        offset = self.partial.stat().st_size
        self.state.mode = "normal"

        manifest = acquisition.acquire(self.url, self.path, component="fixture")

        self.assertEqual(self.path.read_bytes(), PAYLOAD)
        self.assertEqual(self.state.requests[-1]["range"], f"bytes={offset}-")
        self.assertEqual(self.state.requests[-1]["if_range"], ETAG)
        self.assertEqual(
            [item["http_status"] for item in manifest["transport"]["response_history"]],
            [200, 206],
        )
        self.assertEqual(
            [item["range_start"] for item in manifest["transport"]["response_history"]],
            [None, offset],
        )
        self.assertFalse(self.partial.exists())
        self.assertFalse(self.partial_metadata.exists())

    def test_full_sized_unconfirmed_partial_requires_matching_416_before_publication(self):
        self.partial.write_bytes(PAYLOAD)
        self.partial_metadata.write_text(
            json.dumps(
                {
                    "metadata_version": 2,
                    "source_url": self.url,
                    "component": "fixture",
                    "resolved_url": self.url,
                    "started_at": "2026-01-01T00:00:00+00:00",
                    "total_bytes": len(PAYLOAD),
                    "validator": {"header": "ETag", "value": ETAG},
                    "response_history": [
                        {
                            "http_status": 200,
                            "range_start": None,
                            "content_length_bytes": len(PAYLOAD),
                        }
                    ],
                    "response_content_length": len(PAYLOAD),
                    "response_content_range": None,
                    "length_evidence": "content-length",
                    "body_complete": False,
                }
            )
        )

        manifest = acquisition.acquire(self.url, self.path, component="fixture")

        self.assertEqual(self.state.requests[0]["range"], f"bytes={len(PAYLOAD)}-")
        self.assertEqual(self.state.requests[0]["if_range"], ETAG)
        self.assertEqual(self.path.read_bytes(), PAYLOAD)
        self.assertEqual(
            manifest["transport"]["response_history"][-1]["http_status"], 416
        )

    def test_ignored_range_response_preserves_partial_only_with_same_validator(self):
        self.seed_interrupted_partial()
        previous = self.partial.read_bytes()
        self.state.mode = "ignore-range"

        with self.assertRaisesRegex(acquisition.AcquisitionError, "ignored or declined Range"):
            acquisition.acquire(self.url, self.path, component="fixture")

        self.assertEqual(self.partial.read_bytes(), previous)
        self.assertTrue(self.partial_metadata.exists())
        self.assertFalse(self.path.exists())
        self.assertFalse(self.manifest_path.exists())

    def test_malformed_range_response_does_not_append_or_publish(self):
        self.seed_interrupted_partial()
        previous = self.partial.read_bytes()
        self.state.mode = "malformed-range"

        with self.assertRaisesRegex(acquisition.AcquisitionError, "malformed Content-Range"):
            acquisition.acquire(self.url, self.path, component="fixture")

        self.assertEqual(self.partial.read_bytes(), previous)
        self.assertTrue(self.partial_metadata.exists())
        self.assertFalse(self.path.exists())
        self.assertFalse(self.manifest_path.exists())

    def test_changed_representation_discards_partial(self):
        self.seed_interrupted_partial()
        self.state.mode = "changed-range"

        with self.assertRaisesRegex(acquisition.AcquisitionError, "validator changed"):
            acquisition.acquire(self.url, self.path, component="fixture")

        self.assertFalse(self.partial.exists())
        self.assertFalse(self.partial_metadata.exists())
        self.assertFalse(self.path.exists())
        self.assertFalse(self.manifest_path.exists())

    def test_truncated_body_never_publishes_and_keeps_safe_partial(self):
        self.state.mode = "truncate"

        with self.assertRaisesRegex(
            acquisition.AcquisitionError, "(truncated HTTP body|incomplete HTTP body)"
        ):
            acquisition.acquire(self.url, self.path, component="fixture")

        self.assertGreater(self.partial.stat().st_size, 0)
        self.assertLess(self.partial.stat().st_size, len(PAYLOAD))
        self.assertTrue(self.partial_metadata.exists())
        self.assertFalse(self.path.exists())
        self.assertFalse(self.manifest_path.exists())

    def test_checksum_mismatch_discards_partial_and_never_publishes(self):
        wrong_hash = "0" * 64

        with self.assertRaisesRegex(acquisition.AcquisitionError, "SHA-256 mismatch"):
            acquisition.acquire(
                self.url,
                self.path,
                expected_sha256=wrong_hash,
                component="fixture",
            )

        self.assertFalse(self.path.exists())
        self.assertFalse(self.manifest_path.exists())
        self.assertFalse(self.partial.exists())
        self.assertFalse(self.partial_metadata.exists())

    def test_invalid_cached_file_is_quarantined_before_replacement(self):
        self.path.write_bytes(b"stale or unproven cached bytes")
        self.state.gate = True
        thread, result = self.start_acquisition_thread()
        self.assertTrue(self.state.response_started.wait(timeout=5))
        deadline = time.monotonic() + 2
        while not self.partial.exists() and time.monotonic() < deadline:
            time.sleep(0.01)

        self.assertFalse(self.path.exists())
        self.assertFalse(self.manifest_path.exists())
        quarantined = list(self.root.glob("fixture.7z.invalid*"))
        self.assertEqual(len(quarantined), 1)
        self.assertEqual(quarantined[0].read_bytes(), b"stale or unproven cached bytes")

        self.state.release_response.set()
        thread.join(timeout=5)
        self.assertFalse(thread.is_alive())
        self.assertNotIn("error", result)
        self.assertEqual(self.path.read_bytes(), PAYLOAD)
        self.assertEqual(result["manifest"]["acquisition_status"], "complete")

    def test_corrupt_cached_file_is_rejected_and_refetched(self):
        acquisition.acquire(self.url, self.path, component="fixture")
        self.path.write_bytes(PAYLOAD + b"corruption")
        self.state.requests.clear()

        manifest = acquisition.acquire(self.url, self.path, component="fixture")

        self.assertEqual(self.path.read_bytes(), PAYLOAD)
        self.assertEqual(len(self.state.requests), 1)
        self.assertEqual(manifest["sha256"], hashlib.sha256(PAYLOAD).hexdigest())
        self.assertTrue(list(self.root.glob("fixture.7z.invalid*")))
        self.assertTrue(list(self.root.glob("fixture.7z.manifest.json.invalid*")))

    def test_cached_expected_hash_mismatch_fails_without_redownloading(self):
        acquisition.acquire(self.url, self.path, component="fixture")
        self.state.requests.clear()

        with self.assertRaisesRegex(acquisition.AcquisitionError, "cached SHA-256 mismatch"):
            acquisition.acquire(
                self.url,
                self.path,
                expected_sha256="0" * 64,
                component="fixture",
            )

        self.assertEqual(self.state.requests, [])
        self.assertEqual(self.path.read_bytes(), PAYLOAD)
        manifest = json.loads(self.manifest_path.read_text())
        self.assertIsNone(manifest["expected_sha256"])
        self.assertEqual(manifest["checksum_status"], "observed-only")

    def test_partial_without_stable_validator_is_discarded_before_fresh_fetch(self):
        self.partial.write_bytes(PAYLOAD[:100])
        self.partial_metadata.write_text(
            json.dumps(
                {
                    "metadata_version": 2,
                    "source_url": self.url,
                    "component": "fixture",
                    "resolved_url": self.url,
                    "started_at": "2026-01-01T00:00:00+00:00",
                    "total_bytes": len(PAYLOAD),
                    "validator": None,
                    "response_history": [{"http_status": 200, "range_start": None}],
                    "response_content_length": len(PAYLOAD),
                    "response_content_range": None,
                    "length_evidence": "content-length",
                    "body_complete": False,
                }
            )
        )

        acquisition.acquire(self.url, self.path, component="fixture")

        self.assertIsNone(self.state.requests[0]["range"])
        self.assertEqual(self.path.read_bytes(), PAYLOAD)
        self.assertFalse(self.partial.exists())

    def test_valid_cache_is_reused_and_later_expected_hash_is_recorded(self):
        first = acquisition.acquire(self.url, self.path, component="fixture")
        actual_hash = hashlib.sha256(PAYLOAD).hexdigest()
        request_count = len(self.state.requests)

        second = acquisition.acquire(
            self.url,
            self.path,
            expected_sha256=actual_hash,
            component="fixture",
        )

        self.assertEqual(len(self.state.requests), request_count)
        self.assertEqual(second["retrieved_at"], first["retrieved_at"])
        self.assertEqual(second["expected_sha256"], actual_hash)
        self.assertEqual(second["checksum_status"], "matched")
        self.assertEqual(second["authenticity_status"], "matched-user-supplied-sha256")

    def test_atomic_publication_keeps_final_names_absent_until_body_is_complete(self):
        self.state.gate = True
        thread, result = self.start_acquisition_thread()
        self.assertTrue(self.state.response_started.wait(timeout=5))
        deadline = time.monotonic() + 2
        while not self.partial.exists() and time.monotonic() < deadline:
            time.sleep(0.01)

        self.assertFalse(self.path.exists())
        self.assertFalse(self.manifest_path.exists())
        self.assertTrue(self.partial.exists())

        self.state.release_response.set()
        thread.join(timeout=5)
        self.assertFalse(thread.is_alive())
        self.assertNotIn("error", result)
        self.assertEqual(self.path.read_bytes(), PAYLOAD)
        self.assertTrue(self.manifest_path.exists())
        self.assertFalse(self.partial.exists())
        self.assertFalse(self.partial_metadata.exists())


if __name__ == "__main__":
    unittest.main()
