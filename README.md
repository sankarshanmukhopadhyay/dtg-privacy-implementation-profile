# DTG Privacy-Preserving Implementation Profile

**DPIP answers a simple question: when components are used together, does the resulting interaction preserve the privacy properties we intended?**

A credential, proof system, pairwise identifier or Trust Task can be privacy-capable on its own while the complete interaction still exposes a reusable identifier, graph relationship, operator lookup key, telemetry value or other correlation surface. DPIP therefore evaluates privacy over the **composed interaction**, not by inference from individual components.

DPIP v0.1 also operates as a **portable autonomous privacy-assurance specialist** for compatible assurance controllers. It can consume a source-pinned examination, execute or evaluate the available evidence, terminate with a finite portable result, and return that result through durable retryable outbox semantics.

```text
composed interaction / referred proposition
      ↓
canonical privacy scope + evidence obligations
      ↓
evidence planning / supplied evidence / provenance admission
      ↓
execution and bounded privacy inference
      ↓
PASS | FAIL | INDETERMINATE | NOT_APPLICABLE
      ↓
portable assessor result + human explanation
      ↓
durable return/outbox → compatible assurance controller
```

## Start here

If DPIP is new to you, begin with [`docs/understanding-dpip.md`](docs/understanding-dpip.md). Implementers/deployers should use [`docs/deployment-guide/`](docs/deployment-guide/); reviewers should use [`spec/dpip-v0.1-draft.md`](spec/dpip-v0.1-draft.md), [`examples/`](examples/) and [`results/`](results/); integration authors should use [`schema/`](schema/), [`evidence/`](evidence/), [`scripts/`](scripts/) and [`docs/rahp-return-operations.md`](docs/rahp-return-operations.md).

[`readiness/v0.1.yaml`](readiness/v0.1.yaml) is the authoritative v0.1 release gate.

## Current capability boundary

The v0.1 baseline includes:

- canonical C1-C6 privacy interactions and RF-001-RF-004 composed reference flows;
- scoped privacy claims and declared/observable/effective correlation scope;
- machine-readable profile, evidence, finding, result and change-impact contracts;
- positive, negative and adversarial conformance tests;
- implementation-backed and source-pinned evidence packages;
- explicit evidence provenance classes separating source-backed, synthetic/calibration and attributable runtime observations;
- deterministic evidence planning and acquisition contracts;
- supplied-evidence examinations that do not manufacture redundant acquisition work;
- finite evidence-ready and evidence-incomplete execution paths;
- portable `rahp-assessor-result/v1` results;
- deterministic `INDETERMINATE / evidence-required` remediation plans;
- deterministic `INDETERMINATE / model-gap` behavior for unmapped evidence surfaces;
- human-readable dispositions that remain subordinate to the formal machine result;
- durable specialist-return outbox markers, delivery acknowledgement, automatic retry and idempotent reconciliation;
- shared producer/consumer contract fixtures with RAHP for assessor-result and evidence-remediation shapes;
- release governance with persisted Indian-lake codenames and machine-readable readiness.

A successful cryptographic operation, component test or repository workflow is never promoted into a composed privacy PASS unless the exact privacy proposition has sufficient admissible evidence.

## Outcomes

- **PASS:** admissible evidence supports the tested expectation for the stated scope.
- **FAIL:** the tested expectation is not met.
- **INDETERMINATE / evidence-required:** the proposition is understood but required evidence is absent or inadmissible; DPIP returns the smallest bounded evidence-remediation contract it can state.
- **INDETERMINATE / model-gap:** the proposition/evidence surface is not yet mapped sufficiently to make the requested inference; the gap is terminal and actionable rather than a parser/lifecycle failure.
- **NOT_APPLICABLE:** the referred proposition does not apply to the examined privacy scope.

Historical `CONSTRAINED` conformance results remain valid where that result vocabulary is used in DPIP-native fixtures; portable specialist returns use the finite controller contract above.

## What DPIP owns — and does not own

DPIP does **not** redefine DTG Credentials, Trust Tasks, ZKP constructions, relationship artifacts, agent naming, VTA behavior, DID methods, transports, wallets, discovery policy or VTN governance. Those components own their semantics and mechanisms.

DPIP owns the **composition privacy contract**: the conditions under which an implementation can make a scoped end-to-end privacy claim and the evidence needed to support that claim. A component PASS does not imply a composition PASS.

A useful assurance boundary is:

```text
change/source observer: What changed?
RAHP or compatible controller: What could go wrong and what specialist is needed?
DPIP: What privacy property does the composed system actually preserve?
owning component/deployer/governance authority: What should change?
```

DPIP is not version-locked to a particular RAHP release. Interoperability is governed by compatible versioned contracts and shared fixtures.

## Current interaction baseline

| ID | In ordinary language |
| --- | --- |
| **C1** | Privacy-preserving personhood presentation |
| **C2** | Privacy-preserving relationship proof |
| **C3** | Cross-community asymmetric relationship proof |
| **C4** | Privacy-preserving policy discovery |
| **C5** | Privacy-preserving lifecycle evaluation and precedence |
| **C6** | Privacy-preserving recovery and migration |

Reference flows RF-001 through RF-004 compose these concerns into whole-system integration hypotheses.

## Evidence discipline

Specification/source evidence can establish what a conforming system is required, permitted or expected to expose. It cannot establish what two actual contexts observed. Synthetic/calibration fixtures can prove that DPIP detects a prohibited pattern; they do not prove a deployment exhibited it. Runtime evidence must carry the provenance class and immutable implementation/source identity required by the named evidence obligation.

Missing evidence is useful information but is never PASS.

## Release status

**v0.1.0 — Khajjiar Lake** is the first governed release candidate. The historical RF-001 Trust Task binding blocker is no longer an unhandled semantic dead end: DPIP now models the correlation surface, can mechanically pressure-test prohibited thread/envelope reuse, and deterministically returns evidence-required when authoritative runtime observations are absent. This resolves the release blocker without claiming universal privacy success.

See [`readiness/v0.1.yaml`](readiness/v0.1.yaml) and [`docs/releases/v0.1.0.md`](docs/releases/v0.1.0.md).
