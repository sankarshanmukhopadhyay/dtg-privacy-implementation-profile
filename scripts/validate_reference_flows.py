#!/usr/bin/env python3
"""Validate non-normative DPIP reference composed flows."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import yaml
from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
SCHEMA = ROOT / "schema" / "reference-flow.schema.json"
FLOW_DIR = ROOT / "reference-system" / "flows"
PROFILE_DIR = ROOT / "examples"


def canonical_ids() -> tuple[set[str], set[str], set[str], set[str]]:
    interactions: set[str] = set()
    requirements: set[str] = set()
    tests: set[str] = set()
    claims: set[str] = set()
    for path in sorted(PROFILE_DIR.glob("c*-*.yaml")):
        profile = yaml.safe_load(path.read_text())
        interactions.add(profile["interaction"]["id"])
        requirements.update(item["id"] for item in profile.get("requirements", []))
        tests.update(item["id"] for item in profile.get("tests", []))
        claims.update(item["id"] for item in profile.get("privacy_claims", []))
    return interactions, requirements, tests, claims


def semantic_errors(flow: dict) -> list[str]:
    errors: list[str] = []
    actors = {a["id"] for a in flow.get("actors", [])}
    components = {c["id"] for c in flow.get("components", [])}
    assumptions = {a["id"] for a in flow.get("assumptions", [])}
    interactions, requirements, tests, claims = canonical_ids()

    for step in flow.get("steps", []):
        sid = step["id"]
        if step["actor"] not in actors:
            errors.append(f"{sid}: unknown actor {step['actor']}")
        if step["component"] not in components:
            errors.append(f"{sid}: unknown component {step['component']}")
        for aid in step.get("assumptions", []):
            if aid not in assumptions:
                errors.append(f"{sid}: unknown assumption {aid}")
        mappings = step.get("dpip_mappings", {})
        for value in mappings.get("interactions", []):
            if value not in interactions:
                errors.append(f"{sid}: unknown interaction {value}")
        for value in mappings.get("requirements", []):
            if value not in requirements:
                errors.append(f"{sid}: unknown requirement {value}")
        for value in mappings.get("tests", []):
            if value not in tests:
                errors.append(f"{sid}: unknown test {value}")
        for value in mappings.get("claims", []):
            if value not in claims:
                errors.append(f"{sid}: unknown privacy claim {value}")

        for surface in step.get("privacy_surfaces", []):
            declared = surface.get("declared_scope")
            observable = surface.get("observable_scope")
            effective = surface.get("effective_scope")
            values = [v for v in (declared, observable, effective) if v is not None]
            if len(set(values)) > 1 and not surface.get("effect"):
                errors.append(f"{sid}: diverging scope values require an effect/rationale")

    unresolved = {a["id"] for a in flow.get("assumptions", []) if a["status"] == "unresolved"}
    if unresolved:
        outcomes = flow.get("expected_dpip_outcomes", [])
        if outcomes and all(o["status"] == "PASS" for o in outcomes):
            errors.append("flow has unresolved assumptions but every expected DPIP outcome is PASS")

    return errors


def main() -> int:
    schema = json.loads(SCHEMA.read_text())
    validator = Draft202012Validator(schema)
    files = sorted(FLOW_DIR.glob("rf-*.yaml"))
    if not files:
        print("No reference flows found", file=sys.stderr)
        return 1

    failed = False
    for path in files:
        flow = yaml.safe_load(path.read_text())
        problems = [e.message for e in validator.iter_errors(flow)]
        problems.extend(semantic_errors(flow))
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
