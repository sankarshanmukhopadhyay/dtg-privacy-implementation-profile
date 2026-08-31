# RAHP / compatible-controller return operations

DPIP returns completed controller-originated privacy examinations through a **durable, retryable specialist-return outbox**. The automation transports an already-constructed conclusion; it does not invent one from labels, prose or issue closure.

## Completion invariant

A specialist completion must imply a valid returnable result exists. Before `run:complete`, DPIP constructs and validates the formal examination result and, for current executions, the portable `rahp-assessor-result/v1` block.

Portable outcomes are finite:

```text
PASS
FAIL
INDETERMINATE
NOT_APPLICABLE
```

`INDETERMINATE` is further explained by reason codes such as `evidence-required` or `model-gap`. Missing evidence never becomes PASS.

## Durable outbox transaction

Cross-repository delivery is not treated as a best-effort side effect.

1. DPIP constructs the return payload.
2. A durable outbox marker records the payload digest on the specialist examination before delivery.
3. Delivery is attempted using the compatible controller transport.
4. A delivery acknowledgement is recorded only after the controller disposition and lifecycle mutations succeed.
5. If delivery fails, the pending outbox remains machine-visible and scheduled reconciliation retries it.
6. Repeated delivery of the same payload digest is idempotent; an existing controller return marker prevents duplicate semantic returns.

A missing cross-repository credential is therefore a transport failure, not a successful no-op and not a human-only transition.

## Model-gap behavior

A valid `INDETERMINATE` conclusion whose evidence surface is not yet mapped to canonical requirements does not fail return parsing. DPIP synthesizes a bounded `model-gap` remediation contract that identifies the evidence/model surface requiring work. This is the regression class exposed by DPIP #149 / RAHP #309 and is covered by current self-tests/shared fixtures.

## Shared compatibility fixtures

DPIP mirrors and validates the compatible controller-owned shapes used for:

- `rahp-assessor-result/v1`;
- `rahp-evidence-remediation/v1`.

Producer and consumer validate shared-shape fixtures in CI so contract compatibility is executable rather than an assumption embedded independently in parsers. DPIP is not version-locked to RAHP; schema/contract compatibility is authoritative.

## Human-readable disposition

The formal result is authoritative. A `human_summary` may present the same outcome, explanation and action in ordinary language. When absent, the return tooling derives a conservative explanation from the structured evidence summary, residual correlation and action fields without changing the formal conclusion.

## Evidence boundary

Source-backed evidence, repository-native synthetic/calibration fixtures and attributable runtime observations remain distinct. A return can be terminal and actionable while still being INDETERMINATE because the required evidence class is absent.

## Trigger and reconciliation

The return workflow handles completed `source:rahp` examinations and supports explicit/scheduled reconciliation. Scheduled reconciliation is recovery, not the normal semantic authority.

Configure `RAHP_HANDOFF_TOKEN` as a narrowly scoped credential able to write the compatible RAHP repository's Issues surface. The repository `GITHUB_TOKEN` remains bounded to DPIP-local operations. Without the handoff credential, cross-repository delivery must fail visibly and remain retryable.

## Controller lifecycle effect

A successful RAHP return applies the controller's DPIP-complete disposition and removes transient candidate/requested/open markers as appropriate. DPIP completion deliberately does not imply that the wider RAHP assessment is complete; privacy may be one specialist subflow inside a broader assurance run.

A completed INDETERMINATE examination is still complete for its pinned evidence boundary. Re-examination requires materially changed evidence, source pin, target/question or governing profile rather than mutation of completed history.
