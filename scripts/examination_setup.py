#!/usr/bin/env python3
"""Materialize deterministic, non-judgmental DPIP examination setup for admitted RAHP requests."""
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

from rahp_intake import api, intake_payload, labels, canonical_scope

DEFAULT_REPO = "sankarshanmukhopadhyay/dtg-privacy-implementation-profile"
SOURCE_LABEL = "source:rahp"
IN_PROGRESS = "run:in-progress"
REGISTRY = Path("portfolio/rahp-examination-bindings.yaml")
GLOSSARY = Path("portfolio/identifier-glossary.yaml")
EVIDENCE_REQUIREMENTS = Path("portfolio/evidence-requirements.yaml")
EXAMPLES = Path("examples")
FLOWS = Path("reference-system/flows")
SHA40 = re.compile(r"^[0-9a-f]{40}$", re.I)


def load_yaml(path: Path) -> dict[str, Any]:
    value = yaml.safe_load(path.read_text())
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain a mapping")
    return value


def canonical_catalog() -> dict[str, Any]:
    interactions: dict[str, dict[str, Any]] = {}
    claims: dict[str, dict[str, Any]] = {}
    profiles: set[str] = set()
    invariants: set[str] = set()
    for path in sorted(EXAMPLES.glob("*.yaml")):
        doc = yaml.safe_load(path.read_text()) or {}
        interaction = doc.get("interaction") or {}
        iid = interaction.get("id")
        if iid:
            interactions[str(iid)] = {"path": str(path), **interaction}
            profiles.update([str(interaction["target_profile"])]) if interaction.get("target_profile") else None
            invariants.update(str(v) for v in interaction.get("invariants", []) or [])
        for claim in doc.get("privacy_claims", []) or []:
            if claim.get("id"):
                claims[str(claim["id"])] = {"path": str(path), **claim}
    flows: dict[str, dict[str, Any]] = {}
    for path in sorted(FLOWS.glob("*.yaml")):
        doc = yaml.safe_load(path.read_text()) or {}
        flow = doc.get("flow") or doc.get("reference_flow") or doc
        fid = flow.get("id") if isinstance(flow, dict) else None
        if fid:
            flows[str(fid)] = {"path": str(path), **flow}
    reqs = (load_yaml(EVIDENCE_REQUIREMENTS).get("requirements") or {}) if EVIDENCE_REQUIREMENTS.exists() else {}
    return {"interactions": interactions, "claims": claims, "profiles": profiles, "invariants": invariants, "flows": flows, "evidence_requirements": reqs}


def map_many(values: list[Any], mapping: dict[str, Any], key: str = "canonical") -> tuple[list[str], list[str]]:
    out: list[str] = []
    missing: list[str] = []
    for raw in values or []:
        name = str(raw)
        entry = mapping.get(name)
        if entry is None:
            missing.append(name)
            continue
        vals = entry if isinstance(entry, list) else entry.get(key, [])
        for item in vals:
            if str(item) not in out:
                out.append(str(item))
    return out, missing


def structural_source_pins(source: dict[str, Any], body: str) -> list[dict[str, str]]:
    pins: list[dict[str, str]] = []
    for raw in source.get("source_pins", []) or []:
        if not isinstance(raw, dict):
            continue
        repo = str(raw.get("repository") or "").strip()
        revision = str(raw.get("revision") or "").strip()
        if repo and SHA40.fullmatch(revision):
            pins.append({"label": str(raw.get("label") or repo), "repository": repo, "revision": revision})
    changed = source.get("changed_artifact") if isinstance(source.get("changed_artifact"), dict) else {}
    repo = str(changed.get("repository") or "").strip()
    revision = str(changed.get("revision") or "").strip()
    if repo and SHA40.fullmatch(revision) and not any(p["repository"] == repo and p["revision"].lower() == revision.lower() for p in pins):
        pins.insert(0, {"label": "Changed artifact", "repository": repo, "revision": revision})
    # Backward-compatible Markdown pins from historical RAHP intakes.
    for match in re.finditer(r"^-\s+([^\[\n]+?)\s+\[repo=([A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+)\]:\s+`([0-9a-f]{40})`\s*$", body or "", re.MULTILINE | re.I):
        pin = {"label": match.group(1).strip(), "repository": match.group(2), "revision": match.group(3)}
        if not any(p.get("repository") == pin["repository"] and p["revision"].lower() == pin["revision"].lower() for p in pins):
            pins.append(pin)
    for match in re.finditer(r"^-\s+([^:\n]+):\s+`([0-9a-f]{40})`\s*$", body or "", re.MULTILINE | re.I):
        if not any(p["revision"].lower() == match.group(2).lower() for p in pins):
            pins.append({"label": match.group(1).strip(), "revision": match.group(2)})
    return pins


