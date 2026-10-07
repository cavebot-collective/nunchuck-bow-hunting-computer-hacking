#!/usr/bin/env python3
"""Acquire a reproducible Wikidata technology-context snapshot via SPARQL."""
import argparse, datetime as dt, hashlib, json, pathlib, urllib.parse, urllib.request

ENDPOINT = "https://query.wikidata.org/sparql"
DEFAULT_ROOTS = {
    "programming-language": "Q9143",
    "integrated-development-environment": "Q13741",
    "game-engine": "Q193564",
    "database-management-system": "Q176165",
    "web-framework": "Q1330336",
    "operating-system": "Q9135",
}

def query(root):
    sparql=f"""SELECT DISTINCT ?item ?itemLabel ?instanceOf ?instanceOfLabel WHERE {{
      ?item wdt:P31/wdt:P279* wd:{root}.
      OPTIONAL {{ ?item wdt:P31 ?instanceOf. }}
      SERVICE wikibase:label {{ bd:serviceParam wikibase:language "en". }}
    }} ORDER BY ?item"""
    url=ENDPOINT+"?"+urllib.parse.urlencode({"query":sparql,"format":"json"})
    req=urllib.request.Request(url,headers={
      "Accept":"application/sparql-results+json",
      "User-Agent":"nunchuck-skills-dataset-factory/0.1 (https://github.com/cavebot-collective/nunchuck-bow-hunting-computer-hacking)"
    })
    with urllib.request.urlopen(req,timeout=120) as r: return json.load(r)["results"]["bindings"]

def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--out",default="dist/wikidata"); args=ap.parse_args()
    out=pathlib.Path(args.out); out.mkdir(parents=True,exist_ok=True)
    payload={"roots":DEFAULT_ROOTS,"results":{}}
    for name,qid in DEFAULT_ROOTS.items(): payload["results"][name]=query(qid)
    raw=json.dumps(payload,ensure_ascii=False,sort_keys=True,separators=(",",":")).encode()
    p=out/"technology-context.json"; p.write_bytes(raw)
    sha=hashlib.sha256(raw).hexdigest()
    count=sum(len(v) for v in payload["results"].values())
    manifest={"source_id":"wikidata","retrieved_at":dt.datetime.now(dt.timezone.utc).isoformat(),
      "upstream_version":None,"acquisition":{"method":"sparql","endpoint":ENDPOINT,"collector":"scripts/collect_wikidata.py"},
      "license":"CC0-1.0","redistribution":"allowed","record_count":count,
      "files":[{"path":p.name,"sha256":sha,"bytes":len(raw)}]}
    (out/"manifest.json").write_text(json.dumps(manifest,indent=2)+"\n")
    print(f"collected {count} bindings sha256={sha}")

if __name__=="__main__": main()
