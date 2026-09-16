#!/usr/bin/env python3
"""Validate and summarize DPIP evidence obligations.

DPIP owns privacy evidence sufficiency. This module does not acquire evidence, infer
operator-only facts, or convert privacy findings into broader harm/assurance judgments.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

SCHEMA = "dpip-evidence-obligation/v1"
SUPPLIERS = {"TARGET_MAINTAINER","TARGET_OPERATOR","INDEPENDENT_ASSESSOR","INTEROP_LAB","GOVERNANCE_AUTHORITY","DATA_CONTROLLER","THIRD_PARTY_PROCESSOR","UNKNOWN"}
SOURCE_CLASSES = {"DECLARATIVE","STATIC_IMPLEMENTATION","BLACK_BOX_RUNTIME","WHITE_BOX_RUNTIME","GOVERNANCE","DEPLOYMENT","LONGITUDINAL"}
BLOCKERS = {"NONE","NO_TARGET","NO_OBSERVATION_SURFACE","OPERATOR_ACCESS_REQUIRED","GOVERNANCE_AUTHORITY_REQUIRED","SENSITIVE_EVIDENCE","NO_INSTRUMENTATION","NON_REPRODUCIBLE","VERSION_UNBOUND","COST_DISPROPORTIONATE","AUTHORITY_UNCLEAR"}
STATES = {"IDENTIFIED","QUALIFIED","EXPERIMENT_DESIGNED","EVIDENCE_ACQUIRED","REEVALUATED","SATISFIED","FALSIFIED","INDETERMINATE","ACCEPTED_RESIDUAL_RISK","SUPERSEDED","BLOCKED"}
MATURITIES = {f"E{i}" for i in range(6)}
RUNTIME_MATURITY = {"E3","E4","E5"}
TERMINAL = {"SATISFIED","FALSIFIED","INDETERMINATE","ACCEPTED_RESIDUAL_RISK","SUPERSEDED","BLOCKED"}


def require(ok: bool, msg: str) -> None:
    if not ok:
        raise ValueError(msg)


def validate(ob: dict[str, Any]) -> None:
    require(ob.get("schema") == SCHEMA, f"schema must be {SCHEMA}")
    oid = ob.get("id")
    require(isinstance(oid, str) and oid.startswith("DPIP-EG-") and len(oid.split("-")) == 4, "invalid obligation id")
    source = ob.get("source")
    require(isinstance(source, dict) and isinstance(source.get("dpip_issue"), int), "source.dpip_issue is required")
    prop = ob.get("proposition")
    require(isinstance(prop, dict) and isinstance(prop.get("statement"), str) and prop["statement"].strip(), "proposition.statement is required")
    require(isinstance(prop.get("privacy_dimensions"), list) and prop["privacy_dimensions"], "privacy_dimensions are required")
    require(ob.get("materiality") in {"material","non-material"}, "invalid materiality")
    observer = ob.get("observer")
    require(isinstance(observer, dict) and observer.get("role") and observer.get("vantage_point"), "observer role and vantage_point are required")
    supplier = ob.get("supplier")
    require(isinstance(supplier, dict) and supplier.get("role") in SUPPLIERS, "invalid supplier role")
    require(supplier.get("evidence_source_class") in SOURCE_CLASSES, "invalid evidence source class")
    required = ob.get("required_observations")
    require(isinstance(required, list) and required and all(isinstance(x, str) and x.strip() for x in required), "required_observations must be non-empty")
    falsification = ob.get("falsification")
    require(isinstance(falsification, dict) and falsification.get("condition"), "falsification.condition is required")
    maturity = ob.get("evidence_maturity", {}).get("minimum_required")
    require(maturity in MATURITIES, "invalid evidence maturity")
    access = ob.get("access")
    require(isinstance(access, dict) and access.get("status") in {"AVAILABLE","BLOCKED","PARTIAL"}, "invalid access status")
    blocker = access.get("blocker")
    require(blocker in BLOCKERS, "invalid blocker")
    if access["status"] == "AVAILABLE":
        require(blocker == "NONE", "available evidence cannot carry a blocker")
    if access["status"] == "BLOCKED":
        require(blocker != "NONE", "blocked evidence requires a blocker")
    target = ob.get("target")
    if maturity in RUNTIME_MATURITY and blocker != "NO_TARGET":
        require(isinstance(target, dict) and target.get("repository") and target.get("revision"), "E3+ evidence requires repository and immutable revision")
    if blocker == "NO_TARGET":
        require(not target or not target.get("revision"), "NO_TARGET cannot carry a bound target revision")
    state = ob.get("state")
    require(state in STATES, "invalid obligation state")
    if state == "ACCEPTED_RESIDUAL_RISK":
        acceptance = ob.get("residual_risk_acceptance")
        require(isinstance(acceptance, dict) and acceptance.get("authority") and acceptance.get("scope"), "residual risk acceptance requires authority and scope")
    require(isinstance(ob.get("downstream_consumer"), str) and ob["downstream_consumer"], "downstream_consumer is required")


def can_interop_acquire(ob: dict[str, Any]) -> tuple[bool, str]:
    validate(ob)
    source_class = ob["supplier"]["evidence_source_class"]
    blocker = ob["access"]["blocker"]
    if blocker != "NONE":
        return False, blocker
    if source_class in {"STATIC_IMPLEMENTATION","BLACK_BOX_RUNTIME"}:
        return True, "ADMISSIBLE"
    if source_class == "WHITE_BOX_RUNTIME" and ob["supplier"]["role"] == "INTEROP_LAB":
        return True, "ADMISSIBLE"
    return False, "SUPPLIER_OR_AUTHORITY_REQUIRED"


def assurability(ob: dict[str, Any]) -> str:
    validate(ob)
    if ob["access"]["blocker"] in {"NO_OBSERVATION_SURFACE","NO_INSTRUMENTATION","NON_REPRODUCIBLE"}:
        return "ASSURABILITY_GAP"
    if ob["access"]["status"] == "BLOCKED":
        return "EVIDENCE_BLOCKED"
    return "EVIDENTIABLE"


def summarize(items: list[dict[str, Any]]) -> dict[str, Any]:
    ids: set[str] = set()
    rows = []
    for ob in items:
        validate(ob)
        require(ob["id"] not in ids, f"duplicate obligation id: {ob['id']}")
        ids.add(ob["id"])
        admissible, reason = can_interop_acquire(ob)
        rows.append({"id": ob["id"], "state": ob["state"], "blocker": ob["access"]["blocker"], "assurability": assurability(ob), "interop_admissible": admissible, "interop_reason": reason})
    return {"schema": "dpip-evidence-obligation-register/v1", "count": len(rows), "terminal_count": sum(r["state"] in TERMINAL for r in rows), "obligations": rows}


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--input", required=True, type=Path)
    p.add_argument("--output", type=Path)
    p.add_argument("--check", action="store_true")
    args = p.parse_args()
    doc = json.loads(args.input.read_text(encoding="utf-8"))
    items = doc if isinstance(doc, list) else doc.get("obligations")
    require(isinstance(items, list) and items, "input must contain obligations")
    result = summarize(items)
    text = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.write_text(text, encoding="utf-8")
    else:
        print(text, end="")
    if args.check:
        print(f"PASS: {result['count']} evidence obligations are valid and bounded")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
