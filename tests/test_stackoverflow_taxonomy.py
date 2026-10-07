#!/usr/bin/env python3
import csv,pathlib,subprocess,tempfile
root=pathlib.Path(__file__).resolve().parents[1]
with tempfile.TemporaryDirectory() as d:
    out=pathlib.Path(d)
    subprocess.run(["python",str(root/"scripts/extract_stackoverflow_taxonomy.py"),"--tags",str(root/"tests/fixtures/Tags.xml"),"--synonyms",str(root/"tests/fixtures/TagSynonyms.xml"),"--out",str(out)],check=True)
    tags=list(csv.DictReader((out/"tags.tsv").open(),delimiter="\t"))
    syn=list(csv.DictReader((out/"tag-synonyms.tsv").open(),delimiter="\t"))
    assert [x["TagName"] for x in tags]==["c#","prolog"]
    assert syn[0]["SourceTagName"]=="c-sharp" and syn[0]["TargetTagName"]=="c#"
print("Stack Overflow taxonomy fixture OK")
