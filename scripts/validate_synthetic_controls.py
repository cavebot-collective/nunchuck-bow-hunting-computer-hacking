#!/usr/bin/env python3
"""Validate semantic invariants of synthetic capability fixtures."""
from __future__ import annotations
import math, pathlib, sys, yaml

PATH = pathlib.Path(__file__).parents[1] / "fixtures" / "synthetic-controls.yaml"
EPS = 1e-9

def fail(msg: str) -> None:
    print(f"FAIL: {msg}", file=sys.stderr)
    raise SystemExit(1)

data = yaml.safe_load(PATH.read_text(encoding="utf-8"))
profiles = data.get("profiles", [])
if not profiles:
    fail("no synthetic profiles")

seen = set()
for profile in profiles:
    pid = profile["id"]
    if pid in seen:
        fail(f"duplicate profile id: {pid}")
    seen.add(pid)
    for event in profile.get("events", []):
        hours = event.get("hours")
        if not isinstance(hours, (int, float)) or hours < 0:
            fail(f"{pid}/{event.get('phase')}: invalid hours")
        concern = event.get("concern", {})
        if not concern:
            fail(f"{pid}/{event.get('phase')}: empty concern allocation")
        total = sum(concern.values())
        if not math.isclose(total, 1.0, rel_tol=0.0, abs_tol=EPS):
            fail(f"{pid}/{event.get('phase')}: concern weights sum to {total}, not 1")
        allocated = sum(hours * weight for weight in concern.values())
        if not math.isclose(allocated, hours, rel_tol=0.0, abs_tol=EPS):
            fail(f"{pid}/{event.get('phase')}: allocated hours {allocated} != {hours}")

rust = next(p for p in profiles if p["id"] == "systems-veteran-new-rust")
direct_rust_hours = sum(
    e["hours"] for e in rust["events"] if "Rust" in e.get("technology", [])
)
if direct_rust_hours != 700:
    fail(f"Rust control must preserve 700 direct hours, got {direct_rust_hours}")

print(f"PASS: {len(profiles)} profiles; allocations conserved; direct Rust hours={direct_rust_hours}")
