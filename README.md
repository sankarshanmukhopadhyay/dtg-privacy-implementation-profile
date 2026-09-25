# DTG Privacy-Preserving Implementation Profile

**Current stable release: v0.3.0 — Manasbal Lake**

DPIP evaluates whether a composed interaction preserves its intended privacy properties. A privacy-capable credential, proof, identifier or Trust Task can still participate in a composition that exposes reusable identifiers, graph relationships, lookup keys, telemetry or other correlation surfaces.

DPIP v0.3.0 operates as a portable privacy-assurance specialist for compatible assurance controllers: it accepts source-pinned examinations, evaluates admissible evidence, expresses executable evidence obligations, consumes bounded Interop Lab evidence conservatively, and returns finite portable results through durable retryable outbox semantics.

## Start here

Use [`docs/understanding-dpip.md`](docs/understanding-dpip.md) for the conceptual model and outcome semantics. Implementers/deployers should use [`docs/deployment-guide/`](docs/deployment-guide/); reviewers should use [`spec/dpip-v0.1-draft.md`](spec/dpip-v0.1-draft.md), [`examples/`](examples/) and [`results/`](results/); integration authors should use [`schema/`](schema/), [`evidence/`](evidence/), [`scripts/`](scripts/) and [`docs/rahp-return-operations.md`](docs/rahp-return-operations.md).

## What v0.3.0 adds

v0.3.0 packages the post-v0.2 tranche into a stable executable privacy-evidence boundary:

- machine-verifiable `dpip-evidence-obligation/v1` work objects with explicit supplier, observer, target, maturity, assurability and residual-risk authority fields;
- deterministic admission/consumption rules that preserve `BLOCKED`, `EVIDENCE_REQUIRED` and `INDETERMINATE` when the named target or observation surface is unavailable;
- bounded consumption of Interop Lab human-power pressure evidence without promoting synthetic observations into deployment claims;
- conservative task-citation correlation evaluation that separates specification intent, source characterization, fixture evidence and target-runtime observation;
- C9 minimum-disclosure authority-proof semantics at material commitment, including durable mandate/approval identifiers as correlation surfaces;
- predicate-defined audience pressure tests for raw membership disclosure, correlation scope, minimized proof and missing observability;
- source-pinned persona reach/usage/timeline examination results with external-observer correlation retained as an explicit evidence obligation.

## Current capability and evidence boundary

The canonical C1-C6 interactions and RF-001-RF-004 reference flows remain valid. v0.3.0 adds C9 and broadens executable evidence-obligation and evidence-consumption machinery without changing the rule that privacy conclusions remain proposition-scoped.

DPIP distinguishes what a producer says, what a verifier or audit plane can observe, what a target runtime actually exposes, and what a privacy evaluator may conclude from that evidence. Fixture success, proof validity, authority success or a green workflow cannot substitute for missing privacy evidence.

The current persona examination credits implemented reach/minimisation/access controls and the intentional holder-side cross-context join while preserving external-observer/runtime correlation as `EVIDENCE_REQUIRED` until attributable A/B evidence exists.

## What DPIP owns — and does not own

DPIP does **not** redefine DTG Credentials, Trust Tasks, ZKP constructions, relationship artifacts, agent naming, VTA behavior, DID methods, transports, wallets, discovery policy or VTN governance. Those components own their semantics and mechanisms.

DPIP owns the **composition privacy contract**: the conditions under which an implementation can make a scoped end-to-end privacy claim and the evidence needed to support that claim. A component PASS does not imply a composition PASS.

```text
change/source observer: What changed?
RAHP or compatible controller: What could go wrong and what specialist is needed?
DPIP: What privacy property does the composed system actually preserve?
owning component/deployer/governance authority: What should change?
```

DPIP is not version-locked to a particular RAHP release. Interoperability is governed by compatible versioned contracts and shared fixtures.

## Evidence discipline

Specification/source evidence establishes what a conforming system is required, permitted or expected to expose; it cannot establish what two actual runtime contexts observed. Synthetic/calibration fixtures test evaluator behavior; attributable runtime observations test implementation behavior. Evidence must satisfy the provenance class and immutable source identity required by the named obligation. Missing evidence is useful information but is never PASS.

v0.3.0 additionally makes the evidence obligation itself machine-verifiable: absence of a target, observer surface, required maturity or assurability precondition is preserved as an explicit lifecycle state rather than silently repaired by the evaluator.

## Release context

v0.3.0 is independently versioned from RAHP and the Trust Protocol Interop Lab. The Lab may produce bounded executable observations; DPIP evaluates privacy propositions over admissible evidence; RAHP owns broader assurance state and residual reconciliation. Cross-repository conclusions remain source-pinned and proposition-scoped.

## Release status

**v0.3.0 — Manasbal Lake** is the current stable release. It supersedes v0.2.0 **Prashar Lake** as the default GitHub release while preserving prior release records unchanged.

See [`docs/releases/v0.3.0.md`](docs/releases/v0.3.0.md), [`ROADMAP.md`](ROADMAP.md), and the repository evidence/results surfaces for the detailed bounded claims.

## License

DPIP is licensed under the [Apache License 2.0](LICENSE). Third-party material retains its original copyright and licensing terms where separately identified.
