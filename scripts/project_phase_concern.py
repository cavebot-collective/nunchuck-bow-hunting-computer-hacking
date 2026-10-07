#!/usr/bin/env python3
"""Phase × Concern projection for synthetic controls.

Phase is an ordered fixture coordinate, not fabricated calendar time.
"""
from __future__ import annotations
from collections import defaultdict

def project_profile(profile: dict) -> dict:
    cells = defaultdict(float)
    phases = []
    for ordinal, event in enumerate(profile.get("events", [])):
        phase = event["phase"]
        phases.append({"ordinal": ordinal, "phase": phase})
        for concern, weight in event["concern"].items():
            cells[(ordinal, phase, concern)] += event["hours"] * weight
    total = sum(cells.values())
    return {
        "profile_id": profile["id"],
        "x": "ordered_phase",
        "y": "concern",
        "measure": "allocated_experience_hours",
        "preserves": ["event_order", "phase", "concern", "hours"],
        "does_not_imply": ["calendar_duration", "equal_phase_duration", "proficiency", "recency_without_dates"],
        "total_hours": total,
        "phases": phases,
        "cells": [{"ordinal": o, "phase": p, "concern": c, "hours": round(h, 9)}
                  for (o, p, c), h in sorted(cells.items())],
    }
