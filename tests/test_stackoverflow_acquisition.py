#!/usr/bin/env python3
"""Offline HTTP tests for resumable Stack Overflow dump acquisition."""
import hashlib, http.server, pathlib, socketserver, tempfile, threading
from scripts.acquire_stackoverflow_dump import acquire, digest

PAYLOAD = (b"stack-overflow-dump-fixture-" * 97)
class Handler(http.server.BaseHTTPRequestHandler):
    mode = "range"
    def log_message(self, *args): pass
    def do_GET(self):
        rng = self.headers.get("Range")
        if rng and self.mode == "range":
            start = int(rng.removeprefix("bytes=").split("-",1)[0])
            data = PAYLOAD[start:]
            self.send_response(206)
            self.send_header("Content-Range",f"bytes {start}-{len(PAYLOAD)-1}/{len(PAYLOAD)}")
        else:
            data = PAYLOAD
            self.send_response(200)
        self.send_header("Content-Length",str(len(data)))
        self.end_headers()
        self.wfile.write(data)

class Server(socketserver.ThreadingMixIn, http.server.HTTPServer):
    daemon_threads=True

with tempfile.TemporaryDirectory() as tmp:
    with Server(("127.0.0.1",0),Handler) as server:
        thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
        url=f"http://127.0.0.1:{server.server_port}/fixture"
        path=pathlib.Path(tmp)/"dump.7z"
        acquire(url,path)
        assert path.read_bytes()==PAYLOAD
        assert digest(path)==hashlib.sha256(PAYLOAD).hexdigest()
        path.unlink()
        part=path.with_name(path.name+".part")
        part.write_bytes(PAYLOAD[:200])
        acquire(url,path)
        assert path.read_bytes()==PAYLOAD
        path.unlink()
        part.write_bytes(PAYLOAD[:200])
        Handler.mode="ignore"
        try:
            acquire(url,path)
        except RuntimeError as exc:
            assert "resume offset" in str(exc)
        else:
            raise AssertionError("ignored Range must fail closed")
        assert not path.exists() and part.read_bytes()==PAYLOAD[:200]
        server.shutdown()
print("HTTP acquisition fixture OK")
