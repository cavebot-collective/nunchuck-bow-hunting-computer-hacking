#!/usr/bin/env python3
"""Stream Stack Overflow Posts.xml into lossless tag hyperedges + n-gram counts."""
import argparse, collections, csv, itertools, pathlib, xml.etree.ElementTree as ET

def tags(raw):
    # Stack Exchange dump encodes Tags as <tag-a><tag-b>...
    return tuple(x for x in raw.replace("><","|").strip("<>").split("|") if x)

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("posts_xml")
    ap.add_argument("--out",default="dist/stackoverflow-derived")
    args=ap.parse_args()
    out=pathlib.Path(args.out); out.mkdir(parents=True,exist_ok=True)
    counts={n:collections.Counter() for n in range(2,6)}
    tag_counts=collections.Counter()
    questions=0
    with (out/"question-tag-hyperedges.tsv").open("w",newline="",encoding="utf-8") as hf:
        w=csv.writer(hf,delimiter="\t",lineterminator="\n"); w.writerow(["question_id","tags"])
        for _,elem in ET.iterparse(args.posts_xml,events=("end",)):
            if elem.tag!="row": continue
            if elem.attrib.get("PostTypeId")=="1":
                ts=tags(elem.attrib.get("Tags",""))
                if ts:
                    questions+=1; w.writerow([elem.attrib["Id"],",".join(ts)])
                    tag_counts.update(ts)
                    for n in range(2,min(5,len(ts))+1):
                        counts[n].update(itertools.combinations(sorted(set(ts)),n))
            elem.clear()
    with (out/"tag-counts.tsv").open("w",newline="",encoding="utf-8") as f:
        w=csv.writer(f,delimiter="\t",lineterminator="\n"); w.writerow(["tag","question_count"])
        w.writerows(sorted(tag_counts.items()))
    for n,c in counts.items():
        with (out/f"tag-{n}grams.tsv").open("w",newline="",encoding="utf-8") as f:
            w=csv.writer(f,delimiter="\t",lineterminator="\n")
            w.writerow([*(f"tag{i}" for i in range(1,n+1)),"question_count"])
            for combo,count in sorted(c.items()): w.writerow([*combo,count])
    print(f"questions={questions} unique_tags={len(tag_counts)} " + " ".join(f"{n}grams={len(c)}" for n,c in counts.items()))
if __name__=="__main__": main()
