#!/usr/bin/env python3
"""Run DPIP examination execution with causal proposition matching enforced.

This compatibility wrapper keeps the existing examination machinery intact while
requiring mechanism-specific FAIL results to carry proposition-matching causal
attribution. It also keeps repository-native diagnostic fixtures subordinate to
explicit, attributable runtime evidence and independently detects stable nested
binder leaves in A/B runtime surfaces.
"""
from __future__ import annotations

from typing import Any

import examination_execute as execution
from causal_attribution import causal_judgment, self_test as causal_self_test

_original_build_execution = execution.build_execution
_original_judgment = execution.evidence_ready_judgment
_BINDER_TOKENS = ("fingerprint", "identifier", "binder", "handle", "digest")


def _required_runtime_complete(record: dict[str, Any], setup: dict[str, Any]) -> bool:
    required = set(execution.required_ids(setup))
    accepted = set(record.get("satisfied_evidence_requirement_ids", []) or [])
    if not required or required != accepted.intersection(required):
        return False
    required_failures = [
        failure for failure in record.get("evidence_sufficiency_failures", []) or []
        if str(failure.get("requirement_id") or "") in required
    ]
    return not required_failures and not (record.get("required_evidence") or [])


def build_execution(issue_number: int, setup: dict[str, Any]) -> dict[str, Any]:
    """Do not let repository-native diagnostics veto complete runtime evidence."""
    result = _original_build_execution(issue_number, setup)
    record = result["execution_evidence"]
    if _required_runtime_complete(record, setup):
        diagnostic_missing = [
            item for item in record.get("missing_evidence", []) or []
            if item.startswith("no unique repository observation fixture for ")
            or item.startswith("no executable_evaluation rules for ")
            or item.startswith("execution failed for ")
        ]
        nondiagnostic_missing = [
            item for item in record.get("missing_evidence", []) or []
            if item not in diagnostic_missing
        ]
        if not nondiagnostic_missing:
            record["status"] = "evidence-ready"
            record["diagnostic_gaps"] = diagnostic_missing
            record["missing_evidence"] = []
            record["human_acceptance_required"] = False
    return result


def _scalar_leaves(value: Any, path: tuple[str, ...] = ()) -> dict[tuple[str, ...], Any]:
    leaves: dict[tuple[str, ...], Any] = {}
    if isinstance(value, dict):
        for key, child in value.items():
            leaves.update(_scalar_leaves(child, path + (str(key),)))
    elif not isinstance(value, (list, tuple, set)) and not isinstance(value, bool) and value is not None:
        leaves[path] = value
    return leaves


def _binder_path(path: tuple[str, ...]) -> bool:
    lowered = ".".join(path).lower()
    return any(token in lowered for token in _BINDER_TOKENS)


def discovered_stable_binders(binding: dict[str, Any]) -> list[dict[str, Any]]:
    """Find equal binder-like scalar leaves across unrelated A/B runtime contexts."""
    findings: list[dict[str, Any]] = []
    surfaces = binding.get("surfaces")
    if not isinstance(surfaces, dict):
        return findings
    for surface_name, surface in surfaces.items():
        if not isinstance(surface, dict) or "context_a" not in surface or "context_b" not in surface:
            continue
        a_leaves = _scalar_leaves(surface.get("context_a"), (str(surface_name),))
        b_leaves = _scalar_leaves(surface.get("context_b"), (str(surface_name),))
        for path in sorted(set(a_leaves) & set(b_leaves)):
            a_value = a_leaves[path]
            b_value = b_leaves[path]
            if not _binder_path(path) or a_value != b_value or a_value in ("", None):
                continue
            findings.append({
                "requirement_id": binding.get("requirement_id"),
                "path": ".".join(path),
                "value": a_value,
                "classification": "cross-context-stable-binder",
            })
    return findings


