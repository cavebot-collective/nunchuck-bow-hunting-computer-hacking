#!/usr/bin/env python3
"""Deterministic Technology × Concern projection.

Measure: allocated synthetic experience-hours.
Preserves: technology/concern exposure mass.
Collapses: chronology, phase, novelty, autonomy.
Does not imply: proficiency, recency, transfer, equal difficulty per hour.
"""
from __future__ import annotations
import argparse, json, pathlib, yaml
from collections import defaultdict

ROOT = pathlib.Path(__file__).parents[1]
DEFAULT_INPUT = ROOT / "fixtures" / "synthetic-controls.yaml"

def project_profile(profile: dict) -> dict:
    cells = defaultdict(float)
    total = 0.0
    for event in profile.get("events", []):
        technologies = event.get("technology", [])
        if not technologies:
            continue
        # Technology association is non-exclusive in the evidence model. For this
        # projection we split event mass equally across co-listed technologies so
        # displayed cell mass remains conserved rather than multiplying hours.
        tech_share = 1.0 / len(technologies)
        for concern, weight in event.get("concern", {}).items():
            concern_hours = event["hours"] * weight
            for technology in technologies:
                cells[(technology, concern)] += concern_hours * tech_share
            total += concern_hours
    return {
        "profile_id": profile["id"],
        "measure": "allocated_experience_hours",
        "collapsed": ["phase", "chronology", "novelty", "autonomy"],
        "does_not_imply": ["proficiency", "recency", "transfer", "equal_difficulty_per_hour"],
        "total_hours": total,
        "cells": [
            {"technology": t, "concern": c, "hours": round(h, 9)}
            for (t, c), h in sorted(cells.items())
        ],
    }

def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", type=pathlib.Path, default=DEFAULT_INPUT)
    ap.add_argument("--profile")
    args = ap.parse_args()
    data = yaml.safe_load(args.input.read_text(encoding="utf-8"))
    profiles = data["profiles"]
    if args.profile:
        profiles = [p for p in profiles if p["id"] == args.profile]
        if not profiles:
            raise SystemExit(f"unknown profile: {args.profile}")
    print(json.dumps([project_profile(p) for p in profiles], indent=2, sort_keys=True))

if __name__ == "__main__":
    main()
