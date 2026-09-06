# DTG Privacy-Preserving Implementation Profile

**DPIP evaluates whether a composed interaction preserves its intended privacy properties.** A privacy-capable credential, proof, identifier or Trust Task can still participate in a composition that exposes reusable identifiers, graph relationships, lookup keys, telemetry or other correlation surfaces.

DPIP v0.1 also operates as a portable autonomous privacy-assurance specialist for compatible assurance controllers: it accepts source-pinned examinations, evaluates admissible evidence, produces finite portable results, and returns them through durable retryable outbox semantics.

## Start here

Use [`docs/understanding-dpip.md`](docs/understanding-dpip.md) for the conceptual model and outcome semantics. Implementers/deployers should use [`docs/deployment-guide/`](docs/deployment-guide/); reviewers should use [`spec/dpip-v0.1-draft.md`](spec/dpip-v0.1-draft.md), [`examples/`](examples/) and [`results/`](results/); integration authors should use [`schema/`](schema/), [`evidence/`](evidence/), [`scripts/`](scripts/) and [`docs/rahp-return-operations.md`](docs/rahp-return-operations.md).

[`readiness/v0.1.yaml`](readiness/v0.1.yaml) is the authoritative v0.1 release gate.

## Current capability boundary

The v0.1 baseline includes canonical C1-C6 privacy interactions and RF-001-RF-004 composed reference flows; scoped declared/observable/effective correlation semantics; machine-readable profile, evidence, finding, result and change-impact contracts; positive, negative and adversarial tests; source-pinned evidence packages; explicit provenance classes; deterministic evidence planning/acquisition; finite evidence-ready, evidence-required and model-gap paths; portable `rahp-assessor-result/v1` results; durable specialist-return/outbox semantics; and shared producer/consumer fixtures with RAHP.

A successful cryptographic operation, component test or repository workflow is never promoted into a composed privacy PASS unless the exact proposition has sufficient admissible evidence. The detailed outcome vocabulary and reading guidance live in [`docs/understanding-dpip.md`](docs/understanding-dpip.md).

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

Specification/source evidence establishes what a conforming system is required, permitted or expected to expose; it cannot establish what two actual runtime contexts observed. Synthetic/calibration fixtures test evaluator behavior; attributable runtime observations test implementation behavior. Evidence must satisfy the provenance class and immutable source identity required by the named `ER-*` obligation. Missing evidence is useful information but is never PASS.

## Release status

**v0.1.0 — Khajjiar Lake** is the first governed release candidate. The historical RF-001 Trust Task binding blocker is no longer an unhandled semantic dead end: DPIP models the correlation surface, mechanically pressure-tests prohibited thread/envelope reuse, and deterministically returns evidence-required when authoritative runtime observations are absent. This resolves the release blocker without claiming universal privacy success.

See [`readiness/v0.1.yaml`](readiness/v0.1.yaml) and [`docs/releases/v0.1.0.md`](docs/releases/v0.1.0.md).
