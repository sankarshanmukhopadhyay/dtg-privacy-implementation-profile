#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = ROOT / "contracts/privacy-observability-result-v1.schema.json"


def validate_result(doc: dict[str, Any]) -> list[str]:
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    validator = Draft202012Validator(schema)
    errors = [f"schema: {e.message}" for e in sorted(validator.iter_errors(doc), key=lambda e: list(e.path))]
    if errors:
        return errors

    if not doc["executed"] and doc["result"] != "evidence-incomplete":
        errors.append("unexecuted experiment must return evidence-incomplete")

    correlation = doc["correlation"]
    if (correlation["signal"] == "found" or correlation["effective_join"]) and doc["result"] == "supported":
        errors.append("observed correlation/effective join cannot support the privacy proposition")

    if "deployment-wide unlinkability" not in doc["unsupported_inference"]:
        errors.append("bounded observation must explicitly exclude deployment-wide unlinkability")

    outside = [p for p in doc["observer_planes"] if p["threat_model"] == "outside"]
    if doc["result"] == "outside-threat-model" and not outside:
        errors.append("outside-threat-model result requires an explicitly outside observer plane")

    return errors


def main() -> int:
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("path", nargs="?")
    args = parser.parse_args()
    if not args.path:
        print("privacy observability contract validator ready")
        return 0
    doc = json.loads(Path(args.path).read_text(encoding="utf-8"))
    errors = validate_result(doc)
    if errors:
        for error in errors:
            print(error)
        return 1
    print("privacy observability result valid")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
