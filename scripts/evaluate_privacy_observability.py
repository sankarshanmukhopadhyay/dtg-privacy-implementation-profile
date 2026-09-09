#!/usr/bin/env python3
"""Interpret a DPIP privacy-observability result and emit a portable RAHP assessor result."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
OBS_SCHEMA = ROOT / "contracts" / "privacy-observability-result-v1.schema.json"
ASSESSOR_SCHEMA = ROOT / "contracts" / "rahp-assessor-result-v1.schema.json"


def _validate(doc: dict[str, Any], schema_path: Path) -> list[str]:
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    return [
        f"{'.'.join(str(x) for x in exc.absolute_path) or '$'}: {exc.message}"
        for exc in Draft202012Validator(schema).iter_errors(doc)
    ]


def to_assessor_result(doc: dict[str, Any]) -> dict[str, Any]:
    problems = _validate(doc, OBS_SCHEMA)
    if problems:
        raise ValueError("invalid privacy observability result: " + "; ".join(problems))

    result = doc["result"]
    correlation = doc["correlation"]
    unsupported = list(doc.get("unsupported_inference") or [])
    residual = list(doc.get("residual_uncertainty") or [])
    experiment_id = str(doc["experiment"]["id"])

    if result == "supported":
        outcome = "PASS"
        reason_code = "bounded-privacy-supported"
        action = "RAHP may reconcile this specialist PASS only within the DPIP claim boundary; do not promote it to deployment-wide unlinkability or terminal assurance PASS."
    elif result == "not-supported":
        outcome = "FAIL"
        reason_code = "observed-correlation" if correlation.get("signal") == "found" or correlation.get("effective_join") else "privacy-proposition-not-supported"
        action = "Treat the bounded privacy proposition as not met and investigate the observed join/correlation before rerun."
    elif result in {"evidence-incomplete", "indeterminate"}:
        outcome = "INDETERMINATE"
        reason_code = "evidence-incomplete" if result == "evidence-incomplete" else "privacy-indeterminate"
        action = "Acquire the missing observer/runtime evidence and rerun; do not infer PASS from absence of evidence."
    elif result == "outside-threat-model":
        outcome = "NOT_APPLICABLE"
        reason_code = "outside-threat-model"
        action = "Do not extend this DPIP privacy conclusion to the explicitly out-of-scope observer; use a separate assessment if that observer becomes in scope."
    else:
        outcome = "INDETERMINATE"
        reason_code = "unsupported-privacy-result"
        action = "Update the specialist mapping before reconciliation; do not infer PASS."

    observer_ids = [plane["id"] for plane in doc["observer_planes"]]
    evidence_used = [
        f"{doc['schema']}:{experiment_id}:result={result}",
        "observer-planes:" + ",".join(observer_ids),
        f"correlation:{correlation.get('signal')}|effective_join={str(bool(correlation.get('effective_join'))).lower()}",
    ]
    residual_parts = residual + [f"Unsupported inference: {item}" for item in unsupported]
    residual_risk = "; ".join(residual_parts) or "No residual uncertainty supplied; RAHP must retain the bounded specialist scope."

    assessor = {
        "schema": "rahp-assessor-result/v1",
        "assessor": "DPIP privacy observability",
        "assessment_id": f"dpip-privacy-observability:{experiment_id}",
        "outcome": outcome,
        "reason_code": reason_code,
        "evidence_used": evidence_used,
        "residual_risk": residual_risk,
        "action_required": action,
        "details": {
            "privacy_observability_schema": doc["schema"],
            "privacy_result": result,
            "executed": doc["executed"],
            "observer_planes": observer_ids,
            "correlation": correlation,
            "unsupported_inference": unsupported,
            "ownership_boundary": "DPIP owns privacy interpretation for the declared experiment/observer scope; RAHP owns terminal assurance reconciliation."
        }
    }
    assessor_problems = _validate(assessor, ASSESSOR_SCHEMA)
    if assessor_problems:
        raise ValueError("invalid RAHP assessor result: " + "; ".join(assessor_problems))
    return assessor


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    doc = json.loads(args.input.read_text(encoding="utf-8"))
    result = to_assessor_result(doc)
    rendered = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8")
    else:
        print(rendered, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
