# Machine-readable DPIP profiles

DPIP interaction profiles are represented as YAML or JSON instances of `interaction-profile.schema.json`.

The format is intentionally centered on an end-to-end composed interaction rather than a credential format, proof mechanism, or transport.

## Stable identifiers

- `C<n>` — canonical interaction
- `P<n>` — DPIP privacy invariant
- `PP-<n>` — privacy/conformance profile
- `C<n>-R<n>` — interaction requirement
- `C<n>-CS-<n>` — correlation surface
- `C<n>-T<n>` — test case

Stable identifiers allow requirements, adversarial cases, portfolio-monitor findings, and later executable results to refer to the same semantic object.

## Construction neutrality

A profile records the privacy property required at a boundary. It may describe constraints that any selected construction must meet, but it does not normally select a DID method, ZKP scheme, status mechanism, transport, wallet, or VTA implementation.

A deployment-specific conformance record may bind the abstract profile to concrete component versions and configurations.

## Traceability

Every test should identify the requirements and invariants it exercises. Every correlation surface should identify the invariants it can affect. This supports later automated checks such as:

- orphan requirements with no tests;
- tests with missing requirements;
- profile claims with unassessed correlation surfaces;
- underlying specification changes that affect a referenced component boundary;
- regression cases derived from RAHP findings.

## First fixture

`examples/c1-personhood-presentation.yaml` is the first normative-development fixture. It is deliberately more detailed than a minimal example because it is being used to pressure-test the schema before C2 and C3 are added.

The schema is a development baseline and is expected to evolve while preserving the stable semantic identifiers of published interaction cases where feasible.
