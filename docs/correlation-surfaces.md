# Correlation-Surface Taxonomy

A privacy-preserving DTG interaction must account for more than disclosed credential attributes. Correlation can arise from any value or observable behavior that remains sufficiently stable to join observations across interactions, actors, or contexts.

## Assessment dimensions

For each potentially correlatable value, record:

- **observer** — which actor or infrastructure component can observe it;
- **scope** — session, relationship, relying party, community, issuer, deployment, or global;
- **stability** — ephemeral, rotating, long-lived, or permanent;
- **joinability** — whether another observation can be linked using the value directly or probabilistically;
- **necessity** — whether that linkability is required by the trust purpose;
- **mitigation** — isolation, derivation, rotation, blinding, minimisation, deletion, or another control;
- **residual risk** — known correlation capability that remains after mitigation.

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

A worked interaction should eventually express each relevant surface in a structured record similar to:

```yaml
surface_id: CS-001
value: holder_binding
observer:
  - verifier
scope: relying-party
stability: long-lived
joinability: direct
necessity: prohibited
mitigation: pairwise-or-presentation-scoped-binding
residual_risk: none-known
invariants:
  - P2
  - P4
```

The exact machine-readable schema is intentionally deferred until the first worked interactions establish which fields are genuinely useful.

## Key rule

A value does not become privacy-safe merely because it contains no human-readable personal data. Cryptographic values, endpoints, opaque identifiers, and metadata are correlation surfaces when they permit observations to be joined.
