#!/usr/bin/env python3
"""Deterministic Technology × Concern projection."""
from __future__ import annotations
import argparse, json, pathlib, yaml
from collections import defaultdict

ROOT = pathlib.Path(__file__).parents[1]
DEFAULT_INPUT = ROOT / "fixtures" / "synthetic-controls.yaml"
POLICIES = ("equal-split", "duplicate-association")

def project_profile(profile: dict, technology_policy: str = "equal-split") -> dict:
    if technology_policy not in POLICIES:
        raise ValueError(f"unknown technology allocation policy: {technology_policy}")
    cells = defaultdict(float)
    observed_total = sum(e["hours"] for e in profile.get("events", []))
    displayed_mass = 0.0
    for event in profile.get("events", []):
        technologies = event.get("technology", [])
        if not technologies:
            continue
        # This is a projection policy, never an evidentiary claim about how the
        # person's time was divided among simultaneously associated technologies.
        tech_share = 1.0 / len(technologies) if technology_policy == "equal-split" else 1.0
        for concern, weight in event.get("concern", {}).items():
            concern_hours = event["hours"] * weight
            for technology in technologies:
                mass = concern_hours * tech_share
                cells[(technology, concern)] += mass
                displayed_mass += mass
    return {
        "profile_id": profile["id"],
        "measure": "allocated_experience_hours",
        "technology_allocation_policy": technology_policy,
        "observed_event_hours": observed_total,
        "displayed_mass": displayed_mass,
        "mass_semantics": "conserved" if technology_policy == "equal-split" else "nonconserved_association_mass",
        "collapsed": ["phase", "chronology", "novelty", "autonomy"],
        "does_not_imply": ["proficiency", "recency", "transfer", "equal_difficulty_per_hour", "observed_technology_time_split"],
        "cells": [{"technology": t, "concern": c, "hours": round(h, 9)}
                  for (t, c), h in sorted(cells.items())],
    }

def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", type=pathlib.Path, default=DEFAULT_INPUT)
    ap.add_argument("--profile")
    ap.add_argument("--technology-policy", choices=POLICIES, default="equal-split")
    args = ap.parse_args()
    data = yaml.safe_load(args.input.read_text(encoding="utf-8"))
    profiles = data["profiles"]
    if args.profile:
        profiles = [p for p in profiles if p["id"] == args.profile]
        if not profiles:
            raise SystemExit(f"unknown profile: {args.profile}")
    print(json.dumps([project_profile(p, args.technology_policy) for p in profiles], indent=2, sort_keys=True))

if __name__ == "__main__":
    main()
