#!/usr/bin/env python3
"""Run DPIP examination execution with causal proposition matching enforced.

This compatibility wrapper keeps the existing examination machinery intact while
requiring a prohibited observed join to have established, proposition-matching
causal attribution before it can become a mechanism-specific FAIL.
"""
from __future__ import annotations

import examination_execute as execution
from causal_attribution import causal_judgment, self_test as causal_self_test

_original_judgment = execution.evidence_ready_judgment


def evidence_ready_judgment(record, setup):
    result = _original_judgment(record, setup)
    if result.get("outcome") != "FAIL" or result.get("reason_code") != "prohibited-correlation-observed":
        return result

    accepted = set(record.get("satisfied_evidence_requirement_ids", []) or [])
    bindings = [
        item for item in setup.get("provided_evidence", []) or []
        if isinstance(item, dict) and str(item.get("requirement_id") or "") in accepted
    ]
    causal_results = [causal_judgment(binding) for binding in bindings]

    # A mechanism-specific FAIL is allowed only when at least one failed binding
    # establishes a cause that explicitly matches the proposition under examination.
    if any(item.get("outcome") == "FAIL" and item.get("terminal_for_proposition") for item in causal_results):
        result.setdefault("details", {})["causal_attribution"] = causal_results
        return result

    result["outcome"] = "INDETERMINATE"
    result["reason_code"] = "causal-attribution-insufficient"
    result["residual_risk"] = (
        "A prohibited cross-context effect was observed, but the supplied evidence does not establish "
        "that the mechanism named by the examined proposition caused that effect."
    )
    result["action_required"] = (
        "Preserve the observed effect and separately assess the evidenced causal mechanism. "
        "Do not attribute the effect to this proposition until a fresh pinned evidence package establishes proposition-matching causality."
    )
    result.setdefault("details", {})["causal_attribution"] = causal_results
    result["details"]["excluded_inference"] = (
        "Observed common values across contexts do not by themselves prove that the examined mechanism independently created the cross-context join."
    )
    return result


execution.evidence_ready_judgment = evidence_ready_judgment

if __name__ == "__main__":
    causal_self_test()
    execution.main()
