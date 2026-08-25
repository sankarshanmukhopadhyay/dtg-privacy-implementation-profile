# DTG Privacy-Preserving Implementation Profile v0.1 — Draft

Status: **development draft; not release-ready**

The authoritative release-readiness state is `readiness/v0.1.yaml`. This document does not declare v0.1 conformance or release readiness by itself.

## 1. Conformance language

The key words **MUST**, **MUST NOT**, **SHOULD**, **SHOULD NOT**, and **MAY** are normative when they appear in sections marked **Normative** or in canonical interaction requirements. Informative architecture, deployment guidance, reference flows and worked examples do not independently create normative DTG component semantics.

## 2. Scope and composition boundary — Normative

DPIP defines privacy requirements for **composed DTG interactions**. It does not redefine component-owned credential semantics, Trust Task protocol semantics, ZKP constructions, DID methods, wallet/VTA protocols, VTN governance, discovery protocols or transport mechanisms.

A DPIP implementation claim MUST identify the interaction being evaluated, the profile/claims being asserted, the participating component/deployment dependencies, the correlation surfaces considered, and the evidence supporting the result.

A component feature such as selective disclosure, pairwise identifiers or zero-knowledge proof support MUST NOT by itself be treated as proof of end-to-end DPIP privacy.

## 3. Privacy invariants — Normative

The v0.1 draft carries forward P1-P8 from `spec/dpip-concept.md` as stable identifiers. Their exact wording remains under v0.1 review; executable interaction requirements are authoritative for the current draft behavior.

- **P1 Data minimisation** — disclose no more than required for the trust purpose.
- **P2 Contextual unlinkability** — avoid mandatory reuse of stable identifiers across unrelated contexts.
- **P3 Selective provability** — permit predicate proof without unnecessary source-attribute disclosure where the decision depends only on the predicate.
- **P4 Compositional privacy** — composition MUST NOT silently introduce a correlator that defeats the claimed privacy property.
- **P5 Protocol-envelope privacy** — routing, endpoint, status, timing, session and transcript metadata are part of the privacy boundary.
- **P6 Storage minimisation** — retained state and privileged observability are part of the privacy result.
- **P7 Lifecycle privacy** — current draft baseline covers withdrawal/revocation; C5/RF-003 pressure-tests a refinement toward privacy-preserving lifecycle correctness across expiry, suspension, supersession, restoration and precedence. See `docs/p7-lifecycle-review.md`.
- **P8 User-visible disclosure context** — material recipient, purpose, disclosure and linkability consequences should be understandable at authorization time.

## 4. Privacy profiles — Normative draft

DPIP currently defines working profiles PP-1 through PP-5:

- **PP-1 Disclosure Minimised**
- **PP-2 Pairwise Private**
- **PP-3 Unlinkable Presentation**
- **PP-4 Composed Unlinkability**
- **PP-5 Adversarial Privacy**

A higher-numbered profile is not automatically appropriate for every deployment. A conformance claim MUST state the interaction and applicable profile/claim scope.

## 5. Scoped privacy claims — Normative

Privacy claims MUST identify the subject and scope being asserted. DPIP MUST NOT represent privacy as a single unscoped Boolean where different layers of the composed interaction have different results.

Current claim subjects include identifier, credential-half, relationship, presentation and contextual/graph privacy. A claim result is one of:

- `PASS`
- `FAIL`
- `CONSTRAINED`
- `INDETERMINATE`

Evidence supporting a narrower subject/scope MUST NOT be promoted into a broader privacy result without supporting evidence.

## 6. Correlation scope — Normative

Where material to a privacy claim, implementations SHOULD distinguish:

- **declared scope** — intended correlation posture;
- **observable scope** — where the value or equivalent signal is actually visible;
- **effective scope** — the correlation scope supported by the complete composition;
- **scope basis** — the evidence/reasoning explaining the effective scope.

Declared pairwise scope does not establish pairwise effective relationship or contextual privacy if other participating surfaces are public, retained or otherwise joinable.

## 7. Canonical interactions — Normative requirements in fixtures

The canonical YAML fixtures under `examples/` carry the detailed requirement/test identifiers for the current draft.

### C1 — Privacy-preserving personhood presentation

Tests whether a personhood predicate can be demonstrated without unnecessary identity/attribute disclosure or surrounding protocol correlation.

### C2 — Privacy-preserving relationship proof

Tests whether relationship semantics can be proven without an unnecessary durable relationship or holder binder.

### C3 — Cross-community asymmetric relationship proof

