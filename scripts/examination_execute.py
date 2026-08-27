#!/usr/bin/env python3
"""Execute mechanically available DPIP evidence for examination-ready RAHP runs."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
from pathlib import Path
from typing import Any

import yaml

from rahp_intake import api, labels
from evaluate_interaction import evaluate

DEFAULT_REPO = "sankarshanmukhopadhyay/dtg-privacy-implementation-profile"
SOURCE_LABEL = "source:rahp"
IN_PROGRESS = "run:in-progress"
EXAMPLES = Path("examples")
OBSERVATIONS = Path("observations")
SETUP_RE = re.compile(r"```ya?ml\s*\n(.*?)```", re.DOTALL | re.IGNORECASE)


def yaml_docs(text: str) -> list[dict[str, Any]]:
    out = []
    for match in SETUP_RE.finditer(text or ""):
        try:
            value = yaml.safe_load(match.group(1))
        except yaml.YAMLError:
            continue
        if isinstance(value, dict):
            out.append(value)
    return out


def setup_from_comments(comments: list[dict[str, Any]]) -> dict[str, Any] | None:
    for comment in reversed(comments):
        for doc in yaml_docs(comment.get("body") or ""):
            if isinstance(doc.get("examination_setup"), dict):
                return doc["examination_setup"]
    return None


def profile_catalog() -> dict[str, Path]:
    out: dict[str, Path] = {}
    for path in sorted(EXAMPLES.glob("*.yaml")):
        doc = yaml.safe_load(path.read_text()) or {}
        iid = (doc.get("interaction") or {}).get("id")
        if iid:
            out[str(iid)] = path
    return out


def observation_for(interaction_id: str) -> Path | None:
    prefix = interaction_id.lower() + "-"
    matches = sorted(p for p in OBSERVATIONS.glob("*.yaml") if p.name.lower().startswith(prefix))
    return matches[0] if len(matches) == 1 else None


def evidence_requirement(requirement_id: str, proposition: str, evidence_class: str, producer: str,
                         context_boundary: str, required_fields: list[str], privacy_safe_capture_rule: str,
                         acceptance_criterion: str, rerun_target: str, priority: str,
                         routing_target: str) -> dict[str, Any]:
    return {
        "id": requirement_id,
        "proposition": proposition,
        "evidence_class": evidence_class,
        "producer": producer,
        "context_boundary": context_boundary,
        "required_fields": required_fields,
        "privacy_safe_capture_rule": privacy_safe_capture_rule,
        "acceptance_criterion": acceptance_criterion,
        "rerun_target": rerun_target,
        "priority": priority,
        "routing_target": routing_target,
    }


def remediation_plan(issue_number: int, record: dict[str, Any]) -> dict[str, Any]:
    requirements: list[dict[str, Any]] = []
    missing = [str(item) for item in record.get("missing_evidence", [])]
    interactions = [str(item) for item in record.get("candidate_interactions", [])]

    for iid in interactions:
        if any(f"no executable_evaluation rules for {iid}" in item for item in missing):
            requirements.append(evidence_requirement(
                f"DPIP-{iid}-EXECUTABLE-RULES",
                f"DPIP can mechanically evaluate the scoped {iid} privacy proposition against repository observation evidence.",
                "executable-fixture-rule",
                "DPIP",
                "repository-local fixture; does not assert upstream runtime behaviour",
                ["interaction id", "test vector id", "observable fields", "expected falsification/sufficiency condition"],
                "Use synthetic/non-identifying fixture values; fixture data must not be represented as implementation telemetry.",
                f"{iid} has executable_evaluation rules and the repository-native evaluator can execute its canonical observation fixture deterministically.",
                f"DPIP examination #{issue_number} / interaction {iid}",
                "blocks one scoped interaction conclusion",
                "dpip-local",
            ))
        if any(f"no unique repository observation fixture for {iid}" in item for item in missing):
            requirements.append(evidence_requirement(
                f"DPIP-{iid}-OBSERVATION-FIXTURE",
                f"DPIP has one unambiguous repository observation fixture capable of exercising the scoped {iid} failure mode.",
                "executable-observation-fixture",
                "DPIP",
                "repository-local fixture; A/B contexts where the interaction tests cross-context correlation",
                ["interaction id", "context labels", "observable join fields", "expected attack/falsification outcome"],
                "Use normalized or synthetic values sufficient to test joinability; do not introduce real identifiers.",
                f"Exactly one canonical {iid} observation fixture is selected and passes observation validation.",
                f"DPIP examination #{issue_number} / interaction {iid}",
                "blocks one scoped interaction conclusion",
                "dpip-local",
            ))

    # Runtime requirements remain authoritative even after DPIP-local fixtures become executable.
    runtime_specs = [
        ("RELATIONSHIP-BINDER", "Relationship DID / edge identifiers are not stably reused or derivable across unrelated contexts.",
         "implementation-trace", "DTG relationship/credential implementation", ["normalized relationship/edge handle", "context label", "derivation/reuse indicator", "observer vantage"]),
        ("STATUS-DISCOVERY", "Status and policy-discovery activity does not expose a stable cross-context join handle.",
         "status-request-response-trace", "status/policy discovery implementation or operator", ["normalized request handle", "normalized response handle", "cache/log key", "currentness decision", "observer vantage"]),
        ("TRUST-TASK-RETENTION", "Retained Trust Task / relationship evidence does not create an unintended durable cross-context correlator.",
         "operator-retention-trace", "Trust Tasks implementation/operator", ["retained field names", "normalized retained handles", "retention horizon", "observer/access class", "context label"]),
        ("VERIFIER-CONTEXT", "The deliberate-correlation mechanism is bounded to the intended verifier/context and does not become a wider correlator.",
         "protocol-transcript", "verifier / ZKP presentation implementation", ["normalized context commitment", "verifier context", "transcript binding fields", "reuse/derivation indicator"]),
    ]
    for suffix, proposition, evidence_class, producer, fields in runtime_specs:
        requirements.append(evidence_requirement(
            f"RUNTIME-{suffix}", proposition, evidence_class, producer,
            "two unrelated execution contexts A and B",
            fields,
            "Prefer normalized, salted-hash, or otherwise minimized values when equality/joinability is the proposition; do not collect identifying telemetry unless strictly necessary.",
            "Attributable A/B observations contain the minimum listed fields and are sufficient to attempt the scoped cross-context join/falsification without relying on specification intent.",
            f"DPIP examination #{issue_number} pinned to the original scope/source revisions",
            "blocks runtime privacy conclusion",
            "upstream-runtime",
        ))

    plan = {
        "status": "required",
        "source_issue": issue_number,
        "setup_digest": record.get("setup_digest"),
        "execution_digest": record.get("execution_digest"),
        "requirements": requirements,
        "rerun_policy": "Create a new comparable examination using the supplied evidence and the original pinned scope; do not mutate the completed historical examination.",
    }
    plan["plan_digest"] = hashlib.sha256(json.dumps(plan, sort_keys=True, separators=(",", ":")).encode()).hexdigest()[:16]
    return plan


def build_execution(issue_number: int, setup: dict[str, Any]) -> dict[str, Any]:
    catalog = profile_catalog()
    checks = []
    missing = []
    mechanical_results = []

    for iid in setup.get("candidate_interactions", []) or []:
        iid = str(iid)
        profile_path = catalog.get(iid)
        if not profile_path:
            missing.append(f"missing canonical interaction fixture: {iid}")
            continue
        evidence_path = observation_for(iid)
        if evidence_path is None:
            missing.append(f"no unique repository observation fixture for {iid}")
            checks.append({"interaction": iid, "profile": str(profile_path), "status": "NOT_RUN", "reason": "observation fixture unavailable"})
            continue
        profile = yaml.safe_load(profile_path.read_text()) or {}
        evidence = yaml.safe_load(evidence_path.read_text()) or {}
        if not profile.get("executable_evaluation"):
            missing.append(f"no executable_evaluation rules for {iid}")
            checks.append({"interaction": iid, "profile": str(profile_path), "evidence": str(evidence_path), "status": "NOT_RUN", "reason": "executable rules unavailable"})
            continue
        try:
            outputs = evaluate(profile, evidence)
        except Exception as exc:
            missing.append(f"execution failed for {iid}: {exc}")
            checks.append({"interaction": iid, "profile": str(profile_path), "evidence": str(evidence_path), "status": "INDETERMINATE", "reason": str(exc)})
            continue
        checks.append({"interaction": iid, "profile": str(profile_path), "evidence": str(evidence_path), "status": "EXECUTED", "vectors": len(outputs)})
        for result in outputs:
            mechanical_results.append({"interaction": iid, "vector": result.get("_vector_id"), "test_results": result.get("test_results", []), "claim_results": result.get("claim_results", [])})

    state = "evidence-ready" if checks and not missing else "evidence-incomplete"
    execution = {"execution_evidence": {"status": state, "source_issue": issue_number, "setup_digest": setup.get("setup_digest"), "candidate_interactions": setup.get("candidate_interactions", []), "candidate_profiles": setup.get("candidate_profiles", []), "checks": checks, "mechanical_results": mechanical_results, "missing_evidence": missing, "source_pins": setup.get("source_pins", []), "privacy_judgment": "not-made", "human_acceptance_required": True}}
    digest = hashlib.sha256(json.dumps(execution, sort_keys=True, separators=(",", ":")).encode()).hexdigest()[:16]
    execution["execution_evidence"]["execution_digest"] = digest
    return execution


def conclusion_from_execution(execution: dict[str, Any]) -> dict[str, Any] | None:
    record = execution["execution_evidence"]
    if record.get("status") == "evidence-incomplete":
        missing = [str(item) for item in record.get("missing_evidence", []) if str(item).strip()]
        summary = "DPIP confirmed the requested privacy scope is applicable and resolved, but the available repository/source evidence is insufficient to make the requested privacy claim. " + ("Missing executable/runtime evidence: " + "; ".join(missing) if missing else "Required executable/runtime evidence is unavailable.")
        plan = remediation_plan(int(record["source_issue"]), record)
        action = "Produce the bounded evidence requirements in evidence_remediation_plan, then create a pinned comparable DPIP rerun before asserting the composed privacy claim."
        return {"dpip_examination": {"applicability": "applicable", "conclusion": "INDETERMINATE", "affected_interactions": record.get("candidate_interactions", []), "affected_claims": [], "affected_invariants": [], "evidence_summary": summary, "residual_correlation": "Cross-context correlation cannot be ruled in or out from source-backed evidence alone.", "action": action, "evidence_remediation_plan": plan, "human_summary": {"outcome": "We do not have enough evidence to decide yet", "explanation": summary, "action": action}, "source_pins": record.get("source_pins", []), "execution_digest": record.get("execution_digest"), "human_acceptance_required": True}}
    return None


def comments(repo: str, number: int, token: str) -> list[dict[str, Any]]:
    return api("GET", repo, f"issues/{number}/comments?per_page=100", token) or []


def publish(repo: str, issue: dict[str, Any], token: str) -> None:
    number = int(issue["number"])
    existing = comments(repo, number, token)
    setup = setup_from_comments(existing)
    if not setup:
        print(f"SKIP #{number}: no examination_setup comment")
        return
    evidence = build_execution(number, setup)
    digest = evidence["execution_evidence"]["execution_digest"]
    marker = f"<!-- dpip-execution-evidence:{number}:{digest} -->"
    if not any(marker in (comment.get("body") or "") for comment in existing):
        body = f"{marker}\n## DPIP repository-native execution — {evidence['execution_evidence']['status']}\n\nThis stage executes only mechanically available repository evidence. Missing evidence remains explicit; this comment is **not** the DPIP privacy disposition.\n\n```yaml\n{yaml.safe_dump(evidence, sort_keys=False).rstrip()}\n```"
        api("POST", repo, f"issues/{number}/comments", token, {"body": body})
    conclusion = conclusion_from_execution(evidence)
    if conclusion is not None:
        conclusion_digest = hashlib.sha256(json.dumps(conclusion, sort_keys=True, separators=(",", ":")).encode()).hexdigest()[:16]
        conclusion_marker = f"<!-- dpip-examination:{number}:{conclusion_digest} -->"
        if not any(conclusion_marker in (comment.get("body") or "") for comment in existing):
            conclusion_body = f"{conclusion_marker}\n## DPIP scoped conclusion — {conclusion['dpip_examination']['conclusion']}\n\nThis is the DPIP disposition for the evidence currently available. It preserves missing-evidence boundaries rather than converting them into a privacy pass.\n\n```yaml\n{yaml.safe_dump(conclusion, sort_keys=False).rstrip()}\n```"
            api("POST", repo, f"issues/{number}/comments", token, {"body": conclusion_body})
        api("POST", repo, f"issues/{number}/labels", token, {"labels": ["run:complete"]})
        try:
            api("DELETE", repo, f"issues/{number}/labels/run%3Ain-progress", token)
        except Exception:
            pass
    print(f"EXECUTION #{number}: {evidence['execution_evidence']['status']}")


def eligible(issue: dict[str, Any]) -> bool:
    return not issue.get("pull_request") and {SOURCE_LABEL, IN_PROGRESS}.issubset(labels(issue))


def run(repo: str, token: str, issue_number: int | None = None) -> int:
    if issue_number is not None:
        issue = api("GET", repo, f"issues/{issue_number}", token)
        if eligible(issue): publish(repo, issue, token)
        else: print(f"SKIP #{issue_number}: not an admitted RAHP run")
        return 0
    issues = api("GET", repo, "issues?state=open&labels=source%3Arahp%2Crun%3Ain-progress&per_page=100", token) or []
    for issue in issues:
        if eligible(issue): publish(repo, issue, token)
    return 0


def self_test() -> int:
    incomplete = build_execution(111, {"setup_digest": "example", "candidate_interactions": ["C3", "C5"], "candidate_profiles": ["PP-4", "PP-2"], "source_pins": [{"label": "example", "revision": "a" * 40}]})["execution_evidence"]
    assert incomplete["status"] == "evidence-incomplete"
    conclusion = conclusion_from_execution({"execution_evidence": incomplete})["dpip_examination"]
    assert conclusion["conclusion"] == "INDETERMINATE"
    plan = conclusion["evidence_remediation_plan"]
    assert plan["requirements"] and plan["plan_digest"]
    assert any(r["routing_target"] == "dpip-local" for r in plan["requirements"])
    assert any(r["routing_target"] == "upstream-runtime" for r in plan["requirements"])
    assert all(r["privacy_safe_capture_rule"] for r in plan["requirements"])
    assert remediation_plan(111, incomplete)["plan_digest"] == plan["plan_digest"]
    ready = build_execution(63, {"setup_digest": "protected-access", "candidate_interactions": ["C8"], "candidate_profiles": ["PP-5"], "source_pins": [{"label": "example", "revision": "b" * 40}]})["execution_evidence"]
    assert ready["status"] == "evidence-ready" and ready["mechanical_results"]
    print("PASS examination_execute self-test")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--issue-number", type=int)
    args = parser.parse_args()
    if args.self_test: return self_test()
    token = os.environ.get("GITHUB_TOKEN", "")
    if not token: sys.exit("GITHUB_TOKEN is required")
    return run(os.environ.get("DPIP_REPOSITORY", DEFAULT_REPO), token, args.issue_number)


if __name__ == "__main__":
    raise SystemExit(main())
