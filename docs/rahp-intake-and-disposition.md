# RAHP intake and disposition contract

DPIP accepts a RAHP handoff only after RAHP has identified a specific source change, a specific DPIP target, and an actionable privacy examination question. The handoff preserves a strict boundary: RAHP owns the originating risk hypothesis; DPIP owns applicability and the scoped privacy conclusion.

## Intake provenance

Every RAHP-originated DPIP issue SHOULD record:

```yaml
source:
  system: RAHP
  repository: sankarshanmukhopadhyay/rahp-toolkit
  issue: <number>
  portfolio_monitor:
    finding_id: <finding-id>
    fingerprint: <fingerprint>
  changed_artifact:
    repository: owner/repository
    revision: <immutable-revision>
    pull_request: <number-or-null>
```

Where an immutable revision does not exist, DPIP records the limitation rather than treating a mutable issue/discussion as verified implementation evidence.

## Requested examination

The intake SHOULD identify the narrowest useful DPIP targets:

```yaml
requested_examination:
  interactions: [C3]
  reference_flows: [RF-001]
  invariants: [P2, P4]
  claims: [C3-PC-2]
  suspected_surfaces: [identity, protocol-envelope]
  question: >-
    The concrete privacy question DPIP is being asked to resolve.
```

DPIP may narrow or expand the mapping when the examination shows that other claims or correlation surfaces are materially affected, but it records that change in scope.

## Intake lifecycle

DPIP uses:

- `source:rahp` — provenance marker for RAHP-originated examination;
- `run:requested` — intake exists but substantive examination has not started;
- `run:in-progress` — applicability/evidence analysis is underway;
- `run:complete` — the examination has a final disposition.

Lifecycle labels are state, not severity. A completed `FAIL`, `CONSTRAINED`, `INDETERMINATE`, or `NOT_APPLICABLE` examination is still `run:complete`.

## Applicability triage

DPIP first asks whether the changed artifact can alter a scoped privacy property evaluated by the identified interaction/reference flow.

`NOT_APPLICABLE` is an intake disposition, not a DPIP conformance-result status. It is appropriate when the RAHP referral was reasonable but the change does not participate in, or alter, the claimed DPIP property in the stated scope.

For applicable referrals, DPIP uses its existing result vocabulary as appropriate: `PASS`, `FAIL`, `CONSTRAINED`, `INDETERMINATE` and test-level `NOT_RUN`.

A source change that removes one correlation surface does not automatically establish a higher-level privacy claim. DPIP must continue to account for residual graph, protocol, observer, deployment, lifecycle and privileged-operator correlation.

## Evidence discipline

DPIP distinguishes what a source change proves from what it merely suggests.

A commit-pinned code/configuration change may be verified evidence that a particular implementation path changed. It is not automatically verified evidence of runtime unlinkability across independent contexts. Runtime or cross-context privacy claims require evidence appropriate to those claims, such as generated traces, test vectors, observations or implementation-run artifacts.

Issue/discussion evidence remains candidate unless backed by an immutable artifact. Missing upstream semantics or construction evidence produce `INDETERMINATE`, not invented semantics.

## Deduplication and idempotency

Before creating or accepting a second DPIP issue, the handoff should be compared using:

```text
Monitor fingerprint + source repository + immutable source revision + materially equivalent DPIP target/question
```

A repeated weekly Monitor observation does not reopen or duplicate a completed examination. Re-examination requires a materially changed source revision, materially new evidence, or a changed DPIP target.

## DPIP technical conclusion

The DPIP issue SHOULD record:

```yaml
dpip_examination:
  applicability: applicable | not-applicable
  conclusion: PASS | FAIL | CONSTRAINED | INDETERMINATE | NOT_APPLICABLE
  affected_interactions: [C3]
  affected_reference_flows: [RF-001]
  affected_claims: [C3-PC-2]
  evidence:
    - <immutable or otherwise scoped evidence>
  evidence_summary: >-
    What the evidence establishes and what it does not establish.
  residual_correlation: >-
    Remaining effective correlation relevant to the requested claim.
  action: none | dpip-regression | upstream-clarification | upstream-defect | accepted-limitation | evidence-gap | implementation-specific
```

The full reasoning remains in DPIP. The source RAHP issue receives only the concise disposition and link.

## Return path

After completion DPIP posts a concise disposition to the originating RAHP issue containing the DPIP issue number, applicability, conclusion, affected DPIP scope, evidence summary, residual correlation and action. RAHP then transitions the source issue to `assurance:dpip-complete`.

`INDETERMINATE` MUST NOT trigger automatic re-referral on the next monitoring cycle. The return record should identify the evidence condition that would justify re-examination.

## Automation gate

Cross-repository creation and return updates remain manual until three materially different contract tests succeed:

1. applicable examination;
2. `NOT_APPLICABLE` referral;
3. `INDETERMINATE` referral due to missing evidence.

Only after those tests demonstrate deterministic provenance, deduplication, lifecycle transitions and return-path behavior should RAHP automatically create DPIP issues. DPIP result generation remains assurance-driven; automation transports the request and disposition rather than prejudging either.