def _dedupe(values: list[str]) -> list[str]:
    return list(dict.fromkeys(str(v) for v in values if str(v)))


def _validate_ids(ids: list[str], allowed: Any, kind: str, unresolved: list[str]) -> list[str]:
    out = _dedupe(ids)
    for identifier in out:
        if identifier not in allowed:
            unresolved.append(f"unknown canonical {kind} identifier: {identifier}")
    return out


def _human_entry(identifier: str, kind: str, glossary: dict[str, Any], catalog: dict[str, Any]) -> dict[str, Any]:
    section = {"interaction": "interactions", "invariant": "invariants", "profile": "profiles", "reference_flow": "reference_flows"}.get(kind)
    if section:
        meta = (glossary.get(section) or {}).get(identifier)
        if isinstance(meta, dict):
            return {"id": identifier, "kind": kind, "title": meta.get("title"), "summary": meta.get("summary")}
    if kind == "claim":
        claim = catalog["claims"].get(identifier, {})
        prop = str(claim.get("property") or "Privacy claim").replace("-", " ").strip().title()
        subject = str(claim.get("subject") or "scoped subject").replace("-", " ")
        summary = claim.get("statement") or claim.get("description") or f"Evaluate {prop.lower()} for {subject}."
        return {"id": identifier, "kind": kind, "title": f"{prop} — {subject}", "summary": str(summary)}
    if kind == "evidence_requirement":
        req = catalog["evidence_requirements"].get(identifier, {})
        if isinstance(req, dict):
            return {"id": identifier, "kind": kind, "title": req.get("title"), "summary": req.get("summary")}
    return {"id": identifier, "kind": kind, "title": None, "summary": None}


