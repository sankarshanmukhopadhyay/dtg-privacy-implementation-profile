#!/usr/bin/env python3
from __future__ import annotations
import pathlib, sys, yaml

ROOT = pathlib.Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "evidence" / "evidence-requirements.yaml"
BINDINGS = ROOT / "evidence" / "evidence-bindings.yaml"

def load(path):
    with path.open(encoding="utf-8") as f:
        return yaml.safe_load(f)

def main():
    registry = load(REGISTRY)
    bindings = load(BINDINGS)
    ids = [r["id"] for r in registry["requirements"]]
    if len(ids) != len(set(ids)):
        raise SystemExit("duplicate evidence requirement id")
    required = {"ER-REL-DID-AB","ER-STATUS-AB","ER-TASK-AB","ER-VERIFIER-AB","ER-CREDENTIAL-ID-AB"}
    if not required.issubset(set(ids)):
        raise SystemExit("required model-gap contracts missing")
    for item in registry["requirements"]:
        if not item.get("accepted_evidence_classes"):
            raise SystemExit(f"{item['id']}: no accepted evidence class")
        if not item.get("required_surfaces"):
            raise SystemExit(f"{item['id']}: no required surfaces")
        if item.get("source_pin_policy") != "immutable-component-pins-required":
            raise SystemExit(f"{item['id']}: source pin policy not explicit")
        if not item.get("producer_capability"):
            raise SystemExit(f"{item['id']}: no producer capability")
    known=set(ids)
    for b in bindings["bindings"]:
        unknown=set(b["evidence_requirement_ids"])-known
        if unknown:
            raise SystemExit(f"{b['id']}: unknown evidence requirement ids {sorted(unknown)}")
    rel=next(b for b in bindings["bindings"] if b["id"]=="relationship-correlation-privacy")
    if rel["evidence_requirement_ids"] != ["ER-REL-DID-AB","ER-STATUS-AB","ER-TASK-AB","ER-VERIFIER-AB"]:
        raise SystemExit("relationship binding regression")
    print("PASS evidence requirement registry and bindings")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
