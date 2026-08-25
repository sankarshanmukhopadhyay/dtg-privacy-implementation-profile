# DTG Component Privacy Responsibilities

This document establishes the responsibility split between DTG component specifications and the DTG Privacy-Preserving Implementation Profile (DPIP), and provides the first cross-specification privacy traceability matrix.

## Principle

DPIP does not take ownership of component semantics. It evaluates whether the composition of independently specified components preserves a claimed privacy property.

A DPIP requirement may therefore depend on evidence owned elsewhere. **Requirement ownership** and **evidence ownership** are distinct: DPIP owns the end-to-end claim and its scope; the relevant component specification owns the semantics, interfaces, or construction evidence needed to support that claim.

## Responsibility model

| Component area | Primary responsibility | DPIP composition concern |
|---|---|---|
| Credentials | Define claims, relationship semantics, bindings, status semantics, and what is intended to be provable | Whether required claim/binding design forces unnecessary disclosure or cross-context correlation |
| Trust Tasks | Define exchanges, messages, required evidence, and protocol behavior | Whether exchanges expose privacy-compatible proof inputs and avoid durable correlators in envelopes/transcripts |
| ZKP / selective disclosure | Define proof constructions, predicate semantics, composition, and verifier behavior | Whether the selected construction satisfies the interaction profile without leaking linking material |
| Relationship artifacts | Represent relationship state and context | Whether identifiers or references escape their intended scope or become reusable correlators |
| Agent naming / discovery / R-Cards | Name, locate, describe, or route to agents/services/relationship context | Whether discovery identifiers, endpoints, or references become unintended global correlation handles |
| VTA / wallet / key handling | Manage keys, credentials, policy, interaction state, recovery, and storage | Context isolation, key separation, retention, telemetry, recovery, and policy enforcement |
| HTX / user interaction | Present trust interactions to people | Whether disclosure, purpose, recipient, and linkability consequences are intelligible at authorization time |
| VTN / trust context | Establish deployment/community trust-policy and anchoring context | Whether trust-context disclosure creates correlation and whether proof success is incorrectly treated as evidence of policy or anchoring facts |
| DID / VC / crypto substrate | Provide underlying identifier, credential, cryptographic, status, and resolution capabilities | Whether concrete selections introduce privacy properties or failures not visible at the abstract DTG layer |
| RAHP / adversarial assurance | Identify harms, hidden assumptions, unsafe compositions, and pressure-test cases | Whether stable findings should become DPIP negative tests or regression evidence |
| Portfolio monitoring | Observe changes across independently evolving specifications and implementations | Whether a component change invalidates a DPIP assumption, profile, test, or evidence binding |
| DPIP | Define cross-component privacy invariants, interaction profiles, scoped claims, correlation analysis, and conformance evidence | Whether the complete interaction preserves only the privacy properties actually supported by the complete evidence set |

## Cross-specification privacy traceability

This matrix is deliberately construction-neutral. Repository/specification names identify evidence or responsibility sources; they do not freeze DPIP to a particular cryptographic construction or unstable draft interface.

