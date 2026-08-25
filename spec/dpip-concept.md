# DTG Privacy-Preserving Implementation Profile: Concept and Architecture

Status: Initial development draft

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

C3 is an initial pressure test for P4 Compositional Privacy.

## 11. Negative-test model

DPIP conformance should include tests that attempt to disprove claimed privacy properties.

Example:

> Given a holder who proves personhood to Verifier X and subsequently proves a relationship predicate to Verifier Y, X and Y must not be able to correlate the two presentations using a stable identifier or cryptographic value required by the DPIP interaction profile unless that correlation is explicitly part of the interaction semantics.

Negative cases may originate from specification review, implementation experience, RAHP pressure testing, security/privacy analysis, or discovered interoperability failures.

A sufficiently stable negative case SHOULD be promoted from prose into machine-readable conformance evidence.

## 12. Conformance evidence

A DPIP conformance claim should eventually identify:

- interaction identifier and version;
- profile level;
- participating DTG specifications and versions;
- implementation components and relevant configuration;
- privacy invariants claimed;
- identified correlation surfaces;
- normative assertions tested;
- positive test evidence;
- negative/adversarial test evidence;
- known exceptions and justified linkability;
- result and evidence provenance.

The project should progressively move from narrative evidence to structured fixtures and executable tests while retaining human-readable rationale.

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

DPIP should evolve independently of the release cadence of individual DTG components while recording the specification versions against which an interaction profile has been validated.

Changes in an underlying specification SHOULD be assessed for impact on:

- privacy invariants;
- component boundaries;
- correlation surfaces;
- canonical interactions;
- conformance assertions;
- executable tests.

This creates a natural integration point with portfolio monitoring and cross-repository assurance tooling.

## 15. Next work

The next development increments should:

1. formalize component responsibility boundaries;
2. formalize the correlation-surface taxonomy;
3. define a machine-readable interaction/profile schema;
4. produce the three initial worked interaction cases;
5. add negative tests for composed-presentation correlation;
6. map requirements to current DTG specifications without hard-coding unstable construction details;
7. define the first executable conformance evidence format.
