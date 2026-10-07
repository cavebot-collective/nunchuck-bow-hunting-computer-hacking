#!/usr/bin/env python3
"""Extract Stack Overflow taxonomy components from Stack Exchange dump XML."""
import argparse, csv, pathlib, xml.etree.ElementTree as ET

def rows(path):
    if not path: return
    for _,e in ET.iterparse(path,events=("end",)):
        if e.tag=="row": yield dict(e.attrib)
        e.clear()

def write(path, header, records):
    with path.open("w",newline="",encoding="utf-8") as f:
        w=csv.DictWriter(f,fieldnames=header,delimiter="\t",lineterminator="\n",extrasaction="ignore")
        w.writeheader(); w.writerows(records)

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--tags",required=True)
    ap.add_argument("--synonyms")
    ap.add_argument("--out",default="dist/stackoverflow-taxonomy")
    a=ap.parse_args(); out=pathlib.Path(a.out); out.mkdir(parents=True,exist_ok=True)
    write(out/"tags.tsv",["Id","TagName","Count","ExcerptPostId","WikiPostId"],rows(a.tags))
    if a.synonyms:
        write(out/"tag-synonyms.tsv",["Id","SourceTagName","TargetTagName","CreationDate","OwnerUserId","AutoRenameCount","LastAutoRename"],rows(a.synonyms))
    print(out)
if __name__=="__main__": main()
