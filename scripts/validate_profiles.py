#!/usr/bin/env python3
"""Validate DPIP interaction profiles against schema and semantic traceability rules.

Operational contract:
- Checks repository profile structure, invariant scope, requirements/claims/tests, and internal traceability.
- This is repository conformance validation only; passing profiles do not prove an implementation's real-world privacy behaviour.
"""
from __future__ import annotations
import json
import sys
from pathlib import Path

try:
    import yaml
    from jsonschema import Draft202012Validator
except ImportError as exc:
    raise SystemExit(f"Missing validation dependency: {exc}")

ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = ROOT / "schema" / "interaction-profile.schema.json"
EXAMPLES = ROOT / "examples"


def semantic_errors(profile: dict) -> list[str]:
    errors: list[str] = []
    interaction_invariants = set(profile.get("interaction", {}).get("invariants", []))
    reqs = {r["id"]: r for r in profile.get("requirements", [])}
    claims = {c["id"]: c for c in profile.get("privacy_claims", [])}
    covered_requirements: set[str] = set()
    covered_claims: set[str] = set()

    for requirement in reqs.values():
        outside = set(requirement.get("invariants", [])) - interaction_invariants
        if outside:
            errors.append(
                f"{requirement['id']}: invariants outside interaction scope: {', '.join(sorted(outside))}"
            )

    for claim in claims.values():
        outside = set(claim.get("invariants", [])) - interaction_invariants
        if outside:
            errors.append(
                f"{claim['id']}: invariants outside interaction scope: {', '.join(sorted(outside))}"
            )

    for surface in profile.get("correlation_surfaces", []):
        scope = surface.get("correlation_scope")
        if scope:
            values = {
                scope.get("declared_scope"),
                scope.get("observable_scope"),
                scope.get("effective_scope"),
            }
            values.discard(None)
            if len(values) > 1 and not scope.get("scope_basis"):
                errors.append(
                    f"{surface['id']}: divergent declared/observable/effective scope requires scope_basis"
                )

    for test in profile.get("tests", []):
        test_id = test["id"]
        outside = set(test.get("invariants", [])) - interaction_invariants
        if outside:
            errors.append(
                f"{test_id}: invariants outside interaction scope: {', '.join(sorted(outside))}"
            )

        for rid in test.get("requirements", []):
            covered_requirements.add(rid)
            if rid not in reqs:
                errors.append(f"{test_id}: unknown requirement {rid}")

        for cid in test.get("claims", []):
            covered_claims.add(cid)
            if cid not in claims:
                errors.append(f"{test_id}: unknown privacy claim {cid}")

    for rid in sorted(set(reqs) - covered_requirements):
        errors.append(f"requirement {rid} has no test coverage")

    for cid in sorted(set(claims) - covered_claims):
        errors.append(f"privacy claim {cid} has no test coverage")

    return errors


def main() -> int:
    schema = json.loads(SCHEMA_PATH.read_text())
    validator = Draft202012Validator(schema)
    failed = False
    profiles = sorted(EXAMPLES.glob("c*-*.yaml"))
    if not profiles:
        print("No DPIP profiles found", file=sys.stderr)
        return 1

    for path in profiles:
        profile = yaml.safe_load(path.read_text())
        problems = [e.message for e in validator.iter_errors(profile)]
        problems.extend(semantic_errors(profile))
        if problems:
            failed = True
            print(f"FAIL {path.relative_to(ROOT)}")
            for problem in problems:
                print(f"  - {problem}")
        else:
            print(f"PASS {path.relative_to(ROOT)}")

    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