Tests asymmetric privacy postures across reciprocal relationship halves and prevents private-half proof evidence from being promoted into relationship/contextual unlinkability.

### C4 — Privacy-preserving policy discovery

Tests pre-flight admissibility/policy discovery before relationship establishment, including requester-handle reuse, endpoint/timing correlation, rejection logging and relationship-intent exposure.

### C5 — Privacy-preserving lifecycle evaluation and precedence

Tests separation of cryptographic validity, lifecycle state and composed decision precedence; status-query correlation; Trust Task freshness; and supersession/replacement history.

Future canonical interactions may address recovery/migration and additional discovery/routing/HTX cases.

## 8. Component and dependency ownership — Normative boundary

DPIP owns the **composition requirement and privacy conclusion**. Participating specifications own their respective semantics, interfaces and constructions.

When a DPIP requirement cannot be evaluated because a component does not expose the necessary semantics/interface/evidence, the result MUST remain failed, constrained or indeterminate as applicable. DPIP MUST NOT silently invent the missing component behavior.

Cross-specification responsibility mapping is maintained in `docs/component-responsibilities.md`.

## 9. Evidence model — Normative

A DPIP conformance result SHOULD identify:

- interaction and version;
- implementation/deployment identity and configuration scope;
- participating component/specification versions;
- test results;
- scoped privacy-claim results;
- evidence provenance;
- residual correlation and exceptions;
- unresolved assumptions/findings where material.

External evidence may be `candidate`, `verified` or otherwise maturity-scoped according to the evidence-binding model. Issue/discussion references may inform candidate evidence but MUST NOT be treated as immutable verified construction evidence by themselves.

## 10. Findings and regression — Normative process boundary

Reference-flow, implementation or adversarial findings may be recorded using the DPIP finding schema. A finding does not automatically become a normative DPIP requirement.

Stable findings may be reviewed and promoted to:

- DPIP requirements;
- positive/negative/adversarial tests;
- deployment guidance;
- upstream issues;
- accepted risks.

Resolved privacy failures SHOULD retain regression tests or evidence so the failure mode cannot silently return.

## 11. Reference composed systems — Informative

Reference flows under `reference-system/flows/` are non-normative integration hypotheses used to pressure-test DPIP before every DTG repository emits native DPIP metadata.

Current flows:

- **RF-001** relationship establishment and proof;
- **RF-002** pre-flight policy discovery;
- **RF-003** lifecycle privacy and precedence.

A passing reference flow means DPIP can evaluate the stated hypothesis. It does not make the assumed component behavior normative DTG behavior.

## 12. Deployment guidance — Informative

Implementation guidance lives under `docs/deployment-guide/`. Current material covers:

- RF-001 wallet/VTA, Trust Task envelope, proof/verifier, graph/storage and privileged observer handling;
- policy discovery;
- lifecycle/status and precedence.

Deployment guidance maps privacy objectives to dangerous patterns, applicable DPIP controls, expected evidence and negative-assurance questions.

## 13. Portfolio change impact — Normative process / informative registry

DPIP can map external repository changes to affected interactions, requirements, tests, claims and reference flows. An upstream change does not automatically create a DPIP failure; it can require revalidation, review or evidence refresh.

The machine-readable change-impact registry is the integration point for DTG portfolio monitoring.

## 14. Machine-readable artifacts — Normative formats

The repository currently provides schemas for:

- interaction profiles;
- conformance results;
- external evidence bindings;
- reference composed flows;
- findings;
- portfolio change impact.

CI validation ensures repository fixtures conform to these formats and selected semantic/traceability rules.

## 15. v0.1 readiness — Normative release gate

`readiness/v0.1.yaml` is authoritative for whether the draft can be promoted to a v0.1 release baseline.

At minimum, readiness requires that an implementer can:

1. select a canonical interaction;
2. identify the applicable profile and scoped privacy claims;
3. map dependencies to owning DTG specifications/deployment components;
4. execute or inspect the required tests;
5. attach provenance-bearing evidence with correct maturity/scope;
6. produce a machine-validated conformance result;
7. identify unresolved assumptions/findings rather than relying on undocumented architectural assumptions.

A v0.1 release MUST NOT be declared while the readiness artifact reports `not-ready`.

## 16. Informative architecture background

The original architectural reasoning, project evolution, initial roadmap and rationale remain available in `spec/dpip-concept.md`. As the v0.1 draft stabilizes, normative material should migrate into this document while historical/design explanation remains informative.
