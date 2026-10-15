"""Protocol-only utilities for future anti-cherry-picking replay evaluation.

No production route executes an evaluation or creates performance results. These
pure helpers make deterministic selection, cohort separation, and complete
outcome denominators testable with synthetic metadata before any new official
recording is selected or run.
"""
from __future__ import annotations

from collections import Counter
from hashlib import sha256
from pathlib import Path
from typing import Iterable, Mapping, Sequence
import json

ROOT = Path(__file__).resolve().parents[1]
PROTOCOL_PATH = ROOT / "evaluation-protocol.json"
OUTCOME_STATES = frozenset({"executed", "abstained", "error", "asset_failure"})


def load_protocol(path: Path = PROTOCOL_PATH) -> dict:
    value = json.loads(path.read_text(encoding="utf-8"))
    validate_protocol(value)
    return value


def validate_protocol(value: Mapping) -> None:
    if value.get("schema_version") != 1 or value.get("status") != "protocol_only_no_results":
        raise ValueError("evaluation protocol must remain a versioned protocol-only artifact")
    if value.get("execution_authorized") is not False or value.get("results") is not None:
        raise ValueError("evaluation protocol cannot authorize execution or contain results")
    source = value.get("source_scope", {})
    if "unknown" not in str(source.get("training_overlap", "")).lower():
        raise ValueError("training overlap must remain explicit until independently proved")
    selection = value.get("selection", {})
    if selection.get("algorithm") != "sha256_stratified_rank_v1" or selection.get("freeze_before_execution") is not True:
        raise ValueError("deterministic pre-execution freeze contract is missing")
    if selection.get("stratification_fields") != ["declared source split", "source session", "duration bin"]:
        raise ValueError("selection must retain the declared split, session, and duration strata")
    if selection.get("replacement_after_freeze") != "prohibited":
        raise ValueError("post-freeze replacement must be prohibited")
    cohorts = value.get("cohorts", {})
    if cohorts.get("development", {}).get("status") != "planned_not_selected":
        raise ValueError("development cohort must remain unselected in this cycle")
    if cohorts.get("evaluation", {}).get("status") != "planned_not_selected":
        raise ValueError("evaluation cohort must remain unselected in this cycle")
    if set(value.get("outcome_states", ())) != OUTCOME_STATES:
        raise ValueError("outcome states must retain executions, abstentions, errors, and asset failures")


def deterministic_rank(record_ids: Iterable[str], seed: str) -> tuple[str, ...]:
    """Return a stable output-blind rank for unique synthetic/private record IDs."""
    ids = tuple(record_ids)
    if not ids or len(set(ids)) != len(ids) or any(not item for item in ids):
        raise ValueError("record IDs must be non-empty and unique")
    return tuple(sorted(ids, key=lambda item: (sha256(f"{seed}\0{item}".encode()).digest(), item)))


def plan_disjoint_cohorts(
    record_strata: Mapping[str, Sequence[str]],
    *,
    seed: str,
    development_counts: Mapping[tuple[str, ...], int],
    evaluation_counts: Mapping[tuple[str, ...], int],
) -> dict[str, tuple[str, ...]]:
    """Plan explicit per-stratum cohorts without inspecting signals, labels, prompts, or outputs."""
    if not record_strata or any(len(stratum) != 3 or any(not value for value in stratum) for stratum in record_strata.values()):
        raise ValueError("every record must declare split, session, and duration-bin strata")
    normalized = {record_id: tuple(stratum) for record_id, stratum in record_strata.items()}
    strata = set(normalized.values())
    if set(development_counts) != strata or set(evaluation_counts) != strata:
        raise ValueError("cohort counts must explicitly cover every stratum")
    development: list[str] = []
    evaluation: list[str] = []
    for stratum in sorted(strata):
        development_count = development_counts[stratum]
        evaluation_count = evaluation_counts[stratum]
        members = (record_id for record_id, member_stratum in normalized.items() if member_stratum == stratum)
        stratum_seed = seed + "\0" + "\0".join(stratum)
        ranked = deterministic_rank(members, stratum_seed)
        if development_count < 0 or evaluation_count < 0 or development_count + evaluation_count > len(ranked):
            raise ValueError("per-stratum cohort counts must be non-negative and fit the source universe")
        development.extend(ranked[:development_count])
        evaluation.extend(ranked[development_count : development_count + evaluation_count])
    if not development or not evaluation:
        raise ValueError("development and evaluation cohorts must both be non-empty")
    if set(development) & set(evaluation):
        raise RuntimeError("development and evaluation cohorts overlap")
    return {"development": tuple(development), "evaluation": tuple(evaluation)}


def complete_outcome_counts(selected_ids: Iterable[str], outcomes: Mapping[str, str]) -> dict[str, int]:
    """Count all selected records and fail if an outcome or denominator member is missing."""
    selected = tuple(selected_ids)
    if not selected or len(set(selected)) != len(selected) or set(outcomes) != set(selected):
        raise ValueError("outcomes must cover every frozen selection exactly once")
    invalid = set(outcomes.values()) - OUTCOME_STATES
    if invalid:
        raise ValueError("unknown outcome state")
    counts = Counter(outcomes.values())
    result = {state: counts.get(state, 0) for state in sorted(OUTCOME_STATES)}
    result["total"] = len(selected)
    return result


def public_plan(value: Mapping) -> dict:
    """Return a no-result, no-private-identity browser summary."""
    validate_protocol(value)
    return {
        "version": value["protocol_version"],
        "status": "PROTOCOL ONLY · NO RESULTS",
        "execution_authorized": False,
        "question": value["question"],
        "selection": "Deterministic seeded selection, frozen before execution; post-freeze replacement prohibited.",
        "training_overlap": "Unknown; no cohort is labelled held out.",
        "denominator_policy": value["denominator_policy"],
        "allowed_reporting": list(value["allowed_reporting"]),
        "claim_boundary": value["claim_boundary"],
    }
