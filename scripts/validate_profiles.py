#!/usr/bin/env python3
"""Validate DPIP YAML profiles against the JSON Schema and traceability rules."""
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
    req_ids = {r["id"] for r in profile.get("requirements", [])}
    claim_ids = {c["id"] for c in profile.get("privacy_claims", [])}
    test_req_ids = set()
    for test in profile.get("tests", []):
        for rid in test.get("requirements", []):
            test_req_ids.add(rid)
            if rid not in req_ids:
                errors.append(f"{test['id']}: unknown requirement {rid}")
        for cid in test.get("claims", []):
            if cid not in claim_ids:
                errors.append(f"{test['id']}: unknown privacy claim {cid}")
    for rid in sorted(req_ids - test_req_ids):
        errors.append(f"requirement {rid} has no test coverage")
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
