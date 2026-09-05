# DTG #371 correlation-scope privacy evidence plan

Status: experimental assurance evidence against an adopted upstream correlation-scope baseline

Parent assurance work:

- RAHP Discussion #371
- RAHP historical Track A #373 / PR #385
- RAHP source-transition controller #397
- RAHP bounded reconciliation #433
- Canonical proposition matrix: RAHP #372 / `DTG-371-P02`, `P04`, `P05`, `P13`

## Source transition

Historical evidence remains pinned to `trustoverip/dtgwg-cred-spec` PR #30 head `b3840f430f5bd01addab95881350a7f860e763e2` with authority status `proposed-upstream`.

The current source boundary is merged PR #30, merge commit `c8ef706b4d407a3a68a26b5fe2ce554c43674683` (2026-09-05). The correlation-scope semantics established by that merge are now `adopted-upstream-main`.

Upstream `trustoverip/*` is read-only. DPIP changes remain confined to repositories owned by `sankarshanmukhopadhyay`.

## Judgment boundary

Adoption changes specification authority, not the privacy evidence standard. A declaration of `pairwise`, `directed`, or `public` is not runtime privacy evidence.

Track A continues to distinguish declared scope, observable scope, and effective scope. A specification-level PASS cannot be promoted into an effective-privacy PASS.

## Reconciled semantics

The adopted scope axis is `pairwise | directed | public`. Legacy `community` is not a fourth scope; holder-selected reuse is represented by `directed`. Strict pairwise reuse across relationships is contradictory evidence where observations expose it.

The prior carriage uncertainty has narrowed materially: the adopted direction carries the declaration in the credential. DPIP therefore evaluates privacy consequences of credential carriage rather than treating credential-vs-DID-document placement as an unresolved normative choice.

Supporting services do not automatically become counterparties, but their observability remains part of effective-correlation evidence when it creates a join surface.

## Canonical evidence requirements

No new evidence class is required. Track A remains bound to:

- `ER-REL-DID-AB` — cross-context relationship identifier/binder observations;
- `ER-STATUS-AB` — status and policy-discovery observations;
- `ER-TASK-AB` — retained task/relationship evidence observations;
- `ER-VERIFIER-AB` — verifier transcript and deliberate-correlation observations;
- `ER-CREDENTIAL-ID-AB` — credential/presentation/proof/status identifier observations.

The `dtg-371-correlation-scope-convergence` binding remains canonical.

## Evidence cases

A1 pairwise contradiction, A2 counterparty/VTC widening, A3 retained-interaction joins, A4 bounded intentional reconnection, A5 credential-carriage consequences, and A6 durability independence remain required evidence surfaces.

Upstream issue #38 adds a residual: where digest-valued binders occur in a tested composition, DPIP must measure joinability and must not infer privacy merely from use of a cryptographic digest. DPIP does not invent the unresolved normative construction.

## Evidence admission and disposition

Synthetic fixtures may test evaluator mechanics, but final `DTG-371-P02`/`P13` effective-correlation conclusions require attributable runtime observations against immutable component pins. Historical fixture evidence cannot be relabelled as runtime proof of the merged baseline.

Where runtime evidence is unavailable, the result remains `INDETERMINATE / evidence-required` with the canonical requirement IDs and producer capability `composed-unlinkability-v1`.

The PR #30 merge therefore does **not** promote Track A privacy assurance to GREEN. It strengthens specification authority and removes one former design uncertainty while leaving runtime privacy evidence obligations intact.

## Reassessment rule

Historical source-pinned evidence is immutable. Reassess only when a source transition changes semantics material to a bound privacy proposition, runtime implementation pins change, or a residual such as binder blinding changes the observable join surface. A changed upstream SHA is a trigger for semantic comparison, not automatic invalidation of every evidence artifact.
