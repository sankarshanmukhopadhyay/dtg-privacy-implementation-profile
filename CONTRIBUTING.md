# Contributing

Substantive changes should preserve a visible Issue → PR → tests/evidence → merge judgment trail.

1. State the privacy proposition/model gap, affected authority boundary, compatibility/assurance impact, and acceptance criteria in an issue.
2. Implement the smallest coherent change on a branch.
3. Add or update deterministic positive, negative, adversarial, provenance, and boundary evidence where applicable.
4. In the PR, record implementation choice, validation, residual uncertainty, and any evidence invalidation/reassessment consequence.
5. Merge only after the repository's applicable validation gate passes.

DPIP owns composed privacy assurance semantics only. Contributions must not silently acquire authority over component semantics or deployment/governance decisions.

Missing or inadmissible evidence is never PASS. Preserve `INDETERMINATE / evidence-required` and `INDETERMINATE / model-gap` semantics where evidence or model coverage is insufficient.

## Durable artifact placement

Before adding a durable file, identify its repository role: **profile authority, executable contract, executable implementation, evidence, assurance judgment, historical record, or canonical reader documentation**. Evidence registries, observations, fixtures, evidence plans and machine-readable bindings are not disposable documentation merely because they are text or YAML.

Prefer stable requirement IDs such as `ER-*`, case IDs and links to canonical artifacts over repeating cross-repository coordination prose. Add a new explanatory document only when an existing canonical page cannot own the material without obscuring its purpose. Temporary reasoning, status narration and coordination should normally remain in the Issue/PR record.

Security reports must follow [`SECURITY.md`](SECURITY.md).
