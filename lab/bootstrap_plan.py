#!/usr/bin/env python3
"""No-install project-local environment planner and dependency doctor."""
from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
PROFILES = ROOT / "software-profiles.json"


def load_profiles() -> dict[str, object]:
    return json.loads(PROFILES.read_text())


def plan(groups: list[str]) -> dict[str, object]:
    profile = load_profiles()
    selected = {}
    for group in groups:
        if group not in profile["groups"]:
            raise ValueError(f"unknown dependency group: {group}")
        selected[group] = profile["groups"][group]
    return {
        "mode": "dry_run_only",
        "environmentPath": "lab/.venv",
        "groups": selected,
        "nextSteps": [
            "Resolve compatible versions from current upstream release metadata in an isolated branch.",
            "Record hashes from an actual resolver; do not fabricate a lockfile.",
            "Create lab/.venv without system-site-packages only after review.",
            "Install reviewed lock into lab/.venv; never use sudo or global pip/conda.",
        ],
        "commandsExecuted": [],
    }


def doctor() -> dict[str, object]:
    profile = load_profiles()
    status = {}
    for entries in profile["groups"].values():
        for entry in entries:
            module = entry["import"]
            if module:
                status[entry["name"]] = "available" if importlib.util.find_spec(module) else "not installed"
            else:
                status[entry["name"]] = "external/manual profile"
    return {"mode": "read_only_environment_doctor", "status": status, "mutations": []}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--group", action="append", choices=("core", "acquisition", "signal", "model", "edge"))
    parser.add_argument("--doctor", action="store_true")
    args = parser.parse_args()
    report = doctor() if args.doctor else plan(args.group or ["core"])
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