def build_setup(issue_number: int, body: str, registry: dict[str, Any], catalog: dict[str, Any], glossary: dict[str, Any]) -> dict[str, Any]:
    source, requested = intake_payload(body)
    canonical = canonical_scope(requested)
    unresolved: list[str] = []

    # Typed canonical identifiers take precedence. Historical prose aliases remain supported.
    if canonical.get("interaction_ids"):
        interactions = _validate_ids(canonical["interaction_ids"], catalog["interactions"], "interaction", unresolved)
    else:
        interactions, missing = map_many(requested.get("interactions", []), registry.get("interaction_aliases", {})); unresolved += [f"unmapped interaction: {x}" for x in missing]
    if canonical.get("reference_flow_ids"):
        flows = _validate_ids(canonical["reference_flow_ids"], catalog["flows"], "reference flow", unresolved)
    else:
        flows, missing = map_many(requested.get("reference_flows", []), registry.get("reference_flow_aliases", {})); unresolved += [f"unmapped reference flow: {x}" for x in missing]
    if canonical.get("invariant_ids"):
        invariants = _validate_ids(canonical["invariant_ids"], catalog["invariants"], "invariant", unresolved)
    else:
        invariants, missing = map_many(requested.get("invariants", []), registry.get("invariant_aliases", {}), key=""); unresolved += [f"unmapped invariant: {x}" for x in missing]
    if canonical.get("claim_ids"):
        claims = _validate_ids(canonical["claim_ids"], catalog["claims"], "claim", unresolved)
    else:
        claims, missing = map_many(requested.get("claims", []), registry.get("claim_aliases", {})); unresolved += [f"unmapped claim: {x}" for x in missing]

    profiles = _validate_ids(canonical.get("profile_ids", []), catalog["profiles"], "profile", unresolved) if canonical.get("profile_ids") else []
    if not profiles:
        profiles = _dedupe([str(catalog["interactions"][iid].get("target_profile")) for iid in interactions if iid in catalog["interactions"] and catalog["interactions"][iid].get("target_profile")])
    evidence_ids = _validate_ids(canonical.get("evidence_requirement_ids", []), catalog["evidence_requirements"], "evidence requirement", unresolved)

    pins = structural_source_pins(source, body)
    if not pins:
        unresolved.append("no immutable 40-hex component source pins found in structural provenance or issue body")

    fixtures = [str(catalog["interactions"][iid].get("path")) for iid in interactions if catalog["interactions"].get(iid, {}).get("path")]
    human_scope: list[dict[str, Any]] = []
    for kind, ids in (("interaction", interactions), ("reference_flow", flows), ("invariant", invariants), ("profile", profiles), ("claim", claims), ("evidence_requirement", evidence_ids)):
        for identifier in ids:
            entry = _human_entry(identifier, kind, glossary, catalog)
            if not entry.get("title") or not entry.get("summary"):
                unresolved.append(f"canonical {kind} identifier lacks human-readable metadata: {identifier}")
            human_scope.append(entry)

    evidence_status = "evidence-required" if evidence_ids else "not-declared"
    setup = {"examination_setup": {
        "status": "ready" if not unresolved else "needs-review",
        "source_issue": issue_number,
        "source_provenance": source,
        "requested_question": requested.get("question"),
        "candidate_interactions": interactions,
        "candidate_reference_flows": flows,
        "candidate_invariants": invariants,
        "candidate_profiles": profiles,
        "candidate_claims": claims,
        "evidence_requirement_ids": evidence_ids,
        "evidence_status": evidence_status,
        "human_scope": human_scope,
        "evidence_surfaces": requested.get("suspected_surfaces", []),
        "existing_fixtures": fixtures,
        "source_pins": pins,
        "unresolved_bindings": unresolved,
        "applicability": "not-made",
        "privacy_judgment": "not-made",
        "human_acceptance_required": bool(unresolved),
    }}
    digest = hashlib.sha256(json.dumps(setup, sort_keys=True, separators=(",", ":")).encode()).hexdigest()[:16]
    setup["examination_setup"]["setup_digest"] = digest
    return setup


def comments(repo: str, number: int, token: str) -> list[dict[str, Any]]:
    return api("GET", repo, f"issues/{number}/comments?per_page=100", token) or []


def human_markdown(setup: dict[str, Any]) -> str:
    entries = setup.get("human_scope", []) or []
    if not entries:
        return ""
    lines = ["### What the identifiers mean", ""]
    for item in entries:
        lines.append(f"- **{item['id']} — {item['title']}**: {item['summary']}")
    return "\n".join(lines)


def publish(repo: str, issue: dict[str, Any], token: str, registry: dict[str, Any], catalog: dict[str, Any], glossary: dict[str, Any]) -> None:
    number = int(issue["number"])
    setup_doc = build_setup(number, issue.get("body") or "", registry, catalog, glossary)
    setup = setup_doc["examination_setup"]
    digest = setup["setup_digest"]
    marker = f"<!-- dpip-examination-setup:{number}:{digest} -->"
    if any(marker in (c.get("body") or "") for c in comments(repo, number, token)):
        print(f"UNCHANGED #{number}"); return
    status = setup["status"]
    intro = "The setup below is deterministic candidate binding only. It does **not** establish DPIP applicability or a privacy PASS/FAIL result. Known identifiers are resolved to canonical names for human review; unknown identifiers stop the deterministic path."
    body = f"{marker}\n## DPIP examination setup — {status}\n\n{intro}\n\n{human_markdown(setup)}\n\n```yaml\n{yaml.safe_dump(setup_doc, sort_keys=False).rstrip()}\n```"
    api("POST", repo, f"issues/{number}/comments", token, {"body": body})
    print(f"SETUP #{number}: {status}")


