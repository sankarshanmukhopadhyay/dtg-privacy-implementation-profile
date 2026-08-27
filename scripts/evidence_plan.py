#!/usr/bin/env python3
"""Compile deterministic DPIP evidence acquisition plans from examination setup records."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
from pathlib import Path
from typing import Any

import jsonschema
import yaml

from rahp_intake import api

DEFAULT_REPO = "sankarshanmukhopadhyay/dtg-privacy-implementation-profile"
RULES = Path("portfolio/evidence-acquisition-rules.yaml")
SCHEMA = Path("schema/evidence-plan.schema.json")


def yaml_blocks(text: str) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for match in re.finditer(r"```ya?ml\s*\n(.*?)```", text or "", re.DOTALL | re.IGNORECASE):
        try:
            value = yaml.safe_load(match.group(1))
        except yaml.YAMLError:
            continue
        if isinstance(value, dict):
            out.append(value)
    return out


def latest_setup(comments: list[dict[str, Any]]) -> dict[str, Any]:
    for comment in reversed(comments):
        for block in yaml_blocks(comment.get("body") or ""):
            setup = block.get("examination_setup")
            if isinstance(setup, dict):
                return setup
    raise ValueError("no structured examination_setup found")


def task_id(surface: str) -> str:
    slug = re.sub(r"[^A-Z0-9]+", "-", surface.upper()).strip("-")
    digest = hashlib.sha256(surface.encode("utf-8")).hexdigest()[:6].upper()
    return f"EA-{slug[:44]}-{digest}"


def build_plan(setup: dict[str, Any], rules: dict[str, Any]) -> dict[str, Any]:
    unresolved: list[str] = []
    tasks: list[dict[str, Any]] = []
    surface_rules = rules.get("surface_rules", {})
    contexts = rules.get("contexts", [])
    context_ids = [str(c["id"]) for c in contexts]

    for surface in setup.get("evidence_surfaces", []) or []:
        rule = surface_rules.get(str(surface))
        if not isinstance(rule, dict):
            unresolved.append(f"unmapped evidence surface: {surface}")
            continue
        tasks.append({
            "id": task_id(str(surface)),
            "surface": str(surface),
            "component": str(rule["component"]),
            "observer": str(rule["observer"]),
            "contexts": context_ids,
            "retention_stage": str(rule["retention_stage"]),
            "availability": "missing",
            "falsification_purpose": str(rule["falsification_purpose"]),
            "collector": str(rule["collector"]),
        })

    join = rules.get("join_policy", {})
    join_attempts: list[dict[str, Any]] = []
    if tasks:
        for task in tasks:
            join_attempts.append({
                "id": f"JOIN-{task['id'][3:]}",
                "task_ids": [task["id"]],
                "contexts": list(join.get("contexts", context_ids)),
                "basis": str(join.get("basis", "")),
                "expected_question": str(join.get("expected_question", "")),
            })
    else:
        unresolved.append("no acquisition tasks could be compiled")

    plan = {
        "version": "1",
        "source_issue": int(setup["source_issue"]),
        "setup_digest": str(setup["setup_digest"]),
        "source_pins": setup.get("source_pins", []),
        "candidate_interactions": setup.get("candidate_interactions", []),
        "candidate_profiles": setup.get("candidate_profiles", []),
        "candidate_claims": setup.get("candidate_claims", []),
        "candidate_invariants": setup.get("candidate_invariants", []),
        "contexts": contexts,
        "acquisition_tasks": tasks,
        "join_attempts": join_attempts,
        "unresolved_requirements": unresolved,
        "status": "needs-review" if unresolved else "ready",
        "judgment_boundary": rules.get("judgment_boundary", {
            "applicability": "not-made", "privacy_judgment": "not-made", "human_acceptance_required": True
        }),
    }
    jsonschema.validate(plan, json.loads(SCHEMA.read_text()))
    return plan


def plan_digest(plan: dict[str, Any]) -> str:
    return hashlib.sha256(json.dumps(plan, sort_keys=True, separators=(",", ":")).encode()).hexdigest()[:16]


def render_plan_comment(number: int, plan: dict[str, Any]) -> str:
    """Render the exact machine-readable issue-comment handoff consumed downstream."""
    marker = f"<!-- dpip-evidence-plan:{number}:{plan_digest(plan)} -->"
    payload = {"evidence_plan": plan}
    rendered = yaml.safe_dump(payload, sort_keys=False, allow_unicode=True).rstrip()
    # Assert the serialized transport is itself executable before publication.
    parsed = yaml.safe_load(rendered)
    if not isinstance(parsed, dict) or parsed.get("evidence_plan") != plan:
        raise ValueError("rendered evidence-plan payload does not round-trip")
    return (
        f"{marker}\n## DPIP evidence acquisition plan — {plan['status']}\n\n"
        "This is an executable acquisition contract. It identifies evidence to obtain; it does **not** assert that the evidence exists or make a privacy disposition.\n\n"
        f"```yaml\n{rendered}\n```"
    )


def comments(repo: str, number: int, token: str) -> list[dict[str, Any]]:
    return api("GET", repo, f"issues/{number}/comments?per_page=100", token) or []


def publish(repo: str, number: int, token: str) -> None:
    current = comments(repo, number, token)
    setup = latest_setup(current)
    rules = yaml.safe_load(RULES.read_text())
    plan = build_plan(setup, rules)
    digest = plan_digest(plan)
    marker = f"<!-- dpip-evidence-plan:{number}:{digest} -->"
    existing = next((c for c in current if marker in (c.get("body") or "")), None)
    if existing:
        # Old malformed comments with the same semantic digest must not prevent a
        # corrected transport record from being published.
        blocks = yaml_blocks(existing.get("body") or "")
        if any(isinstance(block.get("evidence_plan"), dict) and block["evidence_plan"] == plan for block in blocks):
            print(f"UNCHANGED #{number}")
            return
        print(f"REPAIR #{number}: existing marker is not a valid round-trip evidence plan")
    body = render_plan_comment(number, plan)
    api("POST", repo, f"issues/{number}/comments", token, {"body": body})
    print(f"PLANNED #{number}: {plan['status']}")


def self_test() -> int:
    rules = yaml.safe_load(RULES.read_text())
    setup = {
        "source_issue": 65,
        "setup_digest": "dadeaa89d15b24b3",
        "candidate_interactions": ["C3", "C5"],
        "candidate_profiles": ["PP-4", "PP-2"],
        "candidate_claims": ["C3-PC-2", "C5-PC-2"],
        "candidate_invariants": ["P2", "P4", "P5", "P3", "P6"],
        "evidence_surfaces": list(rules["surface_rules"].keys()),
        "source_pins": [{"label": "Trust Tasks", "revision": "6425a74136c1d2dfa7115889abe0b3521700e887"}],
    }
    first = build_plan(setup, rules)
    second = build_plan(setup, rules)
    assert first == second
    assert first["status"] == "ready"
    assert len(first["contexts"]) == 2 and all(c["relationship"] == "unrelated" for c in first["contexts"])
    assert len(first["acquisition_tasks"]) == 6
    assert all(t["availability"] == "missing" for t in first["acquisition_tasks"])
    assert first["judgment_boundary"]["privacy_judgment"] == "not-made"

    rendered = render_plan_comment(65, first)
    blocks = yaml_blocks(rendered)
    assert len(blocks) == 1
    assert blocks[0]["evidence_plan"] == first
    assert f"dpip-evidence-plan:65:{plan_digest(first)}" in rendered

    bad = dict(setup)
    bad["evidence_surfaces"] = [setup["evidence_surfaces"][0], "unknown surface"]
    blocked = build_plan(bad, rules)
    assert blocked["status"] == "needs-review"
    assert len(blocked["acquisition_tasks"]) == 1
    assert any("unmapped evidence surface" in x for x in blocked["unresolved_requirements"])
    print("PASS evidence_plan self-test")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--issue-number", type=int)
    args = parser.parse_args()
    if args.self_test:
        return self_test()
    if not args.issue_number:
        print("--issue-number is required for runtime publication", file=sys.stderr)
        return 2
    token = os.getenv("GITHUB_TOKEN", "")
    if not token:
        print("GITHUB_TOKEN is required", file=sys.stderr)
        return 2
    publish(os.getenv("DPIP_REPOSITORY", DEFAULT_REPO), args.issue_number, token)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
