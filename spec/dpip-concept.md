# DTG Privacy-Preserving Implementation Profile: Concept and Architecture

Status: Development draft — initial architecture implemented

## 1. Purpose

The DTG Privacy-Preserving Implementation Profile (DPIP) defines how multiple Decentralized Trust Graph specifications and implementation components are composed into an end-to-end interaction while preserving explicit privacy properties.

The profile does not replace or duplicate the normative responsibilities of underlying DTG specifications. It defines requirements at their boundaries and across their composition.

## 2. Problem statement

Privacy properties are not necessarily compositional.

An implementation may use selective-disclosure credentials, unlinkable proof mechanisms, pairwise identifiers, privacy-aware Trust Tasks, and encrypted transports and still create an end-to-end correlation surface through identifiers, metadata, proof bindings, status mechanisms, storage behavior, timestamps, routing, or user interaction.

DPIP therefore evaluates privacy over the complete interaction rather than inferring end-to-end privacy from the properties of individual components.

## 3. Scope

DPIP covers privacy-relevant composition between, at minimum:

- DTG credential and relationship artifacts;
- Trust Task exchanges;
- zero-knowledge and selective-disclosure proof constructions;
- subject, relationship, community, agent, and VTA identifiers;
- wallet or VTA behavior;
- status, revocation, withdrawal, and recovery mechanisms;
- transport and session metadata;
- user-facing disclosure and consent interactions;
- retained state and audit evidence.

DPIP is intended to remain neutral to a particular DID method, ZKP construction, transport protocol, wallet implementation, or deployment topology except where an implementation choice makes a required privacy property impossible.

## 4. Non-goals

DPIP does not:

- define new credential semantics where the credential specification already owns them;
- define a new ZKP protocol;
- define a new DID method;
- replace Trust Task protocol specifications;
- prescribe maximum anonymity for every DTG interaction;
- assume that all legitimate interactions have identical privacy requirements.

## 5. Unit of conformance

The primary unit of DPIP conformance is a **composed interaction**.

A composed interaction is an end-to-end execution involving one or more DTG components for a defined trust purpose, with identified actors, information flows, correlation surfaces, privacy requirements, and observable evidence.

An implementation SHALL NOT claim a DPIP privacy property solely because every individual component used in an interaction advertises a compatible privacy feature.

## 6. Initial privacy invariants

### P1 — Data minimisation

An interaction MUST NOT disclose information beyond what is required to evaluate the trust purpose and any explicitly declared operational requirements.

### P2 — Contextual unlinkability

An implementation MUST NOT require a stable subject or relationship identifier to be reused across contexts unless cross-context linkability is an explicit and justified semantic requirement of the interaction.

### P3 — Selective provability

Where a trust decision depends upon a predicate rather than the underlying attribute value, the composition SHOULD permit the predicate to be proven without disclosure of unnecessary source attributes.

### P4 — Compositional privacy

Combining credentials, proofs, relationship artifacts, or Trust Task evidence MUST NOT silently introduce a correlator that defeats the privacy properties claimed for the constituent components.

### P5 — Protocol-envelope privacy

Identifiers, endpoints, routing metadata, nonces, session state, timestamps, status checks, or transcript structure MUST NOT negate the privacy property claimed for the interaction.

### P6 — Storage minimisation

Participants MUST retain no more interaction data than is necessary for explicitly stated operational, security, accountability, or legal purposes. Retention that creates a new correlation capability MUST be identified as part of the privacy analysis.

### P7 — Withdrawal and revocation without unnecessary exposure

Withdrawal, relationship termination, credential status, and revocation mechanisms MUST avoid requiring disclosure of unrelated identity or relationship information where a less revealing mechanism can satisfy the requirement.

### P8 — User-visible disclosure context

Before a user authorizes a privacy-relevant interaction, the implementation SHOULD make materially significant disclosure, recipient, purpose, and linkability consequences understandable at the interaction boundary.

## 7. Component responsibility model

DPIP distinguishes between component ownership and composition ownership.

- Credential specifications define the semantics of claims and what must be provable.
- Trust Task specifications define exchange behavior and must expose sufficient privacy-compatible evidence and bindings for required proofs.
- ZKP specifications define private proof constructions and verifier semantics.
- Relationship artifacts define relationship semantics without unnecessarily expanding their correlation scope.
- Agent naming, discovery, and VTA interfaces must avoid turning routing or service identifiers into unintended global correlators.
- Wallet/VTA implementations enforce context separation, key handling, storage minimisation, and interaction policy.
- Human Trust Experience guidance provides the user-facing disclosure and authorization boundary.
- DPIP defines whether the resulting composition preserves the claimed end-to-end privacy property.

