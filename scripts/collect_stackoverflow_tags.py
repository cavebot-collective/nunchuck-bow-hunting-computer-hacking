#!/usr/bin/env python3
import argparse, datetime as dt, hashlib, json, pathlib, time, urllib.parse, urllib.request

API = "https://api.stackexchange.com/2.3/tags"

def get(url):
    req = urllib.request.Request(url, headers={"User-Agent": "nunchuck-skills-dataset-factory/0.1"})
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.load(r)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="dist/stackoverflow-tags")
    ap.add_argument("--pagesize", type=int, default=100)
    args = ap.parse_args()
    out = pathlib.Path(args.out); out.mkdir(parents=True, exist_ok=True)
    items=[]; page=1
    while True:
        q=urllib.parse.urlencode({"site":"stackoverflow","page":page,"pagesize":args.pagesize,"order":"desc","sort":"popular"})
        payload=get(f"{API}?{q}")
        items.extend(payload.get("items", []))
        if not payload.get("has_more"): break
        if payload.get("backoff"): time.sleep(payload["backoff"])
        page += 1
    raw = json.dumps(items, ensure_ascii=False, sort_keys=True, separators=(",",":")).encode()
    data_path=out/"tags.json"; data_path.write_bytes(raw)
    sha=hashlib.sha256(raw).hexdigest()
    manifest={
      "source_id":"stackoverflow-tags",
      "retrieved_at":dt.datetime.now(dt.timezone.utc).isoformat(),
      "upstream_version":"Stack Exchange API 2.3",
      "acquisition":{"method":"api","endpoint":API,"collector":"scripts/collect_stackoverflow_tags.py"},
      "license":None,
      "redistribution":"review",
      "record_count":len(items),
      "files":[{"path":"tags.json","sha256":sha,"bytes":len(raw)}]
    }
    (out/"manifest.json").write_text(json.dumps(manifest, indent=2)+"\n", encoding="utf-8")
    print(f"collected {len(items)} tags sha256={sha}")

if __name__=="__main__": main()
