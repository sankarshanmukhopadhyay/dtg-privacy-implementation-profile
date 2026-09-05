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

The current source boundary is the merged PR #30 baseline on upstream `main`, merge commit `c8ef706b4d407a3a68a26b5fe2ce554c43674683` (2026-09-05). For the correlation-scope semantics actually established by that merge, the source authority is now `adopted-upstream-main`.

This repository does not modify upstream. `trustoverip/*` is a read-only evidence/dependency source; DPIP changes are confined to repositories owned by `sankarshanmukhopadhyay`.

## Judgment boundary

Adoption of the three-value correlation-scope model changes specification authority, not the privacy evidence standard. DPIP does not treat a declaration of `pairwise`, `directed`, or `public` as runtime privacy evidence.

DPIP owns the narrower privacy question: whether the complete observable and retained interaction behaves consistently with the claimed correlation boundary, and whether surrounding protocol, resolution, status, governance, task, proof or binder surfaces widen effective correlation beyond that declaration.

Track A therefore continues to separate:

1. **declared scope** — holder-declared intended correlation;
2. **observable scope** — what a particular observer can see;
3. **effective scope** — what can actually be joined after retained evidence, status/resolution traffic, counterparty/VTC disclosure and deliberate correlation attempts are considered.

A specification-level PASS cannot be promoted into an effective-privacy PASS.

## Reconciled semantics

The adopted scope axis is `pairwise | directed | public`. Legacy `community` is not a fourth scope: reuse with a holder-chosen set is represented by `directed`. Strict pairwise use across multiple relationships requires distinct identifiers; contradictory reuse is verifier-observable evidence against the declaration where the observations are available.

The prior Track A carriage uncertainty is narrowed materially: the adopted direction carries the declaration in the credential. DPIP no longer treats credential-vs-DID-document placement as an unresolved normative choice. It still evaluates privacy consequences of the selected carriage, including repeated disclosure, caching/history, verifier retention and lifecycle interpretation.

Supporting services such as witnesses, identity-proofing or resolution actors do not automatically become counterparties for the declaration. Their observability nevertheless remains part of DPIP effective-correlation evidence where it creates a join surface.

## Canonical evidence requirements

No new privacy evidence class is required. The #371 questions remain bound to:

- `ER-REL-DID-AB` — cross-context relationship identifier/binder observations;
- `ER-STATUS-AB` — status and policy-discovery observations;
- `ER-TASK-AB` — retained task/relationship evidence observations;
- `ER-VERIFIER-AB` — verifier transcript and deliberate-correlation observations;
- `ER-CREDENTIAL-ID-AB` — credential/presentation/proof/status identifier observations.

The `dtg-371-correlation-scope-convergence` binding remains the canonical mapping.

## Required evidence cases

### A1 — pairwise contradiction

Two unrelated counterparties observe the same holder identifier declared `pairwise`.

Expected privacy disposition: FAIL for the claimed pairwise property. This is falsification evidence and does not prove universal discoverability.

### A2 — counterparty/VTC widening

The holder uses a `pairwise` identifier toward one relationship boundary, but a counterparty, VTC or governance-controlled surface publishes, forwards or exposes it to another observer.

Expected privacy disposition: holder intent remains recorded, but effective deployment privacy is FAIL or CONSTRAINED according to attributable observations. The declaration is never proof of counterparty non-disclosure.

### A3 — retained interaction joins unrelated contexts

Identifier choice is pairwise at the credential layer, but unrelated relying contexts can join the same subject/relationship using proof binders, task IDs, status handles, resolution traffic, timestamps or retained outcome evidence.

Expected privacy disposition: FAIL for the affected composed unlinkability claim even if credential/proof verification succeeds.

### A4 — intentional reconnection

Distinct identifiers are deliberately reconnected through a common-control proof for a bounded verifier/purpose/context.

Expected privacy disposition: intentional correlation is not itself a defect. PASS requires evidence that the proof does not export an unnecessary durable binder or widen correlation outside the intended context.

### A5 — credential carriage

Evaluate the adopted credential-carried declaration for disclosure frequency, verifier retention, caching/history and lifecycle interpretation. This is now an implementation/profile evidence question, not a request for DPIP to choose between credential and DID-document carriage.

### A6 — durability independence

A long-lived `pairwise` identifier is evaluated against relationship lifetime and rotation/recovery needs independently from its narrow declaration. DPIP records privacy consequences when lifecycle failure causes identifier reuse, migration leakage or forced wider correlation.

### A7 — enumerable digest binders

Upstream issue #38 records an unresolved risk that digest-valued binders can be enumerable without salt/blinding. Where such binders are present in a tested composition, DPIP must measure whether they create cross-context joinability. DPIP must not invent the missing normative construction or assume a digest is privacy-preserving merely because it is cryptographic.

## Evidence admission and current disposition

Synthetic fixtures may test evaluator mechanics, but final `DTG-371-P02`/`P13` effective-correlation conclusions require attributable runtime observations against immutable component pins. Historical fixture evidence cannot be relabelled as runtime proof of the merged baseline.

Where runtime evidence is unavailable, the result remains `INDETERMINATE / evidence-required` with the canonical requirement IDs and producer capability `composed-unlinkability-v1`.

The PR #30 merge therefore **does not promote Track A privacy assurance to GREEN**. It strengthens specification authority and removes one former design uncertainty while leaving runtime privacy evidence obligations intact.

## Reassessment rule

Historical source-pinned evidence is immutable. Reassess only when a source transition changes semantics material to a bound privacy proposition, when runtime implementation pins change, or when a residual such as binder blinding materially changes the observable join surface. A changed upstream SHA is a trigger for semantic comparison, not automatic invalidation of every evidence artifact.
