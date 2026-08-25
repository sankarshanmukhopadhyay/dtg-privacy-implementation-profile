# DTG Component Privacy Responsibilities

This document establishes the initial responsibility split between DTG component specifications and the DTG Privacy-Preserving Implementation Profile (DPIP).

## Principle

DPIP does not take ownership of component semantics. It evaluates whether the composition of independently specified components preserves a claimed privacy property.

| Component area | Primary responsibility | DPIP composition concern |
|---|---|---|
| Credentials | Define claims, relationship semantics, bindings, status semantics, and what is intended to be provable | Whether required claim/binding design forces unnecessary disclosure or cross-context correlation |
| Trust Tasks | Define exchanges, messages, required evidence, and protocol behavior | Whether exchanges expose privacy-compatible proof inputs and avoid durable correlators in envelopes/transcripts |
| ZKP / selective disclosure | Define proof constructions, predicate semantics, composition, and verifier behavior | Whether the selected construction satisfies the interaction profile without leaking linking material |
| Relationship artifacts | Represent relationship state and context | Whether identifiers or references escape their intended scope or become reusable correlators |
| Agent naming / discovery | Name, locate, or route to agents/services | Whether discovery identifiers/endpoints become unintended global correlation handles |
| VTA / wallet | Manage keys, credentials, policy, interaction state, and storage | Context isolation, key separation, retention, telemetry, recovery, and policy enforcement |
| HTX / user interaction | Present trust interactions to people | Whether disclosure, purpose, recipient, and linkability consequences are intelligible at authorization time |
| DID / VC / crypto substrate | Provide underlying identifier, credential, cryptographic, and resolution capabilities | Whether concrete selections introduce privacy properties or failures not visible at the abstract DTG layer |
| DPIP | Define cross-component privacy invariants, interaction profiles, correlation analysis, and conformance evidence | Whether the complete interaction preserves its claimed privacy properties |

## Boundary rule

When an end-to-end privacy requirement cannot be satisfied because a component fails to expose necessary semantics, proof inputs, or privacy-safe interfaces, DPIP should record the failed composition requirement and identify the owning component specification. DPIP should not silently invent a replacement protocol requirement.

## Composition questions

For every component used in a DPIP interaction, an implementation assessment should answer:

1. What information does this component introduce?
2. Which values are stable, scoped, or ephemeral?
3. Which actors can observe those values?
4. What must later components bind to or prove about them?
5. Can that binding be achieved without disclosure of a durable cross-context correlator?
6. What state is retained after the interaction?
7. Which privacy invariant would fail if the component is configured differently?

These questions provide the first reusable handoff between specification analysis and implementation conformance.
