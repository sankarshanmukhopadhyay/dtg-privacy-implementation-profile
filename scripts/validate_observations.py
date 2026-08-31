#!/usr/bin/env python3
"""Validate DPIP observation fixtures and their semantics against canonical interaction profiles.

Operational contract:
- Checks fixture schema, context/test references, observed-vs-missing state semantics, and self-test pressure cases.
- Observation fixtures are controlled evidence artefacts; validator success does not establish that an upstream runtime produced equivalent observations.
"""
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

    context_ids = [c["id"] for c in fixture.get("contexts", [])]
    if len(context_ids) != len(set(context_ids)):
        errors.append("duplicate context id")
    observation_ids: set[str] = set()
    for obs in fixture.get("observed_surfaces", []):
        oid = obs["id"]
        if oid in observation_ids:
            errors.append(f"duplicate observation id {oid}")
        observation_ids.add(oid)
        if context_ids and obs["context_id"] not in context_ids:
            errors.append(f"{oid}: unknown context {obs['context_id']}")
        if obs["state"] != "observed" and ("value" in obs or "value_digest" in obs):
            errors.append(f"{oid}: non-observed surface must not carry observed value material")

    for join in fixture.get("join_attempts", []):
        missing = [oid for oid in join["input_observation_ids"] if oid not in observation_ids]
        if missing:
            errors.append(f"{join['id']}: unknown input observations {', '.join(missing)}")
        if join["result"] == "joined" and len(join["input_observation_ids"]) < 2:
            errors.append(f"{join['id']}: joined result requires at least two observation inputs")
        if join["result"] == "joined" and not join.get("basis"):
            errors.append(f"{join['id']}: joined result requires basis")
        if join["result"] == "joined" and not join.get("evidence"):
            errors.append(f"{join['id']}: joined result requires evidence")
    return errors


def self_test() -> int:
    profile = {"tests": [{"id": "C3-T4"}]}
    bad = {
        "vectors": [{"id": "v", "test_id": "C3-T4"}],
        "contexts": [{"id": "A", "relationship": "unrelated"}, {"id": "B", "relationship": "unrelated"}],
        "observed_surfaces": [{"id": "o1", "task_id": "EA-X", "context_id": "A", "observer": "v", "component": "c", "surface": "s", "state": "observed", "retention_stage": "retained"}],
        "join_attempts": [{"id": "j", "context_ids": ["A", "B"], "input_observation_ids": ["o1"], "basis": "same stable handle", "result": "joined", "evidence": ["o1"]}],
    }
    problems = semantic_errors(bad, profile)
    assert any("at least two observation inputs" in p for p in problems)
    print("PASS observation semantic self-test")
    return 0


def main() -> int:
    if "--self-test" in sys.argv:
        return self_test()
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
