#!/usr/bin/env python3
"""Validate DPIP conformance-result fixtures and reject scoped claim overreach.

Operational contract:
- Checks result schema, canonical interaction/test/claim references, version alignment, and status ceilings.
- A validated result is internally consistent with DPIP semantics; this script does not generate new runtime evidence or upgrade a result to PASS.
"""
from __future__ import annotations
import json
import sys
from pathlib import Path

import yaml
from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
PROFILE_DIR = ROOT / "examples"
RESULT_DIR = ROOT / "results"
RESULT_SCHEMA = ROOT / "schema" / "conformance-result.schema.json"

STATUS_ORDER = {"FAIL": 0, "INDETERMINATE": 1, "CONSTRAINED": 2, "PASS": 3}


def load_profile(interaction_id: str) -> dict:
    matches = sorted(PROFILE_DIR.glob(f"{interaction_id.lower()}-*.yaml"))
    if len(matches) != 1:
        raise ValueError(f"expected one profile for {interaction_id}, found {len(matches)}")
    return yaml.safe_load(matches[0].read_text())


def semantic_errors(result: dict, profile: dict) -> list[str]:
    errors: list[str] = []
    if result["interaction_version"] != profile["interaction"]["version"]:
        errors.append("interaction version does not match canonical profile")

    tests = {t["id"] for t in profile.get("tests", [])}
    claims = {c["id"]: c for c in profile.get("privacy_claims", [])}

    for item in result.get("test_results", []):
        if item["test_id"] not in tests:
            errors.append(f"unknown test {item['test_id']}")

    for item in result.get("claim_results", []):
        cid = item["claim_id"]
        if cid not in claims:
            errors.append(f"unknown privacy claim {cid}")
            continue
        expected = claims[cid]["expected_status"]
        actual = item["status"]
        if STATUS_ORDER[actual] > STATUS_ORDER[expected]:
            errors.append(
                f"{cid}: result {actual} overstates canonical baseline {expected}"
            )

    result_claims = {c["claim_id"] for c in result.get("claim_results", [])}
    for cid in sorted(set(claims) - result_claims):
        errors.append(f"missing privacy claim result {cid}")

    return errors


def main() -> int:
    schema = json.loads(RESULT_SCHEMA.read_text())
    validator = Draft202012Validator(schema)
    failed = False
    files = sorted(RESULT_DIR.glob("*.yaml"))
    if not files:
        print("No conformance results found", file=sys.stderr)
        return 1

    for path in files:
        result = yaml.safe_load(path.read_text())
        problems = [e.message for e in validator.iter_errors(result)]
        try:
            profile = load_profile(result["interaction_id"])
            problems.extend(semantic_errors(result, profile))
        except (KeyError, ValueError) as exc:
            problems.append(str(exc))

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
