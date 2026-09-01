#!/usr/bin/env python3
"""Validate external DPIP evidence bindings and immutable provenance requirements.

`evidence/evidence-bindings.yaml` is a semantic evidence-requirement routing registry,
not an external evidence record. It is validated by `validate_evidence_contracts.py`
and is intentionally excluded here so the two contract classes cannot be confused.
"""
from __future__ import annotations
import json
import sys
from pathlib import Path
import yaml
from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
PROFILE_DIR = ROOT / "examples"
EVIDENCE_DIR = ROOT / "evidence"
SCHEMA = ROOT / "schema" / "evidence-binding.schema.json"
MODEL_BINDINGS = "evidence-bindings.yaml"


def load_profile(interaction_id: str) -> dict:
    matches = sorted(PROFILE_DIR.glob(f"{interaction_id.lower()}-*.yaml"))
    if len(matches) != 1:
        raise ValueError(f"expected one profile for {interaction_id}, found {len(matches)}")
    return yaml.safe_load(matches[0].read_text())


def semantic_errors(registry: dict, profile: dict) -> list[str]:
    errors: list[str] = []
    tests = {t["id"] for t in profile.get("tests", [])}
    claims = {c["id"] for c in profile.get("privacy_claims", [])}
    reqs = {r["id"] for r in profile.get("requirements", [])}
    for binding in registry.get("bindings", []):
        bid = binding["id"]
        if binding["maturity"] == "verified" and not binding.get("revision"):
            errors.append(f"{bid}: verified external evidence requires immutable revision")
        if binding["artifact"]["kind"] in {"issue", "pull-request"} and binding["maturity"] == "verified":
            errors.append(f"{bid}: issue/PR locator cannot itself be verified evidence")
        for target in binding.get("supports", []):
            tid = target["target_id"]
            valid = {"test": tests, "privacy-claim": claims, "requirement": reqs}[target["target_type"]]
            if tid not in valid:
                errors.append(f"{bid}: unknown {target['target_type']} target {tid}")
    return errors


def main() -> int:
    schema = json.loads(SCHEMA.read_text())
    validator = Draft202012Validator(schema)
    failed = False
    files = sorted(path for path in EVIDENCE_DIR.glob("*.yaml") if path.name != MODEL_BINDINGS)
    if not files:
        print("No external evidence registries found", file=sys.stderr)
        return 1
    for path in files:
        registry = yaml.safe_load(path.read_text())
        problems = [e.message for e in validator.iter_errors(registry)]
        try:
            profile = load_profile(registry["interaction_id"])
            problems.extend(semantic_errors(registry, profile))
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
