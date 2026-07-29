#!/usr/bin/env python3
"""Validate split manifests against session/subject leakage policies."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

VALID_SPLITS = {"train", "validation", "test"}
VALID_POLICIES = {"held-out-session", "held-out-subject"}


def validate_manifest(manifest: dict[str, object]) -> list[str]:
    errors: list[str] = []
    policy = manifest.get("policy")
    records = manifest.get("records")
    if policy not in VALID_POLICIES:
        errors.append(f"policy must be one of {sorted(VALID_POLICIES)}")
    if not isinstance(records, list) or not records:
        return errors + ["records must be a non-empty array"]
    seen_ids: set[str] = set()
    session_splits: dict[tuple[str, str], set[str]] = {}
    subject_splits: dict[str, set[str]] = {}
    for index, record in enumerate(records):
        if not isinstance(record, dict):
            errors.append(f"record {index} must be an object")
            continue
        required = ("recordId", "subjectId", "sessionId", "split")
        for key in required:
            if not isinstance(record.get(key), str) or not record[key]:
                errors.append(f"record {index} missing string {key}")
        if any(key not in record for key in required):
            continue
        record_id = record["recordId"]
        if record_id in seen_ids:
            errors.append(f"duplicate recordId: {record_id}")
        seen_ids.add(record_id)
        split = record["split"]
        if split not in VALID_SPLITS:
            errors.append(f"invalid split for {record_id}: {split}")
            continue
        key = (record["subjectId"], record["sessionId"])
        session_splits.setdefault(key, set()).add(split)
        subject_splits.setdefault(record["subjectId"], set()).add(split)
    for key, splits in session_splits.items():
        if len(splits) > 1:
            errors.append(f"session leakage: subject/session {key} appears in {sorted(splits)}")
    if policy == "held-out-subject":
        for subject, splits in subject_splits.items():
            if "test" in splits and len(splits) > 1:
                errors.append(f"subject leakage: held-out test subject {subject} also appears in {sorted(splits - {'test'})}")
    present = {record.get("split") for record in records if isinstance(record, dict)}
    if "train" not in present or "test" not in present:
        errors.append("train and test records are required")
    if manifest.get("source") != "synthetic-fixture":
        errors.append("foundation split examples must declare source synthetic-fixture")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("manifest", type=Path)
    args = parser.parse_args()
    errors = validate_manifest(json.loads(args.manifest.read_text()))
    if errors:
        print("split validation failed:", *[f"- {error}" for error in errors], sep="\n")
        return 1
    print("split validation passed: no session/subject leakage under declared policy")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
