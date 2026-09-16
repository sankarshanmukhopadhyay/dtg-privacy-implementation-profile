#!/usr/bin/env python3
"""Consume Interop Lab human-power observations under DPIP privacy authority.

This module evaluates privacy-depth propositions only. It does not decide coercion,
discrimination, legitimacy, substantive decision fairness, or portfolio assurance.
Synthetic pressure-test evidence may qualify evaluator behavior but cannot establish
production/deployment behavior.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

PACKAGE_SCHEMA = "interop-human-power-evidence-package/v1"
RESULT_SCHEMA = "interop-human-power-observation-evidence/v1"
RETURN_SCHEMA = "dpip-human-power-privacy-result/v1"
OUTCOMES = {"PASS", "FAIL", "INDETERMINATE", "NOT_APPLICABLE"}


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def _result_by_id(package: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {item["case"]["id"]: item for item in package["results"]}


def validate_package(package: dict[str, Any]) -> None:
    _require(isinstance(package, dict), "package must be an object")
    _require(package.get("schema") == PACKAGE_SCHEMA, f"schema must be {PACKAGE_SCHEMA}")
    _require(isinstance(package.get("producer_revision"), str) and package["producer_revision"], "producer_revision is required")
    results = package.get("results")
    _require(isinstance(results, list) and results, "results must be a non-empty array")
    _require(package.get("case_count") == len(results), "case_count must match results length")
    for item in results:
        _require(isinstance(item, dict), "result must be an object")
        _require(item.get("schema") == RESULT_SCHEMA, f"result schema must be {RESULT_SCHEMA}")
        case = item.get("case")
        _require(isinstance(case, dict) and isinstance(case.get("id"), str) and case["id"], "result case.id is required")
        _require(item.get("evidence_state") in {"COMPLETE", "EVIDENCE_REQUIRED"}, "invalid evidence_state")
        _require(isinstance(item.get("source"), dict), "result source is required")
        provenance = item.get("provenance")
        _require(isinstance(provenance, dict) and isinstance(provenance.get("fixture_sha256"), str), "fixture provenance is required")


def evidence_maturity(package: dict[str, Any]) -> str:
    kinds = {item.get("source", {}).get("kind") for item in package["results"]}
    if kinds == {"synthetic-pressure-test"}:
        return "synthetic-pressure-test"
    if "synthetic-pressure-test" in kinds:
        return "mixed"
    return "runtime-or-external"


def _base_return(package: dict[str, Any], issue: int, outcome: str, reasons: list[str]) -> dict[str, Any]:
    _require(outcome in OUTCOMES, f"invalid outcome: {outcome}")
    maturity = evidence_maturity(package)
    return {
        "schema": RETURN_SCHEMA,
        "dpip_issue": issue,
        "outcome": outcome,
        "reasons": reasons,
        "evidence": {
            "source_repository": "sankarshanmukhopadhyay/trust-protocol-interop-lab",
            "source_revision": package["producer_revision"],
            "source_schema": package["schema"],
            "maturity": maturity,
            "case_count": package["case_count"],
        },
        "deployment_claim_supported": maturity == "runtime-or-external",
        "authority_boundary": {
            "dpip_owns": ["privacy minimisation", "observability", "linkability/correlation", "privacy evidence sufficiency"],
            "dpip_does_not_own": ["coercion", "power-asymmetry harm", "discrimination", "substantive decision legitimacy", "portfolio assurance"],
            "terminal_owner": "RAHP",
        },
    }


def evaluate_compelled_disclosure(package: dict[str, Any]) -> dict[str, Any]:
    """Evaluate DPIP #190 from bounded disclosure/correlation/refusal observations."""
    validate_package(package)
    items = _result_by_id(package)
    required = {
        "DISCLOSURE_MINIMAL",
        "DISCLOSURE_EXPANDED",
        "DISCLOSURE_ENHANCED_ASSURANCE",
        "CORRELATION_SCOPED",
        "CORRELATION_STABLE_DEMAND",
        "CORRELATION_CROSS_SESSION",
        "CORRELATION_GOVERNED_STABLE",
        "REFUSAL_HIGH_DEPENDENCY_DENIAL",
    }
    missing_cases = sorted(required - set(items))
    evidence_required = sorted(
        case_id for case_id in required & set(items)
        if items[case_id]["evidence_state"] != "COMPLETE"
    )
    if missing_cases or evidence_required:
        result = _base_return(package, 190, "INDETERMINATE", ["required-pressure-evidence-incomplete"])
        result["residual"] = {"missing_cases": missing_cases, "evidence_required_cases": evidence_required}
        return result

    expanded = items["DISCLOSURE_EXPANDED"]
    enhanced = items["DISCLOSURE_ENHANCED_ASSURANCE"]
    stable = items["CORRELATION_STABLE_DEMAND"]
    cross_session = items["CORRELATION_CROSS_SESSION"]
    governed_stable = items["CORRELATION_GOVERNED_STABLE"]
    denial = items["REFUSAL_HIGH_DEPENDENCY_DENIAL"]

    expanded_beyond = expanded.get("derived_signals", {}).get("disclosed_beyond_available_minimal", [])
    expanded_purpose_bound = expanded.get("observations", {}).get("disclosure", {}).get("purpose_bound")
    enhanced_purpose_bound = enhanced.get("observations", {}).get("disclosure", {}).get("purpose_bound")
    stable_scope_changed = stable.get("derived_signals", {}).get("scope_changed_from_declared")
    cross_scope_changed = cross_session.get("derived_signals", {}).get("scope_changed_from_declared")
    governed_declared = governed_stable.get("derived_signals", {}).get("declared_scope")
    governed_effective = governed_stable.get("derived_signals", {}).get("effective_scope")

    negative_findings: list[str] = []
    if expanded_beyond and expanded_purpose_bound is False:
        negative_findings.append("expanded-disclosure-exceeds-minimal-and-is-not-purpose-bound")
    if stable_scope_changed is True:
        negative_findings.append("stable-identifier-demand-expands-declared-correlation-scope")
    if cross_scope_changed is True:
        negative_findings.append("retention-expands-effective-scope-across-sessions")

    counter_cases: list[str] = []
    if enhanced_purpose_bound is True:
        counter_cases.append("purpose-bound-enhanced-assurance-preserved")
    if governed_declared == governed_effective:
        counter_cases.append("governed-stable-account-scope-remains-aligned")

    reasons = negative_findings or ["no-bounded-privacy-failure-observed"]
    outcome = "FAIL" if negative_findings else "PASS"
    result = _base_return(package, 190, outcome, reasons)
    result["bounded_findings"] = {
        "negative": negative_findings,
        "counter_cases": counter_cases,
        "refusal_context": {
            "consequence": denial.get("observations", {}).get("refusal", {}).get("consequence"),
            "continuation_path": denial.get("observations", {}).get("refusal", {}).get("continuation_path"),
            "privacy_interpretation": "context-for-minimisation-assessment-only",
            "coercion_judgment": "not-made-by-dpip",
        },
    }
    result["residual"] = {
        "deployment_runtime_required": not result["deployment_claim_supported"],
        "reason": "synthetic pressure evidence validates the bounded privacy proposition and evaluator behavior but does not establish any target deployment behavior",
    }
    return result


