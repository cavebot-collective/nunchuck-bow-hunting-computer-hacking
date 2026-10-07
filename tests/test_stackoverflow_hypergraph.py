#!/usr/bin/env python3
import csv, pathlib, subprocess, tempfile

root=pathlib.Path(__file__).resolve().parents[1]
with tempfile.TemporaryDirectory() as d:
    out=pathlib.Path(d)
    subprocess.run(["python",str(root/"scripts/derive_stackoverflow_hypergraph.py"),str(root/"tests/fixtures/Posts.xml"),"--out",str(out)],check=True)
    edges=list(csv.DictReader((out/"question-tag-hyperedges.tsv").open(),delimiter="\t"))
    assert len(edges)==3
    assert edges[0]["tags"]=="c#,unity,game-development"
    pairs=list(csv.DictReader((out/"tag-2grams.tsv").open(),delimiter="\t"))
    got={(r["tag1"],r["tag2"]):int(r["question_count"]) for r in pairs}
    assert got[("c#","unity")]==1
    assert got[("automated-reasoning","prolog")]==1
    triples=list(csv.DictReader((out/"tag-3grams.tsv").open(),delimiter="\t"))
    assert len(triples)==2
    assert (out/"tag-4grams.tsv").exists() and (out/"tag-5grams.tsv").exists()
print("Stack Overflow hypergraph fixture OK")
