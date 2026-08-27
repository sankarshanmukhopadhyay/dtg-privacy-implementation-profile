#!/usr/bin/env python3
"""Validate and execute supplemental DPIP executable-evidence calibration bindings."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[1]
CASE = ROOT / "supplemental-evidence" / "zkp-int-005"


def digest_value(value: str) -> str:
    return "sha256:" + hashlib.sha256(value.encode("utf-8")).hexdigest()


def execute(case_dir: Path = CASE) -> dict[str, Any]:
    fixture = json.loads((case_dir / "fixture.json").read_text(encoding="utf-8"))
    binding = yaml.safe_load((case_dir / "binding.yaml").read_text(encoding="utf-8"))

    assert fixture["fixture_id"] == binding["source"]["fixture_id"]
    assert fixture["expected"] == binding["expected"]["source_fixture_disposition"]
    assert fixture["reason"] == "stable-cross-context-handle"
    assert len(fixture["contexts"]) == 2

    mapped = {row["source_context"]: row for row in binding["contexts"]}
    assert set(mapped) == set(fixture["contexts"])
    assert all(row["relationship"] == "unrelated" for row in mapped.values())

    value_digest = digest_value(fixture["shared_handle"])
    observations = []
    for source_context in fixture["contexts"]:
        row = mapped[source_context]
        observations.append({
            "context_id": row["normalized_context"],
            "source_context": source_context,
            "relationship": row["relationship"],
            "state": "observed",
            "evidence_class": "executable-fixture",
            "value_digest": value_digest,
            "stability": "stable-cross-context",
        })

    digests = {row["value_digest"] for row in observations}
    join_result = "joined" if len(observations) >= 2 and len(digests) == 1 else "not-joined"
    assert join_result == binding["expected"]["join_result"]

    result = {
        "supplemental_evidence_result": {
            "id": binding["id"],
            "kind": binding["kind"],
            "source": binding["source"],
            "semantic_binding": binding["semantic_binding"],
            "observations": observations,
            "join": {
                "basis": "same normalized durable correlation value across unrelated contexts",
                "result": join_result,
                "evidence": [row["context_id"] for row in observations],
            },
            "calibration_disposition": (
                "falsification-pattern-detected" if join_result == "joined" else "pattern-not-detected"
            ),
            "judgment_boundary": binding["judgment_boundary"],
        }
    }
    return result


def self_test() -> None:
    result = execute()["supplemental_evidence_result"]
    assert result["join"]["result"] == "joined"
    assert result["calibration_disposition"] == "falsification-pattern-detected"
    assert result["semantic_binding"]["test"] == "C3-T4"
    assert result["semantic_binding"]["external_test"] == "CP-PRIV-005"
    assert result["judgment_boundary"]["specific_surface_attribution"] == "not-made"
    assert result["judgment_boundary"]["deployment_privacy_judgment"] == "not-made"
    assert result["judgment_boundary"]["source_pin_replacement"] is False
    assert all(row["evidence_class"] == "executable-fixture" for row in result["observations"])
    assert all("link-constant-001" not in json.dumps(row) for row in result["observations"])


def main() -> int:
    self_test()
    result = execute()
    print(yaml.safe_dump(result, sort_keys=False).rstrip())
    print("PASS supplemental executable evidence calibration")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