Requirement ownership and evidence ownership are distinct. DPIP may own an end-to-end requirement while depending on another DTG specification for the semantics, interface, or construction evidence necessary to evaluate it. The detailed traceability model is maintained in `docs/component-responsibilities.md`.

## 8. Correlation-surface model

Every conforming interaction profile SHOULD identify potentially correlatable values, including:

- credential identifiers;
- subject identifiers;
- issuer and verifier identifiers;
- DIDs and DID service endpoints;
- relationship and community identifiers;
- R-Card or equivalent relationship references;
- agent names and VTA identifiers;
- proof identifiers, commitments, holder bindings, and nonces;
- status and revocation endpoints;
- network, transport, and session metadata;
- timestamps and repeated temporal patterns;
- Trust Task transcript artifacts;
- repeated attribute combinations;
- device or wallet identifiers;
- retained audit or telemetry records.

For each value, an implementation profile SHOULD record:

1. who can observe it;
2. the scope over which it is stable;
3. whether it can be joined with another observation;
4. whether such joining is required, allowed, or prohibited;
5. the mitigation or justification when it creates a correlation surface.

The canonical interaction schema implements these fields for executable profiles.

## 9. Initial conformance profiles

DPIP initially defines the following profile levels as working categories. Their names and precise requirements may change as implementation evidence develops.

### PP-1 — Disclosure Minimised

The interaction demonstrates explicit data minimisation and avoids unnecessary attribute disclosure.

### PP-2 — Pairwise Private

The interaction additionally avoids mandatory cross-relying-party stable subject identifiers unless explicitly required by the interaction semantics.

### PP-3 — Unlinkable Presentation

The interaction additionally prevents ordinary presentation-to-presentation linkage through protocol-mandated identifiers or proof values.

### PP-4 — Composed Unlinkability

The interaction additionally preserves unlinkability when multiple DTG credentials, relationship artifacts, Trust Tasks, or proofs are combined.

### PP-5 — Adversarial Privacy

The interaction additionally addresses stronger metadata, transcript, verifier-collusion, storage, and inference threats defined by its threat model.

Higher-numbered profiles are not automatically appropriate for every deployment. A conformance claim MUST state the interaction and profile to which the claim applies.

## 10. Initial canonical interactions

### C1 — Privacy-preserving personhood presentation

A holder demonstrates a required personhood predicate to a verifier without unnecessary disclosure of identity or unrelated credential attributes.

### C2 — Privacy-preserving relationship proof

A holder demonstrates a required relationship predicate using one or more credential or relationship artifacts without exposing unrelated relationship information or introducing an unnecessary reusable relationship identifier.

### C3 — Cross-community asymmetric relationship proof

A holder demonstrates a relationship whose two relevant identities or relationship contexts are intentionally distinct across communities or domains. The proof must preserve the legitimate distinction between those contexts and MUST NOT require their collapse onto a common durable identifier merely to bind the proof.

C3 is an initial pressure test for P4 Compositional Privacy and for scoped privacy claims. Identifier, credential-half, relationship, presentation, and contextual/graph privacy may legitimately have different results for the same interaction.

## 11. Negative-test model

DPIP conformance includes tests that attempt to disprove claimed privacy properties.

Example:

> Given a holder who proves personhood to Verifier X and subsequently proves a relationship predicate to Verifier Y, X and Y must not be able to correlate the two presentations using a stable identifier or cryptographic value required by the DPIP interaction profile unless that correlation is explicitly part of the interaction semantics.

Negative cases may originate from specification review, implementation experience, RAHP pressure testing, security/privacy analysis, or discovered interoperability failures.

A sufficiently stable negative case SHOULD be promoted from prose into machine-readable conformance evidence. C1-C3 now include positive, negative, and/or adversarial vectors in the canonical interaction fixtures.

## 12. Conformance evidence

A DPIP conformance claim identifies, as applicable:

- interaction identifier and version;
- profile level;
- participating DTG specifications and versions;
- implementation components and relevant configuration;
- privacy invariants claimed;
- scoped privacy claims and their subjects;
- identified correlation surfaces;
- normative assertions tested;
- positive test evidence;
- negative/adversarial test evidence;
- known exceptions and justified linkability;
- result and evidence provenance.

