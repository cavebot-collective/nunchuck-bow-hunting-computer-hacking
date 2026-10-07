#!/usr/bin/env python3
from __future__ import annotations
import importlib.util, math, pathlib, yaml

ROOT = pathlib.Path(__file__).parents[1]
spec = importlib.util.spec_from_file_location("projection", ROOT / "scripts" / "project_technology_concern.py")
m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
data = yaml.safe_load((ROOT / "fixtures" / "synthetic-controls.yaml").read_text())
profiles = {p["id"]: p for p in data["profiles"]}

def total_event_hours(p):
    return sum(e["hours"] for e in p["events"])

def concern_totals(result):
    out = {}
    for cell in result["cells"]:
        out[cell["concern"]] = out.get(cell["concern"], 0.0) + cell["hours"]
    return out

for pid, p in profiles.items():
    r = m.project_profile(p)
    assert math.isclose(r["total_hours"], total_event_hours(p), abs_tol=1e-8)
    assert math.isclose(sum(x["hours"] for x in r["cells"]), total_event_hours(p), abs_tol=1e-8)

backend = concern_totals(m.project_profile(profiles["backend-specialist"]))
full = concern_totals(m.project_profile(profiles["true-full-stack"]))
assert full.get("ui", 0) > backend.get("ui", 0) * 3
assert full.get("client", 0) > backend.get("client", 0) * 2
assert backend.get("distributed", 0) > full.get("distributed", 0) * 2

rust = m.project_profile(profiles["systems-veteran-new-rust"])
rust_cells = sum(c["hours"] for c in rust["cells"] if c["technology"] == "Rust")
assert math.isclose(rust_cells, 700.0, abs_tol=1e-8)

print("PASS: Technology × Concern conserves mass and separates control morphologies")