| Area / source | DPIP depends on | DPIP owns | Invariants | Initial interactions | Boundary / unresolved work |
|---|---|---|---|---|---|
| DTG Credentials / relationship semantics | Claim semantics; credential-half and relationship bindings; status semantics; definition of what must be provable | Disclosure and correlation consequences of using those semantics in a composed interaction | P1, P2, P3, P4, P7 | C1, C2, C3 | If required semantics force disclosure of a durable correlator, the credential/relationship layer must expose a privacy-compatible alternative or DPIP records non-conformance |
| DTG Trust Tasks | Exchange semantics; required evidence; message/envelope fields; proof-input interfaces | End-to-end assessment of whether the exchange reintroduces correlation through envelope, transcript, or binding data | P2, P4, P5, P6 | C1, C2, C3 | Exact privacy-compatible binding interface remains owned by Trust Tasks and the relevant proof layer |
| `dtgwg-zkp-tf` | Predicate constructions; hidden-binding behaviour; verifier semantics; construction-specific limitations and evidence | Scope of the resulting end-to-end privacy claim; rejection of claim overreach | P2, P3, P4 | C1, C2, C3 | Construction selection remains external. `dtgwg-zkp-tf#13` is evidence input for C3 asymmetric relationship cases, not normative DPIP semantics |
| VTA / wallet / key handling | Key isolation; holder binding; credential/proof orchestration; recovery; local policy and storage behaviour | Requirements on context separation, retention, telemetry, and disclosure consequences | P2, P4, P5, P6, P7, P8 | C1, C2, C3 | Concrete wallet/VTA conformance evidence is still to be profiled |
| HTX | User-facing interaction semantics and authorization experience | Whether material disclosure, recipient, purpose, and linkability consequences are represented at the composed-interaction boundary | P1, P8 | C1, C2, C3 | Need implementation evidence for privacy consequence presentation rather than generic consent |
| R-Cards / naming / discovery | Relationship/discovery references, service identifiers, endpoints, and routing semantics | Correlation-surface classification and end-to-end impact | P2, P4, P5 | C2, C3 | Determine which identifiers are intentionally public, pairwise, relationship-scoped, or ephemeral |
| VTN / trust context | Community/deployment anchoring and policy semantics | Separation of proof validity from trust-context and privacy claims | P2, P4, P5 | C2, C3 | C3 explicitly permits same-VTN, cross-VTN, and unanchored variants; proof success MUST NOT imply common anchoring or policy acceptance |
| DID / VC / status substrate | Identifier, resolution, credential, status and cryptographic capabilities selected by a deployment | Identification of substrate-induced correlation surfaces and exceptions | P1, P2, P4, P5, P7 | C1, C2, C3 | Method/mechanism-specific analysis belongs in deployment evidence rather than the core DPIP profile |
| RAHP | Adversarial findings and cross-spec pressure tests | Promotion of stable findings into requirements, negative tests, and regression evidence | P1-P8 as applicable | C1, C2, C3 and future cases | Maintain provenance from finding to promoted DPIP test |
| Portfolio monitor | Specification/repository versions and change signals | Impact mapping from upstream change to affected DPIP interaction, invariant, requirement, test, or evidence record | P1-P8 as applicable | All | Machine-readable change-impact binding is next-phase work |

## C1-C3 evidence boundary

### C1 — Privacy-preserving personhood presentation

DPIP requires evidence that the required personhood predicate can be established without unnecessary identity/attribute disclosure and without the surrounding exchange introducing a reusable correlator. Credential semantics define what is being proven; the proof layer establishes the predicate; Trust Tasks and wallet/VTA behaviour determine whether the surrounding presentation preserves the claim.

### C2 — Privacy-preserving relationship proof

DPIP requires evidence that relationship semantics can be established without an unnecessary durable relationship or holder binder. Relationship/credential specifications own the semantics; proof constructions own private binding behaviour; DPIP owns the conclusion about composed unlinkability.

### C3 — Cross-community asymmetric relationship proof

DPIP independently evaluates identifier, credential-half, relationship, presentation, and contextual/graph privacy. Construction evidence such as the cases developed under `sankarshanmukhopadhyay/dtgwg-zkp-tf#13` may demonstrate that a private half or reciprocal binding is cryptographically protected. DPIP does not infer from that evidence that the complete relationship or graph context is unlinkable, nor that both halves share a VTN or trust-policy context.

## Boundary rule

When an end-to-end privacy requirement cannot be satisfied because a component fails to expose necessary semantics, proof inputs, or privacy-safe interfaces, DPIP records the failed composition requirement and identifies the owning component specification. DPIP does not silently invent a replacement protocol requirement.

Likewise, when a component supplies valid evidence for a narrower property, DPIP MUST NOT upgrade that evidence into a broader privacy claim. Proof success, credential-half hiding, or pairwise identifiers are inputs to an end-to-end conclusion, not substitutes for one.

## Composition questions

For every component used in a DPIP interaction, an implementation assessment should answer:

1. What information does this component introduce?
2. Which values are stable, scoped, or ephemeral?
3. Which actors can observe those values?
4. What must later components bind to or prove about them?
5. Can that binding be achieved without disclosure of a durable cross-context correlator?
6. What state is retained after the interaction?
7. Which privacy invariant would fail if the component is configured differently?
8. Which specification owns the semantic or construction evidence needed for this conclusion?
9. Does the evidence support the exact subject and scope of the privacy claim being made?

These questions provide the reusable handoff between specification analysis, implementation conformance, and cross-repository evidence.