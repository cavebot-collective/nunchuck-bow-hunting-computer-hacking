#!/usr/bin/env python3
"""Validate source registry invariants without third-party dependencies."""
import pathlib, re, sys

text=pathlib.Path("sources.yaml").read_text(encoding="utf-8")
blocks=re.split(r"(?m)^  - id: ",text)[1:]
seen=set(); errors=[]
valid={"candidate","implementing","implemented","blocked","retired"}
for raw in blocks:
    lines=raw.splitlines()
    sid=lines[0].strip()
    fields={}
    for line in lines[1:]:
        m=re.match(r"^    ([a-zA-Z0-9_-]+):\s*(.*)$",line)
        if m: fields[m.group(1)]=m.group(2).strip()
    if sid in seen: errors.append(f"duplicate source id: {sid}")
    seen.add(sid)
    if fields.get("status") not in valid: errors.append(f"{sid}: invalid/missing status")
    if not fields.get("name"): errors.append(f"{sid}: missing name")
    if not fields.get("kind"): errors.append(f"{sid}: missing kind")
    if "redistribution" not in fields: errors.append(f"{sid}: missing redistribution")
    if fields.get("status")=="implemented" and not fields.get("collector"):
        errors.append(f"{sid}: implemented source must name collector")
if errors:
    print("\n".join(errors),file=sys.stderr); raise SystemExit(1)
print(f"source registry OK: {len(seen)} sources")
