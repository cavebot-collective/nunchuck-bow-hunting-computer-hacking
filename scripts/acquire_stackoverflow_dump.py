#!/usr/bin/env python3
"""Resumable, hash-attested Stack Exchange dump component download."""
import argparse, datetime, hashlib, json, pathlib, urllib.request, http.client

BASE="https://archive.org/download/stackexchange/"
COMPONENTS={"tags":"stackoverflow.com-Tags.7z","posts":"stackoverflow.com-Posts.7z"}
def digest(path):
    h=hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda:f.read(8*1024*1024),b""): h.update(chunk)
    return h.hexdigest()
def acquire(url,path):
    partial=path.with_name(path.name+".part")
    offset=partial.stat().st_size if partial.exists() else 0
    headers={"User-Agent":"nunchuck-skills-source-acquisition/0.1"}
    if offset: headers["Range"]=f"bytes={offset}-"
    req=urllib.request.Request(url,headers=headers)
    try:\n        response = urllib.request.urlopen(req,timeout=120)\n    except Exception:\n        raise\n    with response:
        status=response.status
        content_range=response.headers.get("Content-Range","")
        if offset and (status!=206 or not content_range.startswith(f"bytes {offset}-")):
            raise RuntimeError("Server did not honor exact resume offset; partial file retained")
        expected_length=response.headers.get("Content-Length")\n        expected_length=int(expected_length) if expected_length is not None else None\n        transferred=0\n        mode="ab" if offset else "wb"
        with partial.open(mode) as f:
            while True:
                chunk=response.read(8*1024*1024)
                if not chunk: break
                f.write(chunk)\n                transferred+=len(chunk)
        if expected_length is not None and transferred != expected_length:\n            raise IOError(f"Incomplete transfer: {transferred}/{expected_length} bytes; partial retained")\n    partial.replace(path)
def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("component",choices=COMPONENTS)
    ap.add_argument("--out",default="data/raw/stackoverflow")
    ap.add_argument("--url",help="Explicit immutable mirror URL; recorded in manifest")
    ap.add_argument("--sha256",help="Expected SHA-256 of compressed archive")
    a=ap.parse_args()
    out=pathlib.Path(a.out);out.mkdir(parents=True,exist_ok=True)
    path=out/COMPONENTS[a.component]
    url=a.url or BASE+COMPONENTS[a.component]
    if not path.exists(): acquire(url,path)
    sha=digest(path)
    if a.sha256 and sha.lower()!=a.sha256.lower():
        raise SystemExit(f"SHA-256 mismatch: expected {a.sha256}, got {sha}; archive retained for inspection")
    manifest={"source_id":"stackoverflow-data-dump","component":a.component,"source_url":url,
      "retrieved_at":datetime.datetime.now(datetime.timezone.utc).isoformat(),
      "sha256":sha,"bytes":path.stat().st_size,"file":path.name,
      "redistribution":"review","acquisition_method":"HTTP range-resumable download",
      "expected_sha256":a.sha256}
    (out/(path.name+".manifest.json")).write_text(json.dumps(manifest,indent=2)+"\n")
    print(json.dumps(manifest,indent=2))
if __name__=="__main__":main()
