#!/usr/bin/env python3
from __future__ import annotations
import json
import sys
from pathlib import Path
import yaml
from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
SCHEMA = json.loads((ROOT / "schema" / "change-impact.schema.json").read_text())
REGISTRY = ROOT / "portfolio" / "change-impact.yaml"


def known_ids() -> tuple[set[str], set[str], set[str], set[str], set[str]]:
    interactions: set[str] = set()
    requirements: set[str] = set()
    tests: set[str] = set()
    claims: set[str] = set()
    flows: set[str] = set()
    for path in (ROOT / "examples").glob("c*-*.yaml"):
        data = yaml.safe_load(path.read_text())
        interactions.add(data["interaction"]["id"])
        requirements.update(x["id"] for x in data.get("requirements", []))
        tests.update(x["id"] for x in data.get("tests", []))
        claims.update(x["id"] for x in data.get("privacy_claims", []))
    for path in (ROOT / "reference-system" / "flows").glob("*.yaml"):
        data = yaml.safe_load(path.read_text())
        flows.add(data["flow"]["id"])
    return interactions, requirements, tests, claims, flows


def main() -> int:
    data = yaml.safe_load(REGISTRY.read_text())
    errors = [e.message for e in Draft202012Validator(SCHEMA).iter_errors(data)]
    known = known_ids()
    categories = ["interactions", "requirements", "tests", "claims", "flows"]
    known_by_category = dict(zip(categories, known))
    seen: set[str] = set()
    for dep in data.get("dependencies", []):
        if dep["id"] in seen:
            errors.append(f"duplicate dependency id {dep['id']}")
        seen.add(dep["id"])
        for category, refs in dep.get("affects", {}).items():
            for ref in refs:
                if ref not in known_by_category[category]:
                    errors.append(f"{dep['id']}: unknown {category[:-1]} {ref}")
        if dep.get("revalidation") == "required" and not any(dep.get("affects", {}).values()):
            errors.append(f"{dep['id']}: required revalidation must identify affected DPIP artifacts")
    if errors:
        print(f"FAIL {REGISTRY.relative_to(ROOT)}")
        for error in errors:
            print(f"  - {error}")
        return 1
    print(f"PASS {REGISTRY.relative_to(ROOT)}")
    print(f"registered dependencies: {len(data.get('dependencies', []))}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
