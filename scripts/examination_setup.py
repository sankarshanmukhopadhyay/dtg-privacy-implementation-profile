#!/usr/bin/env python3
"""Materialize non-judgmental DPIP examination setup for admitted RAHP requests."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
import urllib.request
from pathlib import Path
from typing import Any

import yaml

from rahp_intake import api, intake_payload, labels

DEFAULT_REPO = "sankarshanmukhopadhyay/dtg-privacy-implementation-profile"
SOURCE_LABEL = "source:rahp"
IN_PROGRESS = "run:in-progress"
REGISTRY = Path("portfolio/rahp-examination-bindings.yaml")
EXAMPLES = Path("examples")
FLOWS = Path("reference-system/flows")


def load_registry(path: Path = REGISTRY) -> dict[str, Any]:
    value = yaml.safe_load(path.read_text())
    if not isinstance(value, dict):
        raise ValueError("binding registry must be a mapping")
    return value


def canonical_catalog() -> dict[str, dict[str, Any]]:
    interactions: dict[str, dict[str, Any]] = {}
    claims: dict[str, dict[str, Any]] = {}
    profiles: set[str] = set()
    for path in sorted(EXAMPLES.glob("*.yaml")):
        doc = yaml.safe_load(path.read_text()) or {}
        interaction = doc.get("interaction") or {}
        iid = interaction.get("id")
        if iid:
            interactions[str(iid)] = {"path": str(path), **interaction}
            if interaction.get("target_profile"):
                profiles.add(str(interaction["target_profile"]))
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
    return {"interactions": interactions, "claims": claims, "profiles": {p: {} for p in profiles}, "flows": flows}


def extract_source_pins(body: str) -> list[dict[str, str]]:
    pins: list[dict[str, str]] = []
    for match in re.finditer(r"^-\s+([^:\n]+):\s+`([0-9a-f]{40})`\s*$", body or "", re.MULTILINE | re.IGNORECASE):
        pins.append({"label": match.group(1).strip(), "revision": match.group(2)})
    return pins


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


def build_setup(issue_number: int, body: str, registry: dict[str, Any], catalog: dict[str, dict[str, Any]]) -> dict[str, Any]:
    source, requested = intake_payload(body)
    interactions, mi = map_many(requested.get("interactions", []), registry.get("interaction_aliases", {}))
    invariants, mv = map_many(requested.get("invariants", []), registry.get("invariant_aliases", {}), key="")
    claims, mc = map_many(requested.get("claims", []), registry.get("claim_aliases", {}))
    flows, mf = map_many(requested.get("reference_flows", []), registry.get("reference_flow_aliases", {}))

    unresolved = []
    unresolved += [f"unmapped interaction: {x}" for x in mi]
    unresolved += [f"unmapped invariant: {x}" for x in mv]
    unresolved += [f"unmapped claim: {x}" for x in mc]
    unresolved += [f"unmapped reference flow: {x}" for x in mf]

    for iid in interactions:
        if iid not in catalog["interactions"]:
            unresolved.append(f"binding references missing canonical interaction: {iid}")
    for cid in claims:
        if cid not in catalog["claims"]:
            unresolved.append(f"binding references missing canonical claim: {cid}")
    for fid in flows:
        if fid not in catalog["flows"]:
            unresolved.append(f"binding references missing canonical reference flow: {fid}")

    profiles: list[str] = []
    fixtures: list[str] = []
    for iid in interactions:
        item = catalog["interactions"].get(iid, {})
        if item.get("target_profile") and str(item["target_profile"]) not in profiles:
            profiles.append(str(item["target_profile"]))
        if item.get("path"):
            fixtures.append(str(item["path"]))

    pins = extract_source_pins(body)
    if not pins:
        unresolved.append("no immutable 40-hex component source pins found in issue body")

    setup = {
        "examination_setup": {
            "status": "ready" if not unresolved else "needs-review",
            "source_issue": issue_number,
            "source_provenance": source,
            "requested_question": requested.get("question"),
            "candidate_interactions": interactions,
            "candidate_reference_flows": flows,
            "candidate_invariants": invariants,
            "candidate_profiles": profiles,
            "candidate_claims": claims,
            "evidence_surfaces": requested.get("suspected_surfaces", []),
            "existing_fixtures": fixtures,
            "source_pins": pins,
            "unresolved_bindings": unresolved,
            "applicability": "not-made",
            "privacy_judgment": "not-made",
            "human_acceptance_required": True,
        }
    }
    digest = hashlib.sha256(json.dumps(setup, sort_keys=True, separators=(",", ":")).encode()).hexdigest()[:16]
    setup["examination_setup"]["setup_digest"] = digest
    return setup


def comments(repo: str, number: int, token: str) -> list[dict[str, Any]]:
    return api("GET", repo, f"issues/{number}/comments?per_page=100", token) or []


def publish(repo: str, issue: dict[str, Any], token: str, registry: dict[str, Any], catalog: dict[str, dict[str, Any]]) -> None:
    number = int(issue["number"])
    setup = build_setup(number, issue.get("body") or "", registry, catalog)
    digest = setup["examination_setup"]["setup_digest"]
    marker = f"<!-- dpip-examination-setup:{number}:{digest} -->"
    if any(marker in (c.get("body") or "") for c in comments(repo, number, token)):
        print(f"UNCHANGED #{number}")
        return
    status = setup["examination_setup"]["status"]
    intro = (
        "The setup below is deterministic candidate binding only. It does **not** establish DPIP applicability, evidence sufficiency, or a privacy disposition."
    )
    body = f"{marker}\n## DPIP examination setup — {status}\n\n{intro}\n\n```yaml\n{yaml.safe_dump(setup, sort_keys=False).rstrip()}\n```"
    api("POST", repo, f"issues/{number}/comments", token, {"body": body})
    print(f"SETUP #{number}: {status}")


def eligible(issue: dict[str, Any]) -> bool:
    return not issue.get("pull_request") and {SOURCE_LABEL, IN_PROGRESS}.issubset(labels(issue))


def run(repo: str, token: str, issue_number: int | None = None) -> int:
    registry = load_registry()
    catalog = canonical_catalog()
    if issue_number is not None:
        issue = api("GET", repo, f"issues/{issue_number}", token)
        if eligible(issue):
            publish(repo, issue, token, registry, catalog)
        else:
            print(f"SKIP #{issue_number}: not an admitted RAHP run")
        return 0
    encoded = urllib.request.quote if False else None
    issues = api("GET", repo, "issues?state=open&labels=source%3Arahp%2Crun%3Ain-progress&per_page=100", token) or []
    for issue in issues:
        if eligible(issue):
            publish(repo, issue, token, registry, catalog)
    return 0


def self_test() -> int:
    registry = load_registry()
    catalog = canonical_catalog()
    body = """```yaml
source:
  system: RAHP
  repository: example/rahp
  issue: 91
  changed_artifact:
    repository: example/rahp
    revision: main-after-pr-90
```
```yaml
requested_examination:
  interactions: [credential-proof-trust-task-consequential-execution]
  reference_flows: [DTG Credential -> ZKP presentation -> Trust Task -> retained outcome evidence]
  invariants: [no-unnecessary-cross-context-correlation, correlation-scope-does-not-expand-through-composition, retained-evidence-does-not-defeat-selective-disclosure]
  claims: [pairwise-identifiers-preserve-declared-correlation-scope, zero-knowledge-disclosure-remains-private-after-task-wrapping, retained-task-proof-status-and-outcome-evidence-do-not-enable-unintended-linkage]
  suspected_surfaces: [protocol-envelope, retained-evidence]
  question: Does effective correlation exceed declared scope?
```
## Source pins
- Trust Tasks Framework v0.5.0: `6425a74136c1d2dfa7115889abe0b3521700e887`
"""
    setup = build_setup(65, body, registry, catalog)["examination_setup"]
    assert setup["status"] == "ready", setup
    assert set(setup["candidate_interactions"]) == {"C3", "C5"}
    assert set(setup["candidate_profiles"]) == {"PP-4", "PP-2"}
    assert setup["privacy_judgment"] == "not-made"
    bad = body.replace("credential-proof-trust-task-consequential-execution", "unknown-interaction")
    blocked = build_setup(66, bad, registry, catalog)["examination_setup"]
    assert blocked["status"] == "needs-review"
    assert any("unmapped interaction" in x for x in blocked["unresolved_bindings"])
    print("PASS examination_setup self-test")
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
