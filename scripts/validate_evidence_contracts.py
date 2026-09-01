#!/usr/bin/env python3
from __future__ import annotations
import pathlib
import yaml

ROOT = pathlib.Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "portfolio" / "evidence-requirements.yaml"
BINDINGS = ROOT / "evidence" / "evidence-bindings.yaml"


def load(path):
    with path.open(encoding="utf-8") as f:
        value = yaml.safe_load(f)
    if not isinstance(value, dict):
        raise SystemExit(f"{path}: expected mapping")
    return value


def main() -> int:
    registry = load(REGISTRY)
    bindings = load(BINDINGS)
    requirements = registry.get("requirements") or {}
    if not isinstance(requirements, dict):
        raise SystemExit("authoritative evidence requirements must be a mapping")
    required = {"ER-REL-DID-AB", "ER-STATUS-AB", "ER-TASK-AB", "ER-VERIFIER-AB", "ER-CREDENTIAL-ID-AB", "ER-DEVICE-METADATA-AB"}
    if not required.issubset(set(requirements)):
        raise SystemExit(f"required evidence contracts missing: {sorted(required - set(requirements))}")
    for rid, item in requirements.items():
        if not isinstance(item, dict):
            raise SystemExit(f"{rid}: requirement must be a mapping")
        if not item.get("accepted_evidence_classes"):
            raise SystemExit(f"{rid}: no accepted evidence class")
        if not item.get("required_surfaces"):
            raise SystemExit(f"{rid}: no required surfaces")
        if item.get("source_pin_policy") != "immutable-component-pins-required":
            raise SystemExit(f"{rid}: source pin policy not explicit")
        if not item.get("producer_capability"):
            raise SystemExit(f"{rid}: no producer capability")
    known = set(requirements)
    for binding in bindings.get("bindings", []) or []:
        unknown = set(binding.get("evidence_requirement_ids", [])) - known
        if unknown:
            raise SystemExit(f"{binding.get('id')}: unknown evidence requirements {sorted(unknown)}")
    rel = next(b for b in bindings["bindings"] if b["id"] == "relationship-correlation-privacy")
    if rel["evidence_requirement_ids"] != ["ER-REL-DID-AB", "ER-STATUS-AB", "ER-TASK-AB", "ER-VERIFIER-AB"]:
        raise SystemExit("relationship evidence binding regression")
    cred = next(b for b in bindings["bindings"] if b["id"] == "credential-identifier-cross-context-correlation")
    if cred["evidence_requirement_ids"] != ["ER-CREDENTIAL-ID-AB"]:
        raise SystemExit("credential evidence binding regression")
    print("PASS authoritative DPIP evidence registry and semantic bindings")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
