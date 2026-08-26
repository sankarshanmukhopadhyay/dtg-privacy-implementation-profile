#!/usr/bin/env python3
from __future__ import annotations
import json
import sys
from pathlib import Path
import yaml
from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
PROFILE_DIR = ROOT / "examples"
OBSERVATION_DIR = ROOT / "observations"
SCHEMA = ROOT / "schema" / "observation-fixture.schema.json"


def load_profile(interaction_id: str) -> dict:
    matches = sorted(PROFILE_DIR.glob(f"{interaction_id.lower()}-*.yaml"))
    if len(matches) != 1:
        raise ValueError(f"expected one profile for {interaction_id}, found {len(matches)}")
    return yaml.safe_load(matches[0].read_text())


def semantic_errors(fixture: dict, profile: dict) -> list[str]:
    errors: list[str] = []
    tests = {t["id"] for t in profile.get("tests", [])}
    seen_vectors: set[str] = set()
    for vector in fixture.get("vectors", []):
        vid = vector["id"]
        if vid in seen_vectors:
            errors.append(f"duplicate vector id {vid}")
        seen_vectors.add(vid)
        if vector["test_id"] not in tests:
            errors.append(f"{vid}: unknown test {vector['test_id']}")
    return errors


def main() -> int:
    schema = json.loads(SCHEMA.read_text())
    validator = Draft202012Validator(schema)
    failed = False
    files = sorted(OBSERVATION_DIR.glob("*.yaml"))
    if not files:
        print("No executable observation fixtures found", file=sys.stderr)
        return 1

    for path in files:
        fixture = yaml.safe_load(path.read_text())
        problems = [e.message for e in validator.iter_errors(fixture)]
        try:
            profile = load_profile(fixture["interaction_id"])
            problems.extend(semantic_errors(fixture, profile))
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