def evidence_ready_judgment(record, setup):
    result = _original_judgment(record, setup)

    accepted = set(record.get("satisfied_evidence_requirement_ids", []) or [])
    bindings = [
        item for item in setup.get("provided_evidence", []) or []
        if isinstance(item, dict) and str(item.get("requirement_id") or "") in accepted
    ]

    # Independently inspect privacy-safe A/B values. A producer-level detector may
    # report no join while still exporting an equal durable binder nested inside a
    # larger context object. DPIP must not normalize that observation away.
    stable_binders = [finding for binding in bindings for finding in discovered_stable_binders(binding)]
    if stable_binders:
        result["outcome"] = "FAIL"
        result["reason_code"] = "prohibited-correlation-observed"
        result["residual_risk"] = (
            "At least one privacy-safe binder-like value is identical across unrelated A/B contexts, "
            "creating a directly evidenced cross-context join surface within the admitted scope."
        )
        result["action_required"] = (
            "Treat the scoped unlinkability proposition as failed for this pinned epoch; remove, "
            "context-bind, rotate, or otherwise prevent reuse of the discovered stable binder before rerun."
        )
        result.setdefault("details", {})["dpip_discovered_stable_binders"] = stable_binders
        result["details"]["source_detector_observation_preserved"] = [
            {
                "requirement_id": binding.get("requirement_id"),
                "observed_join": (binding.get("experiment") or {}).get("observed_join"),
            }
            for binding in bindings
        ]
        return result

    if result.get("outcome") != "FAIL" or result.get("reason_code") != "prohibited-correlation-observed":
        return result

    causal_results = [causal_judgment(binding) for binding in bindings]

    # A mechanism-specific FAIL is allowed only when at least one failed binding
    # establishes a cause that explicitly matches the proposition under examination.
    if any(item.get("outcome") == "FAIL" and item.get("terminal_for_proposition") for item in causal_results):
        result.setdefault("details", {})["causal_attribution"] = causal_results
        return result

    result["outcome"] = "INDETERMINATE"
    result["reason_code"] = "causal-attribution-insufficient"
    result["residual_risk"] = (
        "A prohibited cross-context effect was observed, but the supplied evidence does not establish "
        "that the mechanism named by the examined proposition caused that effect."
    )
    result["action_required"] = (
        "Preserve the observed effect and separately assess the evidenced causal mechanism. "
        "Do not attribute the effect to this proposition until a fresh pinned evidence package establishes proposition-matching causality."
    )
    result.setdefault("details", {})["causal_attribution"] = causal_results
    result["details"]["excluded_inference"] = (
        "Observed common values across contexts do not by themselves prove that the examined mechanism independently created the cross-context join."
    )
    return result


def self_test() -> None:
    causal_self_test()

    base_binding = execution._binding("ER-STATUS-AB")
    base_binding["surfaces"] = {
        "last_sent_profile": {
            "classification": "fresh",
            "context_a": {"state": "refused", "profile_fingerprint": "sha256:same"},
            "context_b": {"state": "refused", "profile_fingerprint": "sha256:same"},
            "execution_source": "runtime-persistence",
            "observer": "A/B",
        },
        "retention_boundary": {
            "classification": "fresh",
            "context_a": {"application_retained": True},
            "context_b": {"application_retained": True},
            "execution_source": "runtime-persistence",
            "observer": "A/B",
        },
    }
    found = discovered_stable_binders(base_binding)
    assert [item["path"] for item in found] == ["last_sent_profile.profile_fingerprint"], found

    distinct = dict(base_binding)
    distinct["surfaces"] = {
        "last_sent_profile": {
            "classification": "fresh",
            "context_a": {"state": "refused", "profile_fingerprint": "sha256:a"},
            "context_b": {"state": "refused", "profile_fingerprint": "sha256:b"},
            "execution_source": "runtime-persistence",
            "observer": "A/B",
        }
    }
    assert discovered_stable_binders(distinct) == []

    setup = {
        "candidate_interactions": ["C4"],
        "candidate_profiles": ["PP-4"],
        "evidence_requirement_ids": ["ER-VETTING-DISCOVERY-AB"],
        "provided_evidence": [execution._binding("ER-VETTING-DISCOVERY-AB")],
        "source_pins": [],
    }
    wrapped = build_execution(259, setup)["execution_evidence"]
    assert wrapped["status"] == "evidence-ready", wrapped
    assert any("C4" in item for item in wrapped.get("diagnostic_gaps", [])), wrapped


execution.build_execution = build_execution
execution.evidence_ready_judgment = evidence_ready_judgment

if __name__ == "__main__":
    self_test()
    execution.main()
