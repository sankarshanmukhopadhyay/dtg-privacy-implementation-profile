#!/usr/bin/env python3
"""Execute controlled Trust Tasks threadId cross-exchange calibration cases."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[1]
CASES = ROOT / "supplemental-evidence" / "trust-tasks-threadid" / "cases.yaml"


def digest(value: str) -> str:
    return "sha256:" + hashlib.sha256(value.encode("utf-8")).hexdigest()


def execute_case(case: dict[str, Any], common: dict[str, Any]) -> dict[str, Any]:
    contexts = case["contexts"]
    assert len(contexts) == 2
    assert len({c["exchange"] for c in contexts}) == 2, "calibration contexts must be separate exchanges"
    assert all(c["relationship"] == "unrelated" for c in contexts)

    observations = [{
        "context_id": c["id"],
        "exchange": c["exchange"],
        "relationship": c["relationship"],
        "state": "observed",
        "evidence_class": "controlled-executable-fixture",
        "value_digest": digest(c["thread_id"]),
        "stability": "exchange-correlation-identifier",
    } for c in contexts]

    digests = {o["value_digest"] for o in observations}
    result = "joined" if len(digests) == 1 else "not-joined"
    assert result == case["expected_join"]
    disposition = "falsification-pattern-detected" if result == "joined" else "prohibited-reuse-pattern-not-detected"
    assert disposition == case["expected_disposition"]

    output = {
        "id": case["id"],
        "kind": case["kind"],
        "source": common["source"],
        "semantic_binding": common["semantic_binding"],
        "observations": observations,
        "join": {
            "basis": "same normalized threadId digest across separate unrelated exchanges",
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
    results = [execute_case(case, doc) for case in doc["cases"]]
    return {"trust_tasks_threadid_calibration": results}


def self_test() -> None:
    result = execute()["trust_tasks_threadid_calibration"]
    by_id = {row["id"]: row for row in result}
    neg = by_id["TT-THREAD-NEG-001"]
    pos = by_id["TT-THREAD-POS-001"]
    assert neg["join"]["result"] == "joined"
    assert neg["calibration_disposition"] == "falsification-pattern-detected"
    assert pos["join"]["result"] == "not-joined"
    assert pos["calibration_disposition"] == "prohibited-reuse-pattern-not-detected"
    assert "does not establish global" in pos["limitation"]
    for row in result:
        assert row["semantic_binding"]["surface"] == "trust-task-envelope"
        assert row["judgment_boundary"]["deployment_privacy_judgment"] == "not-made"
        assert row["judgment_boundary"]["runtime_gap_replaced"] is False
    rendered = json.dumps(result)
    for raw in ("tt-controlled-reuse-001", "tt-controlled-fresh-a", "tt-controlled-fresh-b"):
        assert raw not in rendered


def main() -> int:
    self_test()
    print(yaml.safe_dump(execute(), sort_keys=False).rstrip())
    print("PASS Trust Tasks threadId calibration")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
