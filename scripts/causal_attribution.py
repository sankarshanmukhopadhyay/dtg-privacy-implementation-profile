#!/usr/bin/env python3
"""Generic causal-attribution gate for mechanism-specific DPIP judgments.

A prohibited observation is not, by itself, evidence that the mechanism named by
an examined proposition caused it.  This module keeps observation, boundary
crossing, causal attribution, proposition matching and judgment separate.
"""
from __future__ import annotations

from typing import Any


def attribution_for(binding: dict[str, Any]) -> dict[str, Any]:
    value = binding.get("causal_attribution")
    return value if isinstance(value, dict) else {}


def causal_judgment(binding: dict[str, Any]) -> dict[str, Any]:
    """Interpret a producer binding without promoting effect into cause.

    Returns a small machine-readable decision used by the examination layer.
    `terminal_for_proposition` is true only when the causal mechanism is
    established and explicitly matches the proposition under examination.
    """
    experiment = binding.get("experiment") if isinstance(binding.get("experiment"), dict) else {}
    observed = str(experiment.get("observed_join") or "").strip()
    expected = str(experiment.get("expected_join") or "").strip()
    attribution = attribution_for(binding)

    effect_observed = observed in {"detected", "emerged"}
    status = str(attribution.get("status") or "").strip()
    mechanism = str(attribution.get("mechanism") or "").strip()
    surface = str(attribution.get("responsible_surface") or "").strip()
    proposition_match = attribution.get("proposition_match") is True
    established = status == "established" and bool(mechanism) and bool(surface)

    if expected == "must-not-emerge" and effect_observed:
        if established and proposition_match:
            return {
                "outcome": "FAIL",
                "reason_code": "prohibited-correlation-observed",
                "terminal_for_proposition": True,
                "effect_observed": True,
                "causal_attribution": attribution,
                "excluded_inference": None,
            }
        return {
            "outcome": "INDETERMINATE",
            "reason_code": "causal-attribution-insufficient",
            "terminal_for_proposition": False,
            "effect_observed": True,
            "causal_attribution": attribution or {"status": "not-established"},
            "excluded_inference": "Observed cross-context common value must not be attributed to the examined mechanism without proposition-matching causal evidence.",
        }

    if expected == "must-not-emerge" and observed == "not-detected":
        return {
            "outcome": "PASS",
            "reason_code": "evidence-supported-no-prohibited-correlation",
            "terminal_for_proposition": True,
            "effect_observed": False,
            "causal_attribution": attribution,
            "excluded_inference": None,
        }

    return {
        "outcome": "INDETERMINATE",
        "reason_code": "evidence-not-interpretable",
        "terminal_for_proposition": False,
        "effect_observed": effect_observed,
        "causal_attribution": attribution,
        "excluded_inference": None,
    }


def self_test() -> None:
    base = {"experiment": {"expected_join": "must-not-emerge", "observed_join": "detected"}}

    # Effect observed but no cause established: never mechanism-specific FAIL.
    assert causal_judgment(base)["outcome"] == "INDETERMINATE"

    # Real boundary failure caused by a different mechanism: still not a FAIL
    # against the proposition being examined.
    scope_leak = {
        **base,
        "causal_attribution": {
            "status": "established",
            "mechanism": "authorization-scope-bypass",
            "responsible_surface": "enumeration-api",
            "proposition_match": False,
        },
    }
    result = causal_judgment(scope_leak)
    assert result["outcome"] == "INDETERMINATE"
    assert result["reason_code"] == "causal-attribution-insufficient"

    # Same effect, mechanism proven to be the proposition's mechanism: FAIL.
    matched = {
        **base,
        "causal_attribution": {
            "status": "established",
            "mechanism": "cross-context-metadata-egress",
            "responsible_surface": "runtime-transport",
            "proposition_match": True,
        },
    }
    assert causal_judgment(matched)["outcome"] == "FAIL"

    # Valid no-join experiment remains PASS for the scoped proposition.
    no_join = {"experiment": {"expected_join": "must-not-emerge", "observed_join": "not-detected"}}
    assert causal_judgment(no_join)["outcome"] == "PASS"


if __name__ == "__main__":
    self_test()
    print("causal-attribution self-test: PASS")