def eligible(issue: dict[str, Any]) -> bool:
    return not issue.get("pull_request") and {SOURCE_LABEL, IN_PROGRESS}.issubset(labels(issue))


def run(repo: str, token: str, issue_number: int | None = None) -> int:
    registry = load_yaml(REGISTRY); catalog = canonical_catalog(); glossary = load_yaml(GLOSSARY)
    if issue_number is not None:
        issue = api("GET", repo, f"issues/{issue_number}", token)
        if eligible(issue): publish(repo, issue, token, registry, catalog, glossary)
        else: print(f"SKIP #{issue_number}: not an admitted RAHP run")
        return 0
    issues = api("GET", repo, "issues?state=open&labels=source%3Arahp%2Crun%3Ain-progress&per_page=100", token) or []
    for issue in issues:
        if eligible(issue): publish(repo, issue, token, registry, catalog, glossary)
    return 0


def self_test() -> int:
    registry = load_yaml(REGISTRY); catalog = canonical_catalog(); glossary = load_yaml(GLOSSARY)
    dogwood = """```yaml
source:
  system: RAHP
  repository: sankarshanmukhopadhyay/rahp-toolkit
  issue: 225
  changed_artifact:
    repository: OpenVTC/verifiable-trust-infrastructure
    revision: cb01d0a758863fb3a02f9f4eef2c4f15f56c4c3b
  source_pins:
    - label: Dogwood RC-1
      repository: OpenVTC/verifiable-trust-infrastructure
      revision: cb01d0a758863fb3a02f9f4eef2c4f15f56c4c3b
```
```yaml
requested_examination:
  canonical:
    interaction_ids: [C3, C5]
    reference_flow_ids: [RF-001, RF-003]
    invariant_ids: [P2, P4, P5]
    profile_ids: [PP-4, PP-2]
    evidence_requirement_ids: [ER-REL-DID-AB, ER-STATUS-AB, ER-TASK-AB, ER-VERIFIER-AB]
  question: Does Dogwood preserve correlation resistance across the composed privacy boundary?
```"""
    setup = build_setup(120, dogwood, registry, catalog, glossary)["examination_setup"]
    assert setup["status"] == "ready", setup
    assert setup["candidate_interactions"] == ["C3", "C5"]
    assert setup["candidate_reference_flows"] == ["RF-001", "RF-003"]
    assert setup["source_pins"][0]["revision"] == "cb01d0a758863fb3a02f9f4eef2c4f15f56c4c3b"
    assert setup["evidence_status"] == "evidence-required"
    assert setup["human_acceptance_required"] is False
    c3 = next(item for item in setup["human_scope"] if item["id"] == "C3")
    assert c3["title"] == "Asymmetric cross-community relationship privacy"
    assert c3["summary"]
    bad = dogwood.replace("C3, C5", "C3, C999")
    blocked = build_setup(120, bad, registry, catalog, glossary)["examination_setup"]
    assert blocked["status"] == "needs-review"
    assert any("unknown canonical interaction" in x for x in blocked["unresolved_bindings"])
    print("PASS examination_setup self-test")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--issue-number", type=int)
    args = parser.parse_args()
    if args.self_test: return self_test()
    if not args.issue_number:
        print("--issue-number is required for runtime publication", file=sys.stderr); return 2
    token = os.getenv("GITHUB_TOKEN", "")
    if not token:
        print("GITHUB_TOKEN is required", file=sys.stderr); return 2
    repo = os.getenv("DPIP_REPOSITORY", DEFAULT_REPO)
    issue = api("GET", repo, f"issues/{args.issue_number}", token)
    if eligible(issue):
        publish(repo, issue, token, load_yaml(REGISTRY), canonical_catalog(), load_yaml(GLOSSARY))
    else:
        print(f"SKIP #{args.issue_number}: not an admitted RAHP run")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
