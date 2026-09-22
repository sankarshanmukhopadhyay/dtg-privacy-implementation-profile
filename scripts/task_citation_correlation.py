#!/usr/bin/env python3
"""Map Interop Lab task-citation evidence into a bounded DPIP observability result.

Issue: #271
RAHP coordination: sankarshanmukhopadhyay/rahp-toolkit#690
Interop producer: sankarshanmukhopadhyay/trust-protocol-interop-lab#233

The mapper is intentionally conservative:

- fixture-only support never becomes a privacy PASS;
- unavailable or unobservable runtime evidence remains evidence-incomplete;
- an observed stable citation join at target runtime is a bounded negative result;
- absence of a join can support privacy only when target-runtime execution exists
  and the required verifier/audit observer planes are represented.

The returned object conforms to dpip-privacy-observability-result/v1.
"""
from __future__ import annotations

from typing import Any


SCHEMA = "dpip-privacy-observability-result/v1"


def _target_runtime_vectors(package: dict[str, Any]) -> list[dict[str, Any]]:
    vectors = package.get("vectors")
    if not isinstance(vectors, list):
        raise ValueError("interop evidence package must contain a vectors list")
    return [
        item
        for item in vectors
        if isinstance(item, dict) and item.get("surface") == "target-runtime"
    ]


def _fixture_correlation_present(package: dict[str, Any]) -> bool:
    return any(
        isinstance(item, dict)
        and item.get("surface") == "fixture"
        and item.get("correlation") == "confirmed"
        for item in package.get("vectors") or []
    )


def _runtime_correlation_present(vectors: list[dict[str, Any]]) -> bool:
    return any(
        item.get("classification") == "supported"
        and item.get("correlation") == "confirmed"
        for item in vectors
    )


def _runtime_evidence_complete(vectors: list[dict[str, Any]]) -> bool:
    if not vectors:
        return False
    usable = [
        item
        for item in vectors
        if item.get("classification") in {"supported", "divergent"}
    ]
    if not usable:
        return False
    return all(item.get("correlation") in {"confirmed", "contradicted"} for item in usable)


def to_privacy_observability(package: dict[str, Any]) -> dict[str, Any]:
    """Convert a Lab convergence package into a DPIP bounded privacy result."""

    schema = str(package.get("schema") or "")
    if schema != "interop-task-citation-convergence-evidence/v1":
        raise ValueError(f"unsupported interop evidence schema: {schema!r}")

    runtime = _target_runtime_vectors(package)
    runtime_complete = _runtime_evidence_complete(runtime)
    runtime_correlation = _runtime_correlation_present(runtime)
    fixture_correlation = _fixture_correlation_present(package)

    if runtime_correlation:
        result = "not-supported"
        signal = "found"
        effective_join = True
        executed = True
        residual = [
            "The observed join is bounded to the source-pinned target runtime and observer scope.",
            "A future committed or proof-hidden citation construction requires a fresh examination.",
        ]
    elif runtime_complete:
        result = "supported"
        signal = "not-found"
        effective_join = False
        executed = True
        residual = [
            "No join was observed only within the executed source-pinned target-runtime vectors.",
            "Absence of a join does not establish deployment-wide unlinkability.",
        ]
    else:
        result = "evidence-incomplete"
        signal = "not-tested" if not runtime else "inconclusive"
        effective_join = False
        executed = False
        residual = [
            "Target-runtime evidence is absent, unavailable, or insufficient to determine effective correlation.",
            "Fixture-only correlation is pressure-test evidence and must not be promoted into target-runtime fact.",
        ]

    direct = [
        "taskContext",
        "taskDigestMultibase",
        "outcome-evidence identifiers",
        "presentation-visible citation or commitment",
    ]
    derived = [
        "cross-context equality of task citation material",
        "join between retained outcome evidence and credential presentations",
    ]
    if fixture_correlation:
        derived.append("fixture demonstrates that visible stable citation material is joinable in principle")

    return {
        "schema": SCHEMA,
        "experiment": {
            "id": "dpip-task-citation-correlation-271",
            "privacy_proposition": (
                "Credential-to-Trust-Task citation and completion evidence must not create "
                "a stable cross-context join that defeats the declared presentation privacy property."
            ),
            "comparison": {
                "kind": "multi-context",
                "scenarios": ["presentation-A", "presentation-B"],
            },
            "required_observer_planes": ["verifier", "audit"],
            "minimum_evidence_class": "target-runtime-observation",
            "reproducibility": "source-pinned",
            "source_issue": 271,
            "interop_issue": 233,
            "ra hp_coordination_issue".replace(" ", ""): 690,
        },
        "observer_planes": [
            {
                "id": "verifier",
                "direct_observables": direct,
                "derived_or_joinable": derived,
                "privilege": "ordinary",
                "threat_model": "in-scope",
                "composition_notes": [
                    "Credential validity, task completion, and unlinkability are evaluated separately.",
                    "Visible stable citation material is a correlation surface even when credential attributes are hidden.",
                ],
            },
            {
                "id": "audit",
                "direct_observables": [
                    "retained Trust Task evidence",
                    "retained outcome evidence",
                    "retained presentation transcript identifiers",
                ],
                "derived_or_joinable": [
                    "post-interaction joins across retained evidence",
                ],
                "privilege": "privileged",
                "threat_model": "conditional",
                "composition_notes": [
                    "Retention is included because outcome evidence can outlive the presentation."
                ],
            },
        ],
        "correlation": {
            "signal": signal,
            "effective_join": effective_join,
            "composition": [
                "credential citation",
                "Trust Task initiating-document binding",
                "outcome evidence",
                "retained verifier/audit evidence",
            ],
        },
        "result": result,
        "executed": executed,
        "unsupported_inference": [
            "deployment-wide unlinkability",
            "proof validity implies presentation unlinkability",
            "hidden credential attributes imply hidden task citation",
            "fixture-only behavior proves target implementation behavior",
        ],
        "residual_uncertainty": residual,
    }
