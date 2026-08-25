# DPIP Conformance Model

DPIP conformance applies to a declared **interaction profile**, not to a product in the abstract.

## Conformance claim

A useful claim should identify:

- the DPIP version;
- the interaction identifier and version;
- the privacy profile claimed;
- participating DTG specifications and versions;
- implementation components and relevant configuration;
- privacy invariants covered;
- correlation surfaces assessed;
- normative assertions evaluated;
- positive test results;
- negative or adversarial test results;
- justified exceptions and required linkability;
- evidence provenance.

A generic statement such as “DPIP compliant” is insufficient unless it is accompanied by the interaction and profile scope.

## Evidence layers

DPIP should mature through four evidence layers.

### E1 — Narrative analysis

Human-readable rationale explains the interaction, data flows, trust purpose, privacy invariants, and known correlation surfaces.

### E2 — Structured assertions

The interaction, invariants, surfaces, requirements, and expected outcomes are represented in machine-readable form.

### E3 — Executable tests

Positive and negative cases can be run against an implementation or implementation fixture.

### E4 — Reproducible conformance evidence

Test inputs, outputs, implementation/version metadata, results, and provenance can be reproduced and independently inspected.

## Positive and negative evidence

Positive evidence demonstrates that the required trust interaction succeeds with the permitted disclosure and binding behavior.

Negative evidence attempts to disprove the privacy claim. Examples include:

- correlating two presentations using a mandated stable identifier;
- joining separately private credentials through a common holder binding;
- extracting relationship context from a Trust Task transcript;
- correlating presentations through status-check behavior;
- demonstrating that recovery or migration silently changes identifier scope;
- showing that retained telemetry reconstructs relationships that the protocol otherwise hides.

A privacy claim is materially stronger when the corresponding negative cases have been exercised.

## Initial profile ladder

The initial working ladder is:

- **PP-1 Disclosure Minimised**
- **PP-2 Pairwise Private**
- **PP-3 Unlinkable Presentation**
- **PP-4 Composed Unlinkability**
- **PP-5 Adversarial Privacy**

These are capability profiles rather than maturity scores. A deployment should claim only the level that is appropriate and evidenced for a given interaction.

## Exceptions

Some interactions legitimately require persistence or linkability. DPIP does not prohibit this by default.

An exception should be explicit and should state:

1. what value is linkable;
2. who can perform the linkage;
3. across which contexts;
4. why the linkage is required;
5. which invariant is constrained;
6. whether a less linkable design was considered;
7. what controls limit secondary use.

Undeclared linkability is a conformance defect. Declared and justified linkability is an architectural property to be evaluated.

## Change impact

When an underlying DTG specification changes, existing DPIP claims should be re-evaluated where the change affects:

- values exposed at a component boundary;
- proof or holder-binding semantics;
- identifier scope;
- status/revocation behavior;
- Trust Task envelopes or transcript structure;
- wallet/VTA retention or recovery behavior;
- user-visible disclosure semantics.

This model is intended to support automated impact signals from portfolio-monitoring tooling as the project matures.
