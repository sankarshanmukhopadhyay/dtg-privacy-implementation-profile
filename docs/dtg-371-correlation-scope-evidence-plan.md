# DTG #371 correlation-scope privacy evidence plan

Status: experimental

Parent assurance work:

- RAHP Discussion: https://github.com/sankarshanmukhopadhyay/rahp-toolkit/discussions/371
- RAHP Track A: https://github.com/sankarshanmukhopadhyay/rahp-toolkit/issues/373
- Canonical proposition matrix: RAHP #372 / `DTG-371-P02`, `P04`, `P05`, `P13`

Upstream proposal pin:

- `trustoverip/dtgwg-cred-spec` PR #30
- head SHA: `b3840f430f5bd01addab95881350a7f860e763e2`
- authority status: `proposed-upstream`

## Judgment boundary

PR #30 defines the proposed correlation-scope semantics. DPIP does not decide whether those semantics are adopted, and it does not treat a declaration of `pairwise`, `directed`, or `public` as runtime privacy evidence.

DPIP owns the narrower privacy question: whether the complete observable and retained interaction behaves consistently with the claimed correlation boundary, and whether surrounding protocol, resolution, status, governance, task or proof surfaces widen effective correlation beyond that declaration.

Accordingly, Track A uses three separate quantities:

1. **declared scope** — what the holder says about intended correlation;
2. **observable scope** — what a particular observer can see in the interaction;
3. **effective scope** — what can actually be joined after protocol metadata, retained evidence, status/resolution traffic, counterparty disclosure and deliberate correlation attempts are considered.

A PASS at the declaration layer cannot be promoted into an effective-privacy PASS.

## Existing canonical evidence requirements

No new privacy evidence class is required for this wave. The semantic gap exposed by earlier RAHP/DPIP work has already been closed by the canonical evidence registry. The #371 correlation-scope questions bind to existing requirements:

- `ER-REL-DID-AB` — cross-context relationship identifier/binder observations;
- `ER-STATUS-AB` — status and policy-discovery observations;
- `ER-TASK-AB` — retained task/relationship evidence observations;
- `ER-VERIFIER-AB` — verifier transcript and deliberate-correlation observations;
- `ER-CREDENTIAL-ID-AB` — credential/presentation/proof/status identifier observations.

The new `dtg-371-correlation-scope-convergence` binding maps Track A surfaces onto those canonical requirements rather than creating another evidence vocabulary.

## Required Track A evidence cases

### A1 — pairwise contradiction

Two unrelated counterparties observe the same holder identifier that was declared `pairwise`.

Expected privacy disposition: FAIL for the claimed pairwise property. This case is definitional/falsification evidence and does not require proof that every possible observer can discover the reuse.

### A2 — counterparty/community widening

The holder uses a `pairwise` identifier toward one community, but the community publishes, forwards or otherwise exposes that identifier to another observer.

Expected privacy disposition: the holder declaration remains evidence of holder intent, but effective deployment privacy is FAIL or CONSTRAINED according to the resulting observation. A holder declaration must never be reported as proof of counterparty non-disclosure.

### A3 — retained interaction joins unrelated contexts

Identifier choice is correctly pairwise at the credential layer, but two unrelated relying contexts can join the same subject/relationship using proof binders, task IDs, status handles, resolution traffic, timestamps or retained outcome evidence.

Expected privacy disposition: FAIL for the affected composed cross-context-unlinkability claim even if credential/proof verification succeeds.

### A4 — intentional reconnection

Distinct identifiers are deliberately reconnected through a common-control proof for a bounded verifier/purpose/context.

Expected privacy disposition: the intentional correlation itself is not a defect. PASS requires evidence that the proof does not export an unnecessary durable binder or widen correlation outside the intended context.

### A5 — declaration carriage

Compare credential-carried and DID-document-carried scope declarations as design alternatives.

DPIP must record, not decide away, the privacy differences: resolver observability, network dependency, caching/history behavior, repeated credential disclosure, and lifecycle interpretation. Until upstream selects a carriage model, the privacy design result is bounded and cannot establish one normative implementation requirement.

### A6 — durability independence

A long-lived `pairwise` identifier must be evaluated against the credential relationship lifetime and key-rotation/recovery needs independently from its narrow correlation declaration.

DPIP does not determine DID-method suitability in general; it records privacy consequences when a lifecycle failure causes identifier reuse, migration leakage or forced wider correlation.

## Evidence admission

Synthetic fixtures may test evaluator mechanics, but the final `DTG-371-P02`/`P13` effective-correlation conclusion requires `runtime-upstream-observation` evidence against immutable component pins. Existing DPIP fixture evidence cannot be silently relabelled as runtime proof of the new PR #30 behavior.

Where runtime evidence is unavailable, the correct result is `INDETERMINATE / evidence-required` with the canonical evidence requirement IDs and producer capability `composed-unlinkability-v1`.

## Reassessment rule

Any material change to PR #30 head SHA, or an upstream resolution of the declaration-carriage question, makes dependent experimental evidence stale. Historical evidence remains immutable; a new run is produced against the new pin.
