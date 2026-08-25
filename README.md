# DTG Privacy-Preserving Implementation Profile

An implementation-centric profile and playbook for composing Decentralized Trust Graph (DTG) specifications into privacy-preserving systems.

DPIP defines cross-component privacy invariants, correlation surfaces, implementation patterns, conformance profiles, adversarial tests, evidence bindings, reference composed flows, findings and executable validation for end-to-end DTG deployments.

## Start here

For implementers, begin with:

1. [`spec/dpip-v0.1-draft.md`](spec/dpip-v0.1-draft.md) — structured v0.1 implementation specification draft;
2. [`examples/`](examples/) — canonical interactions C1-C5 with machine-readable requirements and tests;
3. [`reference-system/`](reference-system/) — non-normative composed DTG flows used to pressure-test DPIP;
4. [`docs/deployment-guide/`](docs/deployment-guide/) — implementation/deployment guidance;
5. [`readiness/v0.1.yaml`](readiness/v0.1.yaml) — authoritative v0.1 release-readiness state.

The existence of a v0.1 draft does **not** mean v0.1 is release-ready. The machine-readable readiness artifact and CI remain authoritative.

## Why this project exists

DTG components can individually support privacy while still producing a privacy failure when composed. A selective-disclosure credential, unlinkable proof, pairwise identifier, or privacy-aware Trust Task is not sufficient if another required component introduces a durable correlator, excessive disclosure, linkable metadata, conflicting lifecycle semantics, or unnecessary retained state.

This project therefore treats the **composed interaction** as the primary unit of privacy evaluation.

## What this project owns

This profile does **not** redefine DTG Credentials, Trust Tasks, ZKP constructions, relationship artifacts, agent naming, VTA behavior, DID methods, transports, wallets, discovery policy, or VTN governance.

It defines the **composition contract** between those components: the conditions under which an implementation can make a scoped end-to-end privacy claim and the evidence needed to support that claim.

## Current interaction baseline

- **C1** privacy-preserving personhood presentation;
- **C2** privacy-preserving relationship proof;
- **C3** cross-community asymmetric relationship proof;
- **C4** privacy-preserving policy discovery;
- **C5** privacy-preserving lifecycle evaluation and precedence.

Reference flows RF-001 through RF-003 exercise these interactions as whole-system integration hypotheses.

## Design posture

The profile is intended to remain:

- implementation-centric;
- construction-neutral where possible;
- compatible with evolving DTG component specifications;
- testable at composed-interaction boundaries;
- explicit about declared, observable and effective correlation scope;
- capable of turning pressure-test findings into reviewed requirements/tests or upstream issues;
- progressively translatable into machine-readable conformance and portfolio revalidation evidence.

## Repository structure

```text
spec/              specification drafts and architecture history
docs/              implementation guidance and supporting models
examples/          canonical interaction profiles and tests
reference-system/  non-normative composed flows and findings
schema/             machine-readable artifact formats
results/            conformance-result fixtures
evidence/           external evidence bindings
readiness/          release-readiness gates
portfolio/          cross-repository change-impact metadata
scripts/            validation and assurance tooling
```

## Status

Development draft. The executable baseline is substantial, but v0.1 MUST NOT be declared until the readiness gate reports ready.
