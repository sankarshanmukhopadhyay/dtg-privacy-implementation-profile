#!/usr/bin/env python3
"""Execute mechanically available DPIP evidence for examination-ready RAHP runs.

Known missing or wrong-class evidence is a deterministic assurance state:
INDETERMINATE / evidence-required. It is not a generic human-review condition and can
never be converted into PASS.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
from pathlib import Path
from typing import Any

import yaml

from rahp_intake import api, labels
from evaluate_interaction import evaluate, has_executable_evaluation

DEFAULT_REPO = "sankarshanmukhopadhyay/dtg-privacy-implementation-profile"
SOURCE_LABEL = "source:rahp"
IN_PROGRESS = "run:in-progress"
EXAMPLES = Path("examples")
OBSERVATIONS = Path("observations")
EVIDENCE_REQUIREMENTS = Path("portfolio/evidence-requirements.yaml")
SETUP_RE = re.compile(r"```ya?ml\s*\n(.*?)```", re.DOTALL | re.IGNORECASE)
SHA40 = re.compile(r"^[0-9a-f]{40}$", re.I)
DEFAULT_RUNTIME_REQUIREMENTS = {
    "C3": ["ER-REL-DID-AB", "ER-TASK-AB", "ER-VERIFIER-AB"],
    "C5": ["ER-STATUS-AB", "ER-TASK-AB", "ER-VERIFIER-AB"],
}
REQUIRED_RUNTIME_PROVENANCE = (
    "producer", "run_id", "observed_at", "implementation_repository",
    "implementation_revision", "context_a_run", "context_b_run",
)


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


def requirement_catalog() -> dict[str, dict[str, Any]]:
    if not EVIDENCE_REQUIREMENTS.exists():
        return {}
    doc = yaml.safe_load(EVIDENCE_REQUIREMENTS.read_text()) or {}
    return doc.get("requirements", {}) if isinstance(doc.get("requirements"), dict) else {}


def required_ids(setup: dict[str, Any]) -> list[str]:
    explicit = [str(x) for x in setup.get("evidence_requirement_ids", []) or []]
    if explicit:
        return list(dict.fromkeys(explicit))
    inferred: list[str] = []
    for iid in setup.get("candidate_interactions", []) or []:
        inferred.extend(DEFAULT_RUNTIME_REQUIREMENTS.get(str(iid), []))
    return list(dict.fromkeys(inferred))


def assess_supplied_evidence(setup: dict[str, Any], req_catalog: dict[str, dict[str, Any]]) -> tuple[list[str], list[dict[str, Any]]]:
    """Return accepted requirement IDs plus reviewer-readable sufficiency failures."""
    accepted: list[str] = []
    failures: list[dict[str, Any]] = []
    for index, binding in enumerate(setup.get("provided_evidence", []) or []):
        if not isinstance(binding, dict):
            failures.append({"binding_index": index, "reason_code": "malformed-evidence", "explanation": "Supplied evidence binding is not a mapping."})
            continue
        rid = str(binding.get("requirement_id") or "").strip()
        if not rid:
            failures.append({"binding_index": index, "reason_code": "malformed-evidence", "explanation": "Supplied evidence has no requirement_id."})
            continue
        meta = req_catalog.get(rid)
        if not isinstance(meta, dict):
            failures.append({"requirement_id": rid, "reason_code": "unknown-evidence-requirement", "explanation": f"No DPIP evidence requirement is registered for {rid}."})
            continue
        evidence_class = str(binding.get("evidence_class") or "").strip()
        accepted_classes = [str(x) for x in meta.get("accepted_evidence_classes", []) or []]
        if accepted_classes and evidence_class not in accepted_classes:
            failures.append({
                "requirement_id": rid,
                "evidence_class": evidence_class or None,
                "accepted_evidence_classes": accepted_classes,
                "reason_code": "wrong-evidence-class",
                "explanation": f"{rid} requires evidence class {', '.join(accepted_classes)}; supplied class is {evidence_class or '<missing>'}.",
            })
            continue
        provenance = binding.get("provenance")
        missing_provenance: list[str] = []
        if not isinstance(provenance, dict):
            missing_provenance = list(REQUIRED_RUNTIME_PROVENANCE)
        else:
            missing_provenance = [key for key in REQUIRED_RUNTIME_PROVENANCE if not str(provenance.get(key) or "").strip()]
            revision = str(provenance.get("implementation_revision") or "")
            if revision and not SHA40.fullmatch(revision):
                missing_provenance.append("implementation_revision(immutable-40-hex-required)")
        if missing_provenance:
            failures.append({
                "requirement_id": rid,
                "evidence_class": evidence_class or None,
                "reason_code": "malformed-evidence-provenance",
                "missing_or_invalid": missing_provenance,
                "explanation": f"{rid} has incomplete or mutable runtime provenance: {', '.join(missing_provenance)}.",
            })
            continue
        if not isinstance(binding.get("surfaces"), dict) or not str(binding.get("observation_summary") or "").strip():
            failures.append({
                "requirement_id": rid,
                "evidence_class": evidence_class or None,
                "reason_code": "malformed-evidence-observation",
                "explanation": f"{rid} must include an observation_summary and surfaces mapping.",
            })
            continue
        if rid not in accepted:
            accepted.append(rid)
    return accepted, failures


def build_execution(issue_number: int, setup: dict[str, Any]) -> dict[str, Any]:
    catalog = profile_catalog()
    req_catalog = requirement_catalog()
    checks: list[dict[str, Any]] = []
    missing: list[str] = []
    mechanical_results: list[dict[str, Any]] = []
    interactions = [str(i) for i in setup.get("candidate_interactions", []) or []]

    for iid in interactions:
        profile_path = catalog.get(iid)
        if not profile_path:
            missing.append(f"missing canonical interaction fixture: {iid}")
            continue
        evidence_path = observation_for(iid)
        if evidence_path is None:
            missing.append(f"no unique repository observation fixture for {iid}")
            checks.append({"interaction": iid, "profile": str(profile_path), "status": "NOT_RUN", "reason": "repository observation fixture unavailable"})
            continue
        profile = yaml.safe_load(profile_path.read_text()) or {}
        evidence = yaml.safe_load(evidence_path.read_text()) or {}
        if not has_executable_evaluation(profile):
            missing.append(f"no executable_evaluation rules for {iid}")
            checks.append({"interaction": iid, "profile": str(profile_path), "evidence": str(evidence_path), "status": "NOT_RUN", "reason": "executable rules unavailable"})
            continue
        try:
            outputs = evaluate(profile, evidence)
        except Exception as exc:
            missing.append(f"execution failed for {iid}: {exc}")
            checks.append({"interaction": iid, "profile": str(profile_path), "evidence": str(evidence_path), "status": "INDETERMINATE", "reason": str(exc)})
            continue
        checks.append({"interaction": iid, "profile": str(profile_path), "evidence": str(evidence_path), "status": "EXECUTED", "vectors": len(outputs), "boundary": "repository-native synthetic/canonical evidence; not upstream runtime telemetry"})
        for result in outputs:
            mechanical_results.append({"interaction": iid, "vector": result.get("_vector_id"), "test_results": result.get("test_results", []), "claim_results": result.get("claim_results", [])})

    required = required_ids(setup)
    accepted_ids, evidence_failures = assess_supplied_evidence(setup, req_catalog)
    supplied = set(accepted_ids)
    missing_requirements: list[dict[str, Any]] = []
    for rid in required:
        if rid in supplied:
            continue
        meta = req_catalog.get(rid)
        if not isinstance(meta, dict):
            missing.append(f"unknown evidence requirement: {rid}")
            continue
        related_failures = [failure for failure in evidence_failures if failure.get("requirement_id") == rid]
        missing_requirements.append({
            "id": rid,
            "title": meta.get("title"),
            "summary": meta.get("summary"),
            "evidence_kind": meta.get("evidence_kind"),
            "accepted_evidence_classes": meta.get("accepted_evidence_classes", []),
            "source_lineage": meta.get("source_lineage", []),
            **({"supplied_evidence_failures": related_failures} if related_failures else {}),
        })
    if missing_requirements:
        missing.append("required attributable runtime evidence not supplied or not provenance-sufficient: " + ", ".join(item["id"] for item in missing_requirements))

    state = "evidence-ready" if checks and not missing else "evidence-incomplete"
    record = {
        "status": state,
        "source_issue": issue_number,
        "setup_digest": setup.get("setup_digest"),
        "candidate_interactions": interactions,
        "candidate_profiles": setup.get("candidate_profiles", []),
        "human_scope": setup.get("human_scope", []),
        "checks": checks,
        "mechanical_results": mechanical_results,
        "required_evidence": missing_requirements,
        "satisfied_evidence_requirement_ids": sorted(supplied),
        "evidence_sufficiency_failures": evidence_failures,
        "missing_evidence": missing,
        "source_pins": setup.get("source_pins", []),
        "privacy_judgment": "not-made",
        "human_acceptance_required": False if missing_requirements and not any(item.startswith("unknown") for item in missing) else True,
    }
    execution = {"execution_evidence": record}
    digest = hashlib.sha256(json.dumps(execution, sort_keys=True, separators=(",", ":")).encode()).hexdigest()[:16]
    record["execution_digest"] = digest
    return execution


def remediation_plan(record: dict[str, Any]) -> dict[str, Any]:
    requirements = []
    for req in record.get("required_evidence", []) or []:
        requirements.append({
            "id": req.get("id"),
            "title": req.get("title"),
            "summary": req.get("summary"),
            "evidence_kind": req.get("evidence_kind"),
            "accepted_evidence_classes": req.get("accepted_evidence_classes", []),
            "supplied_evidence_failures": req.get("supplied_evidence_failures", []),
            "producer_lineage": req.get("source_lineage", []),
            "acceptance_criterion": "Supply attributable provenance-bound evidence in an accepted evidence class for this requirement in a comparable pinned rerun.",
        })
    plan = {
        "status": "required",
        "source_issue": record.get("source_issue"),
        "setup_digest": record.get("setup_digest"),
        "execution_digest": record.get("execution_digest"),
        "requirements": requirements,
        "rerun_policy": "Create a new comparable examination using supplied evidence and the original pinned scope; do not mutate the completed historical examination.",
    }
    plan["plan_digest"] = hashlib.sha256(json.dumps(plan, sort_keys=True, separators=(",", ":")).encode()).hexdigest()[:16]
    return plan


def conclusion_from_execution(execution: dict[str, Any]) -> dict[str, Any] | None:
    record = execution["execution_evidence"]
    if record.get("status") != "evidence-incomplete":
        return None
    named = [f"{r.get('id')} — {r.get('title')}" for r in record.get("required_evidence", []) or []]
    explanation = "The admitted privacy proposition is understood, but the evidence contract is not satisfied. "
    if named:
        explanation += "Missing or provenance-insufficient evidence: " + "; ".join(named) + ". "
    wrong_class = [f for f in record.get("evidence_sufficiency_failures", []) or [] if f.get("reason_code") == "wrong-evidence-class"]
    if wrong_class:
        explanation += "At least one supplied binding has the wrong evidence provenance class. "
    explanation += "Repository-native fixtures may exercise DPIP rules but do not prove upstream runtime behaviour."
    action = "Produce the named attributable runtime evidence in an accepted provenance class and create a pinned comparable DPIP rerun."
    return {"dpip_examination": {
        "applicability": "applicable",
        "conclusion": "INDETERMINATE",
        "reason_code": "evidence-required",
        "affected_interactions": record.get("candidate_interactions", []),
        "human_scope": record.get("human_scope", []),
        "evidence_summary": explanation,
        "residual_correlation": "Cross-context correlation cannot be ruled in or out until the evidence contract is satisfied.",
        "action": action,
        "evidence_remediation_plan": remediation_plan(record),
        "human_summary": {"outcome": "INDETERMINATE — more evidence is required", "explanation": explanation, "action": action},
        "source_pins": record.get("source_pins", []),
        "execution_digest": record.get("execution_digest"),
        "human_acceptance_required": record.get("human_acceptance_required", True),
    }}


def comments(repo: str, number: int, token: str) -> list[dict[str, Any]]:
    return api("GET", repo, f"issues/{number}/comments?per_page=100", token) or []


def _human_scope_md(scope: list[dict[str, Any]]) -> str:
    rows = []
    for item in scope or []:
        if item.get("title"):
            rows.append(f"- **{item.get('id')} — {item.get('title')}**: {item.get('summary')}")
    return "\n".join(rows)


def publish(repo: str, issue: dict[str, Any], token: str) -> None:
    number = int(issue["number"])
    existing = comments(repo, number, token)
    setup = setup_from_comments(existing)
    if not setup:
        print(f"SKIP #{number}: no examination_setup comment"); return
    evidence = build_execution(number, setup)
    record = evidence["execution_evidence"]
    digest = record["execution_digest"]
    marker = f"<!-- dpip-execution-evidence:{number}:{digest} -->"
    if not any(marker in (comment.get("body") or "") for comment in existing):
        body = f"{marker}\n## DPIP repository-native execution — {record['status']}\n\n{_human_scope_md(record.get('human_scope', []))}\n\nMissing or wrong-class evidence remains explicit; repository fixtures are not promoted into runtime proof.\n\n```yaml\n{yaml.safe_dump(evidence, sort_keys=False).rstrip()}\n```"
        api("POST", repo, f"issues/{number}/comments", token, {"body": body})
    conclusion = conclusion_from_execution(evidence)
    if conclusion is not None:
        exam = conclusion["dpip_examination"]
        conclusion_digest = hashlib.sha256(json.dumps(conclusion, sort_keys=True, separators=(",", ":")).encode()).hexdigest()[:16]
        conclusion_marker = f"<!-- dpip-examination:{number}:{conclusion_digest} -->"
        if not any(conclusion_marker in (comment.get("body") or "") for comment in existing):
            body = f"{conclusion_marker}\n## DPIP scoped conclusion — {exam['conclusion']} / {exam['reason_code']}\n\n**Human reading:** {exam['human_summary']['explanation']}\n\n{_human_scope_md(exam.get('human_scope', []))}\n\n```yaml\n{yaml.safe_dump(conclusion, sort_keys=False).rstrip()}\n```"
            api("POST", repo, f"issues/{number}/comments", token, {"body": body})
        api("POST", repo, f"issues/{number}/labels", token, {"labels": ["run:complete"]})
        try:
            api("DELETE", repo, f"issues/{number}/labels/run%3Ain-progress", token)
        except Exception:
            pass
    print(f"EXECUTION #{number}: {record['status']}")


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


def _binding(rid: str, evidence_class: str = "runtime-upstream-observation", revision: str = "cb01d0a758863fb3a02f9f4eef2c4f15f56c4c3b") -> dict[str, Any]:
    return {
        "requirement_id": rid,
        "evidence_class": evidence_class,
        "provenance": {
            "producer": "trust-protocol-interop-lab",
            "run_id": "runtime-ab-001",
            "observed_at": "2026-08-30T00:00:00Z",
            "implementation_repository": "OpenVTC/verifiable-trust-infrastructure",
            "implementation_revision": revision,
            "context_a_run": "A-001",
            "context_b_run": "B-001",
        },
        "observation_summary": f"A/B runtime observation for {rid}",
        "surfaces": {"example": {"classification": "fresh", "context_a": "a", "context_b": "b"}},
    }


def self_test() -> int:
    setup = {
        "setup_digest": "dogwood",
        "candidate_interactions": ["C3", "C5"],
        "candidate_profiles": ["PP-4", "PP-2"],
        "evidence_requirement_ids": ["ER-REL-DID-AB", "ER-STATUS-AB", "ER-TASK-AB", "ER-VERIFIER-AB"],
        "human_scope": [
            {"id": "C3", "kind": "interaction", "title": "Asymmetric cross-community relationship privacy", "summary": "Human-readable C3 meaning."},
            {"id": "C5", "kind": "interaction", "title": "Privacy-preserving lifecycle evaluation and precedence", "summary": "Human-readable C5 meaning."},
        ],
        "source_pins": [{"label": "Dogwood RC-1", "repository": "OpenVTC/verifiable-trust-infrastructure", "revision": "cb01d0a758863fb3a02f9f4eef2c4f15f56c4c3b"}],
    }
    execution = build_execution(120, setup)
    record = execution["execution_evidence"]
    assert record["status"] == "evidence-incomplete", record
    assert {r["id"] for r in record["required_evidence"]} == {"ER-REL-DID-AB", "ER-STATUS-AB", "ER-TASK-AB", "ER-VERIFIER-AB"}
    conclusion = conclusion_from_execution(execution)["dpip_examination"]
    assert conclusion["conclusion"] == "INDETERMINATE"
    assert conclusion["reason_code"] == "evidence-required"
    assert conclusion["human_acceptance_required"] is False
    assert "C3" in _human_scope_md(conclusion["human_scope"])
    assert "Asymmetric cross-community relationship privacy" in _human_scope_md(conclusion["human_scope"])
    assert conclusion["source_pins"][0]["revision"].startswith("cb01d0")

    synthetic = json.loads(json.dumps(setup))
    synthetic["provided_evidence"] = [_binding(rid, "synthetic-fixture-self-test") for rid in setup["evidence_requirement_ids"]]
    synthetic_record = build_execution(124, synthetic)["execution_evidence"]
    assert not synthetic_record["satisfied_evidence_requirement_ids"]
    assert {f["reason_code"] for f in synthetic_record["evidence_sufficiency_failures"]} == {"wrong-evidence-class"}
    assert {r["id"] for r in synthetic_record["required_evidence"]} == set(setup["evidence_requirement_ids"])

    runtime = json.loads(json.dumps(setup))
    runtime["provided_evidence"] = [_binding(rid) for rid in setup["evidence_requirement_ids"]]
    runtime_record = build_execution(124, runtime)["execution_evidence"]
    assert set(runtime_record["satisfied_evidence_requirement_ids"]) == set(setup["evidence_requirement_ids"])
    assert runtime_record["required_evidence"] == []

    malformed = json.loads(json.dumps(setup))
    malformed["provided_evidence"] = [_binding("ER-REL-DID-AB", revision="main")]
    malformed_record = build_execution(124, malformed)["execution_evidence"]
    assert any(f["reason_code"] == "malformed-evidence-provenance" for f in malformed_record["evidence_sufficiency_failures"])
    print("PASS examination_execute self-test")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--issue-number", type=int)
    args = parser.parse_args()
    if args.self_test: return self_test()
    token = os.getenv("GITHUB_TOKEN", "")
    if not token:
        raise SystemExit("GITHUB_TOKEN is required")
    return run(os.getenv("DPIP_REPOSITORY", DEFAULT_REPO), token, args.issue_number)


if __name__ == "__main__":
    raise SystemExit(main())
