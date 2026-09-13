# DTG Privacy-Preserving Implementation Profile

**Current stable release: v0.2.0 — Prashar Lake**

DPIP evaluates whether a composed interaction preserves its intended privacy properties. A privacy-capable credential, proof, identifier or Trust Task can still participate in a composition that exposes reusable identifiers, graph relationships, lookup keys, telemetry or other correlation surfaces.

DPIP v0.2.0 operates as a portable privacy-assurance specialist for compatible assurance controllers: it accepts source-pinned examinations, evaluates admissible evidence, produces finite portable results, and returns them through durable retryable outbox semantics.

## Start here

Use [`docs/understanding-dpip.md`](docs/understanding-dpip.md) for the conceptual model and outcome semantics. Implementers/deployers should use [`docs/deployment-guide/`](docs/deployment-guide/); reviewers should use [`spec/dpip-v0.1-draft.md`](spec/dpip-v0.1-draft.md), [`examples/`](examples/) and [`results/`](results/); integration authors should use [`schema/`](schema/), [`evidence/`](evidence/), [`scripts/`](scripts/) and [`docs/rahp-return-operations.md`](docs/rahp-return-operations.md).

## What v0.2.0 adds

v0.2.0 packages the post-v0.1 evidence tranche into a stable boundary:

- attributable runtime evidence handling across composed privacy examinations;
- bounded A/B correlation analysis for relationship/verifier, status, Trust Task and policy-discovery surfaces;
- explicit distinction between intentional common service surfaces and evidence of subject correlation;
- Data Rooms E1-E6 observability contracts and private-tier evidence boundaries;
- durable transfer of privacy-specific residuals from RAHP into DPIP-owned examination issues;
- evidence-required outcomes when realistic deployment/observer evidence is absent rather than inferred privacy PASS;
- continued portable `rahp-assessor-result/v1` returns and deterministic evidence planning/acquisition.

## Current capability and evidence boundary

The canonical C1-C6 privacy interactions and RF-001-RF-004 composed reference flows remain the baseline. DPIP models declared, observable and effective correlation semantics; machine-readable profile/evidence/finding/result/change-impact contracts; source-pinned evidence packages; provenance classes; positive, negative and adversarial tests; deterministic evidence planning/acquisition; and finite evidence-ready, evidence-required and model-gap paths.

The 2026-09-08 RAHP-triggered relationship-correlation rerun consumed attributable OpenVTC A/B evidence produced by the Trust Protocol Interop Lab. Within that exact pinned runtime boundary, DPIP reached **SATISFIED** for the exercised relationship/verifier, status, Trust Task and policy-discovery surfaces. That result is deliberately bounded: it does not establish deployment-wide unlinkability, network/device unlinkability or universal privacy across unexercised transports and implementations.

Data Rooms remain a separate evidence boundary. [`docs/data-room-observability.md`](docs/data-room-observability.md) defines the E1-E6 observability contract. Private-room runtime execution remains unavailable where same-subject/common-control ZK support or deployment evidence does not exist; those propositions remain `EVIDENCE_REQUIRED` rather than being promoted by architectural intent.

Issuer-side credential enumeration is likewise treated as a privacy/governance question in its own right: body minimization and successful authorization do not, by themselves, prove that historical holder metadata is appropriately minimized or non-correlating for a real deployment role.

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

## Coordinated release context

v0.2.0 is the DPIP member of the September 2026 coordinated RAHP / DPIP / Trust Protocol Interop Lab release tranche. The three repositories remain independently versioned and governed. RAHP owns assurance state and orchestration; DPIP owns composed privacy examination; the Lab owns bounded executable evidence. Cross-repository conclusions remain source-pinned and proposition-scoped.

## Release status

**v0.2.0 — Prashar Lake** is the current stable release. It supersedes v0.1.0 **Khajjiar Lake** as the default GitHub release while preserving the v0.1.0 record unchanged.

See [`docs/releases/v0.2.0.md`](docs/releases/v0.2.0.md), [`ROADMAP.md`](ROADMAP.md), and the repository evidence/results surfaces for the detailed bounded claims.

## License

DPIP is licensed under the [Apache License 2.0](LICENSE). Third-party material retains its original copyright and licensing terms where separately identified.
