# Evidence-directed INDETERMINATE

DPIP treats `INDETERMINATE` as a valid assurance disposition. It is not a weak PASS, a deferred FAIL, or a generic request for more information.

When an examination is evidence-incomplete, the disposition SHOULD identify the smallest evidence package capable of changing the result. The generated remediation plan records the proposition, evidence class, producer, context boundary, minimum fields, privacy-safe capture rule, sufficiency criterion, rerun target, priority, and routing target.

## Evidence boundary

Two evidence classes must remain distinct:

1. **DPIP-local executable evidence** demonstrates that DPIP can mechanically detect or falsify a defined condition using repository fixtures.
2. **Upstream/runtime evidence** demonstrates what a pinned implementation or deployment actually exposed or retained in the examined interaction.

A synthetic DPIP fixture MUST NOT be represented as evidence that an upstream implementation exhibits the fixture's behaviour. Conversely, specification text describing intended privacy properties MUST NOT be converted into a runtime privacy PASS.

## Privacy-safe evidence acquisition

Evidence demands should be minimized to what the proposition requires. When equality, derivability, retention, or joinability can be tested with normalized or hashed values, the remediation plan should prefer those forms over unnecessarily identifying telemetry.

## Rerun semantics

A completed examination remains immutable as historical assurance evidence. Satisfying an evidence-remediation plan should create a new pinned, comparable examination rather than mutate the completed disposition. This preserves the judgment trail from an earlier `INDETERMINATE` result to a later `PASS`, `FAIL`, `CONSTRAINED`, or narrower residual `INDETERMINATE` result.

The governing workflow is:

`change → RAHP proposition → DPIP examination → INDETERMINATE → machine-readable evidence demand → evidence production → pinned rerun → disposition`

The governing principle is:

> **INDETERMINATE is the disposition; evidence remediation is the action.**
