# Understanding DPIP

DPIP answers a simple question:

> **When several DTG components are used together, does the resulting interaction preserve the privacy properties we intended?**

A component can be privacy-capable on its own and still participate in a composed system that leaks, correlates, or retains more information than intended. DPIP examines the whole interaction rather than awarding privacy by inheritance from individual components.

## The mental model

```text
DTG interaction
      ↓
What privacy property is expected?
      ↓
What information or correlation is actually observable?
      ↓
Does the complete interaction satisfy the expectation?
      ↓
Evidence + scoped DPIP result
```

DPIP does not ask whether a credential format, DID method, proof system, wallet, Trust Task, transport, or registry is "private" in the abstract. It asks what happens when those things are combined for a particular purpose and observed by particular parties.

## A concrete example

Suppose two presentations use different pairwise identifiers. Looking only at those identifiers, the presentations appear unlinkable.

Now suppose the surrounding exchange reuses the same account identifier, task identifier, device telemetry value, operator lookup key, or graph edge. An observer able to see that value can join the presentations even though the pairwise identifiers themselves are different.

That reusable value is a **correlation surface**. DPIP records who can observe it and how far the effective correlation can extend.

This is why DPIP distinguishes:

- **declared scope** — the correlation the design says should exist;
- **observable scope** — what a particular observer can actually see;
- **effective scope** — how far those observations allow contexts to be joined in practice.

## What DPIP examines

The canonical interactions give recurring privacy questions stable identifiers. In ordinary language:

| Interaction | Human question |
| --- | --- |
| C1 | Can a person prove what is needed without unnecessarily revealing or reusing identity information? |
| C2 | Can a relationship be proven without exposing more of the relationship or its participants than necessary? |
| C3 | Can an asymmetric/cross-community relationship be proven without turning private relationship information into a durable cross-context correlator? |
| C4 | Can policy or trust information be discovered without unnecessarily revealing who is asking, what they hold, or what they intend to do? |
| C5 | Can status, lifecycle and precedence be evaluated without creating unnecessary historical or cross-context linkage? |
| C6 | Can recovery or migration preserve necessary continuity without collapsing previously separate contexts into a durable recovery index? |

A **reference flow** (RF-xxx) then composes relevant components into an end-to-end scenario. It is the whole-system pressure test, not a new DTG protocol.

## How an examination works

A useful DPIP examination follows five steps.

### 1. State the privacy expectation

The examination identifies the interaction, reference flow, privacy claims and invariants that matter. The claim is scoped: privacy for whom, against which observer, in which context, and for which information.

### 2. Observe the implementation

DPIP records implementation evidence rather than assuming that specification intent equals deployed behavior. Evidence may include protocol envelopes, identifiers, proof inputs/outputs, stored mappings, graph state, logs, telemetry, operator-visible indexes and configuration.

### 3. Try to break the privacy expectation

Negative and adversarial tests deliberately attempt joins and disclosures that the privacy claim says should not be possible. A failed privacy test is useful evidence; DPIP is an assurance mechanism, not a green-badge generator.

### 4. Produce a scoped result

A result may show that an expectation is met, not met, limited by residual correlation, outside the scope of the examination, or impossible to decide with available evidence.

### 5. Record what should happen next

The disposition can call for a regression test, upstream clarification, implementation change, additional evidence, or acceptance of a documented limitation. DPIP should identify the boundary precisely without silently rewriting the component specification that owns it.

## Reading a DPIP result

Start with the plain-language summary when one is present. It is intended to answer three questions:

1. **What did DPIP find?**
2. **Why does that matter?**
3. **What should someone do about it?**

Then use the formal fields for auditability, automation and exact scope.

Typical formal outcomes should be understood as follows:

| Formal outcome | Plain-language meaning |
| --- | --- |
| PASS / SATISFIED | The tested privacy expectation is supported by the available evidence for the stated scope. |
| FAIL | The tested privacy expectation is not met for the stated scope. |
| CONSTRAINED | Some intended privacy is present, but an important limitation or residual correlation remains. |
| INDETERMINATE | The question is relevant, but there is not enough reliable evidence to decide. |
| NOT_APPLICABLE | The referred change or question does not affect the DPIP scope being examined. |

`INDETERMINATE` is not a failure and `CONSTRAINED` is not a pass. Both communicate useful assurance information that would be lost in a binary result.

## Evidence maturity matters

A discussion, issue or design hypothesis can identify a plausible privacy concern, but it does not establish implementation behavior. DPIP therefore distinguishes candidate evidence from stronger evidence such as commit-pinned implementations, generated traces, test vectors, configuration snapshots and immutable artifacts.

A precise `INDETERMINATE` result is preferable to converting an upstream hypothesis into an unsupported privacy conclusion.

## DPIP in the portfolio assurance loop

```text
DTG Portfolio Monitor
        ↓
What changed?
        ↓
RAHP
What could go wrong?
        ↓
DPIP referral when warranted
        ↓
What privacy property does the composed system actually preserve?
        ↓
DPIP result and disposition
        ↓
RAHP / owning specification / regression evidence
```

The roles are intentionally different. The Portfolio Monitor detects change. RAHP identifies plausible risk. DPIP performs the scoped privacy examination. The specification or implementation owner decides how an identified gap should be remediated.

## Where to go next

- [`../README.md`](../README.md) — repository orientation and current status.
- [`../spec/dpip-v0.1-draft.md`](../spec/dpip-v0.1-draft.md) — structured implementation specification.
- [`../examples/`](../examples/) — machine-readable canonical interactions and tests.
- [`../reference-system/`](../reference-system/) — composed reference flows, findings and implementation-backed run material.
- [`deployment-guide/`](deployment-guide/) — deployer-facing implementation guidance.
- [`rahp-return-operations.md`](rahp-return-operations.md) — operational RAHP ↔ DPIP return contract.
