#!/usr/bin/env python3
"""Materialize deterministic, non-judgmental DPIP examination setup for admitted RAHP requests.

Operational contract:
- resolve admitted privacy scope to canonical interactions/claims/invariants/flows;
- derive required evidence contracts when the referral did not already supply them;
- preserve supplied evidence and immutable source provenance without judging sufficiency;
- never manufacture evidence or a privacy conclusion.
"""
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
EVIDENCE_BINDINGS = Path("evidence/evidence-bindings.yaml")
EXAMPLES = Path("examples")
FLOWS = Path("reference-system/flows")
SHA40 = re.compile(r"^[0-9a-f]{40}$", re.I)


def load_yaml(path: Path) -> dict[str, Any]:
    value = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain a mapping")
    return value


def canonical_catalog() -> dict[str, Any]:
    interactions: dict[str, dict[str, Any]] = {}
    claims: dict[str, dict[str, Any]] = {}
    profiles: set[str] = set()
    invariants: set[str] = set()
    for path in sorted(EXAMPLES.glob("*.yaml")):
        doc = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        interaction = doc.get("interaction") or {}
        iid = interaction.get("id")
        if iid:
            interactions[str(iid)] = {"path": str(path), **interaction}
            if interaction.get("target_profile"):
                profiles.add(str(interaction["target_profile"]))
            invariants.update(str(v) for v in interaction.get("invariants", []) or [])
        for claim in doc.get("privacy_claims", []) or []:
            if claim.get("id"):
                claims[str(claim["id"])] = {"path": str(path), **claim}
    flows: dict[str, dict[str, Any]] = {}
    for path in sorted(FLOWS.glob("*.yaml")):
        doc = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
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
    if repo and SHA40.fullmatch(revision) and not any(p.get("repository") == repo and p["revision"].lower() == revision.lower() for p in pins):
        pins.insert(0, {"label": "Changed artifact", "repository": repo, "revision": revision})
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
        return {"id": identifier, "kind": kind, "title": req.get("title"), "summary": req.get("summary")} if isinstance(req, dict) else {"id": identifier, "kind": kind}
    return {"id": identifier, "kind": kind, "title": None, "summary": None}


def _provided_evidence(requested: dict[str, Any], unresolved: list[str]) -> list[dict[str, Any]]:
    value = requested.get("provided_evidence", [])
    if value is None:
        return []
    if not isinstance(value, list):
        unresolved.append("requested_examination.provided_evidence must be a list")
        return []
    out: list[dict[str, Any]] = []
    for index, item in enumerate(value):
        if not isinstance(item, dict):
            unresolved.append(f"provided_evidence[{index}] must be a mapping")
        else:
            out.append(item)
    return out


def _matches_any(actual: list[str], wanted: list[str]) -> bool:
    return not wanted or bool(set(actual) & set(wanted))


def derive_evidence_requirements(interactions: list[str], claims: list[str], surfaces: list[str], catalog: dict[str, Any]) -> list[str]:
    """Resolve evidence contracts from semantic scope, never from issue/referral identity."""
    doc = load_yaml(EVIDENCE_BINDINGS)
    resolved: list[str] = []
    normalized_surfaces = [str(v).strip().lower() for v in surfaces or []]
    for binding in doc.get("bindings", []) or []:
        if not isinstance(binding, dict):
            continue
        match = binding.get("match") if isinstance(binding.get("match"), dict) else {}
        if not _matches_any(interactions, [str(v) for v in match.get("interactions_any", []) or []]):
            continue
        if not _matches_any(claims, [str(v) for v in match.get("claims_any", []) or []]):
            continue
        wanted_surfaces = [str(v).strip().lower() for v in match.get("surfaces_any", []) or []]
        if wanted_surfaces and not any(any(w in surface or surface in w for surface in normalized_surfaces) for w in wanted_surfaces):
            continue
        for rid in binding.get("evidence_requirement_ids", []) or []:
            rid = str(rid)
            if rid not in catalog["evidence_requirements"]:
                raise ValueError(f"evidence binding {binding.get('id')} references unknown requirement {rid}")
            if rid not in resolved:
                resolved.append(rid)
    return resolved