The project provides machine-readable interaction and conformance-result schemas, validation tooling, and automated repository checks. Conformance results MUST NOT upgrade a narrower privacy result into a broader claim without supporting evidence.

## 13. Relationship to RAHP

RAHP-style analysis is an input to DPIP conformance design, not a substitute for it.

RAHP may identify harms, adversarial compositions, correlation surfaces, hidden assumptions, or cross-specification failure modes. DPIP can then promote sufficiently well-scoped findings into:

1. a privacy invariant or refinement;
2. an interaction requirement;
3. a negative conformance case;
4. a machine-readable test vector;
5. regression evidence.

This provides a feedback loop from adversarial review to implementation assurance.

## 14. Evolution model

DPIP evolves independently of the release cadence of individual DTG components while recording the specification versions and evidence sources against which an interaction profile has been validated.

Changes in an underlying specification SHOULD be assessed for impact on:

- privacy invariants;
- component boundaries;
- correlation surfaces;
- canonical interactions;
- scoped privacy claims;
- conformance assertions;
- executable tests;
- external evidence bindings.

This creates a natural integration point with portfolio monitoring and cross-repository assurance tooling.

## 15. Implementation status and next work

The original architecture roadmap has now produced an executable initial baseline.

| Initial increment | Status | Current artifact |
|---|---|---|
| Formalize component responsibility boundaries | Implemented | `docs/component-responsibilities.md` and Section 7 |
| Formalize correlation-surface taxonomy | Implemented baseline | `docs/correlation-surfaces.md`, Section 8, and interaction fixtures |
| Define machine-readable interaction/profile schema | Implemented | `schema/interaction-profile.schema.json` |
| Produce C1-C3 worked interaction cases | Implemented | canonical YAML fixtures under `examples/` |
| Add negative tests for composed-presentation correlation | Implemented baseline | C1-C3 test vectors, including C3 asymmetric/privacy-scope cases |
| Map requirements to current DTG specifications without hard-coding unstable constructions | Implemented baseline | cross-specification traceability in `docs/component-responsibilities.md` |
| Define first executable conformance evidence format | Implemented | conformance-result schema, example result, validator, and CI |

### 15.1 Next-phase priorities

The next phase moves DPIP from an executable concept baseline toward a versioned implementation profile suitable for external implementer use.

1. **Cross-repository evidence binding.** Define a machine-readable way for a DPIP conformance result to reference versioned evidence owned by another DTG repository while recording provenance and the exact claim that evidence supports.
2. **Construction-aware, construction-neutral evidence.** Permit concrete ZKP/selective-disclosure evidence to be attached to a profile without making one construction normative. C3 should use `dtgwg-zkp-tf#13` and subsequent artifacts as an early pressure test.
3. **Evidence-to-claim sufficiency rules.** Extend automated validation beyond syntactic traceability so that evidence for identifier or credential-half privacy cannot be silently promoted to relationship, presentation, or contextual privacy.
4. **Deployment profiles and implementation guidance.** Add deployer-facing guidance for wallet/VTA behaviour, Trust Task envelopes, status/revocation, storage, telemetry, discovery, VTN context, and HTX privacy consequences.
5. **Portfolio change-impact analysis.** Define machine-readable links from DTG repository/specification versions to affected DPIP invariants, interactions, requirements, tests, and evidence records so portfolio monitoring can identify privacy-relevant drift.
6. **Additional canonical interactions.** Add recovery/migration, withdrawal/revocation, discovery/routing, and other interactions where privacy can fail outside the credential proof itself.
7. **Adversarial regression pipeline.** Establish a repeatable path from RAHP or implementation findings to candidate negative tests, reviewed conformance vectors, and retained regression evidence.
8. **v0.1 specification baseline.** Promote the concept document into a coherent versioned specification once the evidence-binding model and deployer guidance are sufficiently stable.

### 15.2 Readiness criterion for v0.1

DPIP should be considered ready for a v0.1 specification baseline when an implementer can select a canonical interaction, identify the applicable privacy profile and scoped claims, map each dependency to an owning DTG specification or deployment component, execute or inspect the required tests, attach provenance-bearing evidence, and produce a machine-validated conformance result without relying on undocumented architectural assumptions.