def evaluate_proxy_inference(package: dict[str, Any]) -> dict[str, Any]:
    """Evaluate DPIP #191 without inventing a sensitive-characteristic inference."""
    validate_package(package)
    items = _result_by_id(package)
    required = {
        "DECISION_FEATURE_PRIMARY_ONLY",
        "DECISION_FEATURE_HIDDEN_COMMUNITY",
        "DECISION_FEATURE_GOVERNED_RISK",
        "CORRELATION_SCOPED",
        "CORRELATION_CROSS_SESSION",
    }
    missing_cases = sorted(required - set(items))
    evidence_required = sorted(
        case_id for case_id in required & set(items)
        if items[case_id]["evidence_state"] != "COMPLETE"
    )
    if missing_cases or evidence_required:
        result = _base_return(package, 191, "INDETERMINATE", ["required-proxy-privacy-evidence-incomplete"])
        result["residual"] = {"missing_cases": missing_cases, "evidence_required_cases": evidence_required}
        return result

    hidden = items["DECISION_FEATURE_HIDDEN_COMMUNITY"]
    primary = items["DECISION_FEATURE_PRIMARY_ONLY"]
    governed = items["DECISION_FEATURE_GOVERNED_RISK"]
    hidden_features = hidden.get("derived_signals", {}).get("undeclared_evaluated_features", [])
    hidden_outcome = hidden.get("derived_signals", {}).get("outcome")
    primary_outcome = primary.get("derived_signals", {}).get("outcome")
    governed_undeclared = governed.get("derived_signals", {}).get("undeclared_evaluated_features", [])

    observable_surface = "community_membership" in hidden_features
    controlled_outcome_difference = observable_surface and hidden_outcome != primary_outcome
    less_revealing_alternative = primary_outcome == "permit"

    # The Interop fixture shows consequential use of an extra metadata feature, but it
    # does not observe a mapping from that feature to a sensitive/social characteristic,
    # nor an actual cross-context inference. DPIP therefore must not promote it to a
    # proxy-inference conclusion.
    reasons = ["sensitive-or-social-inference-not-observed", "cross-context-proxy-effect-not-observed"]
    result = _base_return(package, 191, "INDETERMINATE", reasons)
    result["bounded_findings"] = {
        "observable_extra_feature": observable_surface,
        "feature": "community_membership" if observable_surface else None,
        "controlled_outcome_difference": controlled_outcome_difference,
        "less_revealing_alternative_observed": less_revealing_alternative,
        "governed_counter_case_has_undeclared_features": bool(governed_undeclared),
        "discrimination_or_legitimacy_judgment": "not-made-by-dpip",
    }
    result["residual"] = {
        "evidence_required": [
            "observer-bound mapping, if any, from trust metadata to the claimed sensitive/social characteristic",
            "cross-context observation showing whether the metadata/inference is reusable or linkable beyond the bounded decision",
            "target-specific provenance if a deployment claim is sought",
        ],
        "next_action": "request a target-specific Interop Lab runtime observation only when a concrete implementation surface is nominated",
    }
    return result


def evaluate(package: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema": "dpip-human-power-privacy-bundle/v1",
        "source_revision": package.get("producer_revision"),
        "results": [evaluate_compelled_disclosure(package), evaluate_proxy_inference(package)],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, type=Path, help="Interop Lab human-power evidence package")
    parser.add_argument("--output", type=Path, help="write DPIP specialist bundle")
    parser.add_argument("--check", action="store_true", help="validate and require terminal DPIP results")
    args = parser.parse_args()
    package = json.loads(args.input.read_text(encoding="utf-8"))
    bundle = evaluate(package)
    text = json.dumps(bundle, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text, encoding="utf-8")
    else:
        print(text, end="")
    if args.check:
        for result in bundle["results"]:
            _require(result["outcome"] in OUTCOMES, "non-terminal outcome")
        print("PASS: DPIP human-power privacy bundle is terminal and bounded")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
