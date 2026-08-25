# Correlation-Surface Taxonomy

A privacy-preserving DTG interaction must account for more than disclosed credential attributes. Correlation can arise from any value or observable behavior that remains sufficiently stable to join observations across interactions, actors, or contexts.

## Assessment dimensions

For each potentially correlatable value, record:

- **observer** — which actor or infrastructure component can observe it;
- **scope** — the operational context in which the surface exists, such as session, relationship, relying party, community, issuer, deployment, or global;
- **correlation scope** — the declared, observable, and effective correlation posture described below;
- **stability** — ephemeral, rotating, long-lived, or permanent;
- **joinability** — whether another observation can be linked using the value directly or probabilistically;
- **necessity** — whether that linkability is required by the trust purpose;
- **mitigation** — isolation, derivation, rotation, blinding, minimisation, deletion, or another control;
- **residual risk** — known correlation capability that remains after mitigation.

## Declared, observable, and effective correlation scope

DPIP distinguishes three scope concepts because a value's intended privacy posture is not necessarily the privacy posture of the composed interaction.

- **declared scope** records the correlation posture intended or asserted by the owning component, holder, policy, or deployment. DPIP does not prescribe the vocabulary used by the owning DTG specification.
- **observable scope** records where the value, an equivalent signal, or information sufficient to join observations is actually visible.
- **effective scope** records the correlation posture supported after the surface is composed with the other observables participating in the interaction.
- **scope basis** records the evidence or reasoning for a difference between these scopes.

A declared pairwise identifier can therefore remain pairwise as an identifier while the relationship containing it has a broader effective correlation scope because the reciprocal half is public or surrounding graph data is observable. A narrow result for one privacy subject MUST NOT be silently promoted to a narrow result for another subject.

This model is intentionally independent of whether the Credential specification adopts a particular identifier taxonomy or declared-scope vocabulary. The asymmetric relationship pressure test in `sankarshanmukhopadhyay/dtgwg-zkp-tf#13` is the initial cross-specification reference for the distinction.

## Initial surface classes

### Identity surfaces

- subject identifiers;
- DIDs and DID URLs;
- issuer and verifier identifiers;
- community identifiers;
- agent names;
- VTA or wallet identifiers;
- device identifiers.

### Relationship surfaces

- relationship credential identifiers;
- R-Card or equivalent references;
- pairwise identifiers reused beyond their intended context;
- relationship status handles;
- delegation identifiers.

### Proof surfaces

- holder bindings;
- commitments;
- proof identifiers;
- nonces or challenges reused improperly;
- signature or proof values with unintended stability;
- disclosed attribute combinations that become quasi-identifiers.

### Protocol-envelope surfaces

- Trust Task message identifiers;
- endpoints;
- routing handles;
- session identifiers;
- status and revocation URLs;
- transport metadata;
- network-level observables.

### Temporal surfaces

- high-resolution timestamps;
- repeated timing patterns;
- synchronized status checks;
- issuance/presentation timing relationships.

### Persistence surfaces

- audit records;
- telemetry;
- logs;
- cached resolutions;
- retained transcripts;
- backup and recovery artifacts.

## Correlation record

A structured surface can express both its operational scope and its privacy/correlation posture:

```yaml
id: C3-CS-2
class: identity
value: private_half_identifier
observers: [wallet_vta]
scope: relationship
correlation_scope:
  declared_scope: pairwise
  observable_scope: pairwise
  effective_scope: pairwise
stability: relationship-scoped
joinability: must not become cross-context joinable
necessity: required within the relationship context
mitigation: hidden or presentation-scoped binding
residual_risk: construction-dependent
invariants: [P2, P4]
```

When the scopes diverge, `scope_basis` is required:

```yaml
correlation_scope:
  declared_scope: pairwise
  observable_scope: pairwise
  effective_scope: publicly-correlatable-relationship
  scope_basis: reciprocal public half and public graph make the relationship joinable without exposing the private identifier itself
```

## Key rules

A value does not become privacy-safe merely because it contains no human-readable personal data. Cryptographic values, endpoints, opaque identifiers, and metadata are correlation surfaces when they permit observations to be joined.

Likewise, declared scope is evidence about intended treatment, not proof of effective privacy. DPIP evaluates effective privacy from the complete set of materially observable surfaces.