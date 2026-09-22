#!/usr/bin/env python3
"""Bounded DPIP evaluator for predicate-defined audience privacy pressure cases.

This evaluator owns disclosure, observability and correlation propositions only.
It does not determine whether collective authority or audience membership grants
authorization; that remains with the owning authority/policy layer.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

OUTCOMES = {"PASS", "FAIL", "INDETERMINATE", "NOT_APPLICABLE"}


def evaluate(case: dict) -> dict:
    audience_kind = case.get("audience_kind")
    evidence_state = case.get("evidence_state")

    if audience_kind == "none":
        return {
            "outcome": "NOT_APPLICABLE",
            "materiality": "not-automatic",
            "reasons": ["collective-authority-alone-does-not-create-a-predicate-audience-privacy-finding"],
        }

    if audience_kind != "predicate-bounded":
        return {
            "outcome": "INDETERMINATE",
            "materiality": "unknown",
            "reasons": ["unsupported-audience-kind"],
        }

    if evidence_state != "COMPLETE":
        return {
            "outcome": "INDETERMINATE",
            "materiality": "warranted",
            "reasons": ["observable-membership-proof-surface-not-established"],
        }

    obs = case.get("observations") or {}
    failures: list[str] = []
    if obs.get("raw_membership_disclosed") is True:
        failures.append("raw-membership-disclosed")
    if obs.get("predicate_details_disclosed") is True:
        failures.append("predicate-details-disclosed")
    if obs.get("stable_identifier_scope") not in {None, "none", obs.get("required_scope")}:
        failures.append("identifier-correlation-scope-exceeds-required-audience")

    return {
        "outcome": "FAIL" if failures else "PASS",
        "materiality": "warranted",
        "reasons": failures or ["membership-proof-is-bounded-to-required-audience-scope"],
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", required=True, type=Path)
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args()
    payload = json.loads(args.input.read_text(encoding="utf-8"))
    failures = []
    results = []
    for case in payload.get("cases", []):
        result = evaluate(case)
        results.append({"id": case.get("id"), **result})
        if result["outcome"] != case.get("expected_outcome") or result["materiality"] != case.get("expected_materiality"):
            failures.append(case.get("id"))
    print(json.dumps({"schema": "dpip-predicate-audience-result/v1", "results": results}, indent=2))
    return 1 if args.check and failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
