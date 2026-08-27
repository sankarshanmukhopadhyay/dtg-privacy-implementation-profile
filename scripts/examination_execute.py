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
            mechanical_results.append({
                "interaction": iid,
                "vector": result.get("_vector_id"),
                "test_results": result.get("test_results", []),
                "claim_results": result.get("claim_results", []),
            })

    state = "evidence-ready" if checks and not missing else "evidence-incomplete"
    execution = {
        "execution_evidence": {
            "status": state,
            "source_issue": issue_number,
            "setup_digest": setup.get("setup_digest"),
            "candidate_interactions": setup.get("candidate_interactions", []),
            "candidate_profiles": setup.get("candidate_profiles", []),
            "checks": checks,
            "mechanical_results": mechanical_results,
            "missing_evidence": missing,
            "source_pins": setup.get("source_pins", []),
            "privacy_judgment": "not-made",
            "human_acceptance_required": True,
        }
    }
    digest = hashlib.sha256(json.dumps(execution, sort_keys=True, separators=(",", ":")).encode()).hexdigest()[:16]
    execution["execution_evidence"]["execution_digest"] = digest
    return execution


def conclusion_from_execution(execution: dict[str, Any]) -> dict[str, Any] | None:
    record = execution["execution_evidence"]
    status = record.get("status")
    if status == "evidence-incomplete":
        missing = [str(item) for item in record.get("missing_evidence", []) if str(item).strip()]
        summary = (
            "DPIP confirmed the requested privacy scope is applicable and resolved, but the available "
            "repository/source evidence is insufficient to make the requested privacy claim. "
            + ("Missing executable/runtime evidence: " + "; ".join(missing) if missing else
               "Required executable/runtime evidence is unavailable.")
        )
        action = (
            "Obtain the missing runtime/executable evidence identified by this examination, "
            "then rerun the DPIP examination before asserting the composed privacy claim."
        )
        return {
            "dpip_examination": {
                "applicability": "applicable",
                "conclusion": "INDETERMINATE",
                "affected_interactions": record.get("candidate_interactions", []),
                "affected_claims": [],
                "affected_invariants": [],
                "evidence_summary": summary,
                "residual_correlation": "Cross-context correlation cannot be ruled in or out from source-backed evidence alone.",
                "action": action,
                "human_summary": {
                    "outcome": "We do not have enough evidence to decide yet",
                    "explanation": summary,
                    "action": action,
                },
                "source_pins": record.get("source_pins", []),
                "execution_digest": record.get("execution_digest"),
                "human_acceptance_required": True,
            }
        }
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
    if any(marker in (c.get("body") or "") for c in existing):
        print(f"UNCHANGED #{number}")
        return
    status = evidence["execution_evidence"]["status"]
    body = (
        f"{marker}\n## DPIP repository-native execution — {status}\n\n"
        "This stage executes only mechanically available repository evidence. Missing evidence remains explicit; this comment is **not** the DPIP privacy disposition.\n\n"
        f"```yaml\n{yaml.safe_dump(evidence, sort_keys=False).rstrip()}\n```"
    )
    api("POST", repo, f"issues/{number}/comments", token, {"body": body})
    conclusion = conclusion_from_execution(evidence)
    if conclusion is not None:
        conclusion_digest = hashlib.sha256(
            json.dumps(conclusion, sort_keys=True, separators=(",", ":")).encode()
        ).hexdigest()[:16]
        conclusion_marker = f"<!-- dpip-examination:{number}:{conclusion_digest} -->"
        conclusion_body = (
            f"{conclusion_marker}\n## DPIP scoped conclusion — {conclusion['dpip_examination']['conclusion']}\n\n"
            "This is the DPIP disposition for the evidence currently available. It preserves missing-evidence boundaries rather than converting them into a privacy pass.\n\n"
            f"```yaml\n{yaml.safe_dump(conclusion, sort_keys=False).rstrip()}\n```"
        )
        api("POST", repo, f"issues/{number}/comments", token, {"body": conclusion_body})
        api("POST", repo, f"issues/{number}/labels", token, {"labels": ["run:complete"]})
        try:
            api("DELETE", repo, f"issues/{number}/labels/run%3Ain-progress", token)
        except Exception:
            pass
    print(f"EXECUTION #{number}: {status}")


def eligible(issue: dict[str, Any]) -> bool:
    return not issue.get("pull_request") and {SOURCE_LABEL, IN_PROGRESS}.issubset(labels(issue))


def run(repo: str, token: str, issue_number: int | None = None) -> int:
    if issue_number is not None:
        issue = api("GET", repo, f"issues/{issue_number}", token)
        if eligible(issue):
            publish(repo, issue, token)
        else:
            print(f"SKIP #{issue_number}: not an admitted RAHP run")
        return 0
    issues = api("GET", repo, "issues?state=open&labels=source%3Arahp%2Crun%3Ain-progress&per_page=100", token) or []
    for issue in issues:
        if eligible(issue):
            publish(repo, issue, token)
    return 0


def self_test() -> int:
    incomplete = build_execution(65, {
        "setup_digest": "example",
        "candidate_interactions": ["C3", "C5"],
        "candidate_profiles": ["PP-4", "PP-2"],
        "source_pins": [{"label": "example", "revision": "a" * 40}],
    })["execution_evidence"]
    assert incomplete["status"] == "evidence-incomplete"
    assert any("C3" in item for item in incomplete["missing_evidence"])
    assert any("C5" in item for item in incomplete["missing_evidence"])
    assert incomplete["privacy_judgment"] == "not-made"
    incomplete_conclusion = conclusion_from_execution({"execution_evidence": incomplete})
    assert incomplete_conclusion["dpip_examination"]["conclusion"] == "INDETERMINATE"
    assert incomplete_conclusion["dpip_examination"]["applicability"] == "applicable"
    assert "missing" in incomplete_conclusion["dpip_examination"]["evidence_summary"].lower()

    ready = build_execution(63, {
        "setup_digest": "protected-access",
        "candidate_interactions": ["C8"],
        "candidate_profiles": ["PP-5"],
        "source_pins": [{"label": "example", "revision": "b" * 40}],
    })["execution_evidence"]
    assert ready["status"] == "evidence-ready", ready
    assert ready["mechanical_results"], ready
    assert ready["privacy_judgment"] == "not-made"
    print("PASS examination_execute self-test")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--issue-number", type=int)
    args = parser.parse_args()
    if args.self_test:
        return self_test()
    token = os.environ.get("GITHUB_TOKEN", "")
    if not token:
        sys.exit("GITHUB_TOKEN is required")
    repo = os.environ.get("DPIP_REPOSITORY", DEFAULT_REPO)
    return run(repo, token, args.issue_number)


if __name__ == "__main__":
    raise SystemExit(main())
