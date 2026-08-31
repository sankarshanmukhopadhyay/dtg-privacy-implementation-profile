#!/usr/bin/env python3
"""Execute controlled ZKP context-commitment cross-context calibration cases.

Operational contract:
- Runs controlled distinct-verifier cases to verify detection of context-reuse/correlation-scope patterns.
- Passing calibration validates the detector against fixtures; it is not evidence that an upstream ZKP implementation behaves the same way in production.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[1]
CASES = ROOT / "supplemental-evidence" / "zkp-context-commitment" / "cases.yaml"


def digest(value: str) -> str:
    return "sha256:" + hashlib.sha256(value.encode("utf-8")).hexdigest()


def execute_case(case: dict[str, Any], common: dict[str, Any]) -> dict[str, Any]:
    contexts = case["contexts"]
    assert len(contexts) == 2
    assert len({c["verifier"] for c in contexts}) == 2, "calibration requires distinct verifier contexts"
    assert all(c["relationship"] == "unrelated" for c in contexts)

    observations = [{
        "context_id": c["id"],
        "verifier": c["verifier"],
        "relationship": c["relationship"],
        "state": "observed",
        "evidence_class": "controlled-executable-fixture",
        "value_digest": digest(c["context_id"]),
        "stability": "zkp-context-commitment",
    } for c in contexts]

    digests = {o["value_digest"] for o in observations}
    result = "joined" if len(digests) == 1 else "not-joined"
    assert result == case["expected_join"]
    disposition = (
        "correlation-scope-widening-pattern-detected"
        if result == "joined"
        else "context-reuse-pattern-not-detected"
    )
    assert disposition == case["expected_disposition"]

    output = {
        "id": case["id"],
        "kind": case["kind"],
        "source": common["source"],
        "semantic_binding": common["semantic_binding"],
        "observations": observations,
        "join": {
            "basis": "same normalized ZKP context commitment digest across unrelated verifier contexts",
            "result": result,
            "evidence": [o["context_id"] for o in observations],
        },
        "calibration_disposition": disposition,
        "judgment_boundary": common["judgment_boundary"],
    }
    if case.get("limitation"):
        output["limitation"] = case["limitation"]
    return output


def execute() -> dict[str, Any]:
    doc = yaml.safe_load(CASES.read_text(encoding="utf-8"))
    return {"zkp_context_calibration": [execute_case(case, doc) for case in doc["cases"]]}


def self_test() -> None:
    results = execute()["zkp_context_calibration"]
    by_id = {row["id"]: row for row in results}
    neg = by_id["ZKP-CTX-NEG-001"]
    pos = by_id["ZKP-CTX-POS-001"]
    assert neg["join"]["result"] == "joined"
    assert neg["calibration_disposition"] == "correlation-scope-widening-pattern-detected"
    assert pos["join"]["result"] == "not-joined"
    assert pos["calibration_disposition"] == "context-reuse-pattern-not-detected"
    assert "does not establish global" in pos["limitation"]
    for row in results:
        assert row["semantic_binding"]["surface"] == "zkp-context-commitment"
        assert row["judgment_boundary"]["deployment_privacy_judgment"] == "not-made"
        assert row["judgment_boundary"]["runtime_gap_replaced"] is False
        assert row["judgment_boundary"]["source_pin_replacement"] is False
    rendered = json.dumps(results)
    for raw in ("zkp-controlled-context-reuse-001", "zkp-controlled-context-a", "zkp-controlled-context-b"):
        assert raw not in rendered


def main() -> int:
    self_test()
    print(yaml.safe_dump(execute(), sort_keys=False).rstrip())
    print("PASS ZKP context commitment calibration")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