def build_setup(issue_number: int, body: str, registry: dict[str, Any], catalog: dict[str, Any], glossary: dict[str, Any]) -> dict[str, Any]:
    source, requested = intake_payload(body)
    canonical = canonical_scope(requested)
    unresolved: list[str] = []

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
        profiles = _dedupe([str(catalog["interactions"][iid].get("target_profile")) for iid in interactions if catalog["interactions"].get(iid, {}).get("target_profile")])

    explicit_evidence = canonical.get("evidence_requirement_ids", []) or []
    evidence_ids = _validate_ids(explicit_evidence, catalog["evidence_requirements"], "evidence requirement", unresolved)
    if not evidence_ids:
        evidence_ids = derive_evidence_requirements(interactions, claims, requested.get("suspected_surfaces", []) or [], catalog)
    supplied_evidence = _provided_evidence(requested, unresolved)

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

    evidence_status = "evidence-supplied-for-evaluation" if supplied_evidence else ("evidence-required" if evidence_ids else "model-gap")
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
        "provided_evidence": supplied_evidence,
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
    setup["examination_setup"]["setup_digest"] = hashlib.sha256(json.dumps(setup, sort_keys=True, separators=(",", ":")).encode()).hexdigest()[:16]
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
    intro = "The setup below is deterministic candidate binding only. It does **not** establish DPIP applicability, evidence sufficiency, or a privacy PASS/FAIL result."
    body = f"{marker}\n## DPIP examination setup — {setup['status']}\n\n{intro}\n\n{human_markdown(setup)}\n\n```yaml\n{yaml.safe_dump(setup_doc, sort_keys=False).rstrip()}\n```"
    api("POST", repo, f"issues/{number}/comments", token, {"body": body})
    print(f"SETUP #{number}: {setup['status']}")


def eligible(issue: dict[str, Any]) -> bool:
    return not issue.get("pull_request") and {SOURCE_LABEL, IN_PROGRESS}.issubset(labels(issue))


def self_test() -> int:
    registry = load_yaml(REGISTRY); catalog = canonical_catalog(); glossary = load_yaml(GLOSSARY)
    pin = "cb01d0a758863fb3a02f9f4eef2c4f15f56c4c3b"
    relationship = f"""```yaml
source:
  system: RAHP
  changed_artifact: {{repository: OpenVTC/verifiable-trust-infrastructure, revision: {pin}}}
```
```yaml
requested_examination:
  canonical:
    interaction_ids: [C3, C5]
    reference_flow_ids: [RF-001, RF-003]
    invariant_ids: [P2, P4, P5]
    claim_ids: [C3-PC-2, C5-PC-2, C3-PC-4, C3-PC-5, C5-PC-4]
    profile_ids: [PP-4, PP-2]
  suspected_surfaces: [relationship DID and edge identifiers, status and policy discovery traffic, retained relationship evidence, deliberate-correlation mechanisms]
  question: relationship correlation
```"""
    setup = build_setup(168, relationship, registry, catalog, glossary)["examination_setup"]
    assert setup["evidence_requirement_ids"] == ["ER-REL-DID-AB", "ER-STATUS-AB", "ER-TASK-AB", "ER-VERIFIER-AB"], setup
    assert setup["evidence_status"] == "evidence-required"
    assert setup["status"] == "ready", setup

    credential = f"""```yaml
source:
  system: RAHP
  changed_artifact: {{repository: example/credential-implementation, revision: {'a'*40}}}
```
```yaml
requested_examination:
  canonical:
    interaction_ids: [C3]
    invariant_ids: [P2, P4, P5]
    claim_ids: [C3-PC-2]
    profile_ids: [PP-4]
  suspected_surfaces: [credential identifier cross-context correlation]
  question: can a credential identifier join unrelated contexts?
```"""
    cred = build_setup(149, credential, registry, catalog, glossary)["examination_setup"]
    assert cred["evidence_requirement_ids"] == ["ER-CREDENTIAL-ID-AB"], cred
    assert cred["evidence_status"] == "evidence-required"

    replay = build_setup(999, relationship, registry, catalog, glossary)["examination_setup"]
    assert replay["evidence_requirement_ids"] == setup["evidence_requirement_ids"]
    print("PASS examination_setup semantic evidence binding regressions (#149/#168)")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--issue-number", type=int)
    args = parser.parse_args()
    if args.self_test:
        return self_test()
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
