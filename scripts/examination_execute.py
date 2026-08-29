#!/usr/bin/env python3
"""Execute mechanically available DPIP evidence for examination-ready RAHP runs.

Known missing evidence is a deterministic assurance state: INDETERMINATE / evidence-required.
It is not a generic human-review condition and can never be converted into PASS.
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
DEFAULT_RUNTIME_REQUIREMENTS = {
    "C3": ["ER-REL-DID-AB", "ER-TASK-AB", "ER-VERIFIER-AB"],
    "C5": ["ER-STATUS-AB", "ER-TASK-AB", "ER-VERIFIER-AB"],
}


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


def supplied_ids(setup: dict[str, Any]) -> list[str]:
    # Comparable reruns may carry explicit evidence bindings from RAHP/Interop Lab.
    # A requirement is satisfied only when a binding states the requirement ID and
    # supplies attributable provenance; synthetic repository fixtures do not satisfy it.
    supplied: list[str] = []
    for binding in setup.get("provided_evidence", []) or []:
        if not isinstance(binding, dict):
            continue
        rid = str(binding.get("requirement_id") or "").strip()
        provenance = binding.get("provenance")
        if rid and provenance:
            supplied.append(rid)
    return list(dict.fromkeys(supplied))


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
    supplied = set(supplied_ids(setup))
    missing_requirements: list[dict[str, Any]] = []
    for rid in required:
        if rid in supplied:
            continue
        meta = req_catalog.get(rid)
        if not isinstance(meta, dict):
            missing.append(f"unknown evidence requirement: {rid}")
            continue
        missing_requirements.append({
            "id": rid,
            "title": meta.get("title"),
            "summary": meta.get("summary"),
            "evidence_kind": meta.get("evidence_kind"),
            "source_lineage": meta.get("source_lineage", []),
        })
    if missing_requirements:
        missing.append("required attributable runtime evidence not supplied: " + ", ".join(item["id"] for item in missing_requirements))

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
            "producer_lineage": req.get("source_lineage", []),
            "acceptance_criterion": "Supply attributable provenance-bound evidence for this requirement in a comparable pinned rerun.",
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
    missing = [str(item) for item in record.get("missing_evidence", []) if str(item).strip()]
    named = [f"{r.get('id')} — {r.get('title')}" for r in record.get("required_evidence", []) or []]
    explanation = "The admitted privacy proposition is understood, but the evidence contract is not satisfied. "
    if named:
        explanation += "Missing evidence: " + "; ".join(named) + ". "
    explanation += "Repository-native fixtures may exercise DPIP rules but do not prove upstream runtime behaviour."
    action = "Produce the named attributable runtime evidence and create a pinned comparable DPIP rerun."
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
        body = f"{marker}\n## DPIP repository-native execution — {record['status']}\n\n{_human_scope_md(record.get('human_scope', []))}\n\nMissing evidence remains explicit; repository fixtures are not promoted into runtime proof.\n\n```yaml\n{yaml.safe_dump(evidence, sort_keys=False).rstrip()}\n```"
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
