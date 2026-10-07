#!/usr/bin/env python3
from __future__ import annotations
import importlib.util, math, pathlib, yaml
ROOT=pathlib.Path(__file__).parents[1]
spec=importlib.util.spec_from_file_location("phase_concern",ROOT/"scripts"/"project_phase_concern.py")
m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
data=yaml.safe_load((ROOT/"fixtures"/"synthetic-controls.yaml").read_text())
profiles={p["id"]:p for p in data["profiles"]}
for pid,p in profiles.items():
    r=m.project_profile(p)
    assert math.isclose(r["total_hours"],sum(e["hours"] for e in p["events"]),abs_tol=1e-8)
    assert len(r["phases"])==len(p["events"])
backend=m.project_profile(profiles["backend-specialist"])
ui_by_phase={c["phase"]:c["hours"] for c in backend["cells"] if c["concern"]=="ui"}
assert ui_by_phase.get("excursion",0)>0
assert all(v==0 for k,v in ui_by_phase.items() if k!="excursion")
assert "calendar_duration" in backend["does_not_imply"]
print("PASS: Phase × Concern conserves mass and isolates the backend UI excursion")
