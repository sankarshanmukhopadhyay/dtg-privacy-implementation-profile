# Contributing

Substantive changes should preserve a visible Issue → PR → tests/evidence → merge judgment trail.

1. State the privacy proposition/model gap, affected authority boundary, compatibility/assurance impact, and acceptance criteria in an issue.
2. Implement the smallest coherent change on a branch.
3. Add or update deterministic positive, negative, adversarial, provenance, and boundary evidence where applicable.
4. In the PR, record implementation choice, validation, residual uncertainty, and any evidence invalidation/reassessment consequence.
5. Merge only after the repository's applicable validation gate passes.

DPIP owns composed privacy assurance semantics only. Contributions must not silently acquire authority over component semantics or deployment/governance decisions.

Missing or inadmissible evidence is never PASS. Preserve `INDETERMINATE / evidence-required` and `INDETERMINATE / model-gap` semantics where evidence or model coverage is insufficient.

Security reports must follow [`SECURITY.md`](SECURITY.md).
