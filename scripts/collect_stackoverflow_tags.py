#!/usr/bin/env python3
"""Small Stack Exchange API smoke sample.

This is intentionally NOT the canonical Stack Overflow corpus collector.
The full taxonomy and question tag hyperedges come from the Stack Exchange
data dump so long-tail tags are never excluded by API pagination.
"""
import argparse, datetime as dt, hashlib, json, pathlib, urllib.parse, urllib.request

API = "https://api.stackexchange.com/2.3/tags"

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--out",default="dist/stackoverflow-tags-api-smoke")
    ap.add_argument("--pagesize",type=int,default=100)
    args=ap.parse_args()
    q=urllib.parse.urlencode({"site":"stackoverflow","page":1,"pagesize":args.pagesize,"order":"desc","sort":"popular"})
    req=urllib.request.Request(f"{API}?{q}",headers={"User-Agent":"nunchuck-skills-dataset-factory/0.1"})
    with urllib.request.urlopen(req,timeout=60) as r: payload=json.load(r)
    out=pathlib.Path(args.out); out.mkdir(parents=True,exist_ok=True)
    raw=json.dumps(payload,ensure_ascii=False,sort_keys=True,separators=(",",":")).encode()
    p=out/"page-1.json"; p.write_bytes(raw)
    sha=hashlib.sha256(raw).hexdigest()
    manifest={"source_id":"stackoverflow-tags-api-smoke","retrieved_at":dt.datetime.now(dt.timezone.utc).isoformat(),
      "upstream_version":"Stack Exchange API 2.3","acquisition":{"method":"api-smoke","endpoint":API,"collector":"scripts/collect_stackoverflow_tags.py"},
      "license":None,"redistribution":"review","record_count":len(payload.get("items",[])),
      "files":[{"path":p.name,"sha256":sha,"bytes":len(raw)}]}
    (out/"manifest.json").write_text(json.dumps(manifest,indent=2)+"\n")
    print(f"smoke sample {len(payload.get('items',[]))} tags sha256={sha}")
if __name__=="__main__": main()
