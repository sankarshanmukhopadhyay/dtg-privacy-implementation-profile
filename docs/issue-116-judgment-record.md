# Judgment record — DPIP #116

## Proposition

An `INDETERMINATE` DPIP result should remain a legitimate assurance disposition while also producing the smallest bounded evidence package capable of changing that result.

## Decision

Emit a machine-readable `evidence_remediation_plan` as part of evidence-incomplete DPIP conclusions and propagate a compact form back to RAHP.

## Alternatives considered

- **Generic “obtain more evidence” action:** rejected because it does not make the examination operationally rerunnable.
- **Treat repository fixtures as sufficient implementation evidence:** rejected because detector calibration cannot establish upstream runtime behaviour.
- **Reduce INDETERMINATE by inferring from specification intent:** rejected because it would silently weaken the assurance boundary.
- **Demand broad telemetry:** rejected because assurance evidence collection can itself create privacy risk.

## Pressure tests and falsification boundaries

The implementation must preserve these boundaries:

- missing executable or runtime evidence remains `INDETERMINATE`;
- DPIP-local and upstream-runtime requirements are separately routed;
- the generated remediation plan is deterministic for the same execution record;
- privacy-safe capture guidance is present for every evidence requirement;
- a completed examination is not mutated when evidence later arrives; a new pinned comparable rerun is required;
- a synthetic fixture never becomes evidence that an upstream implementation exhibited the fixture behaviour.

## Residual uncertainty / deferred work

This change defines and routes evidence demands. It does not itself make C3/C5 executable; that is deliberately separated into DPIP #117. Nor does it produce upstream runtime traces. Those remain authoritative external evidence requirements.

## Human acceptance decision

Merge should mean acceptance of the evidence-directed `INDETERMINATE` contract, not acceptance of any privacy claim about the implementation examined in DPIP #111.
