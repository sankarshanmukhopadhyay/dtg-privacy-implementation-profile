# DTG Privacy-Preserving Implementation Profile

**DPIP answers a simple question: when several DTG components are used together, does the resulting interaction preserve the privacy properties we intended?**

A credential, proof system, pairwise identifier or Trust Task can be privacy-capable on its own while the complete interaction still exposes a reusable identifier, graph relationship, operator lookup key, telemetry value or other correlation surface. DPIP therefore evaluates privacy over the **composed DTG interaction**, not by inference from individual components.

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

## Start here

If DPIP is new to you, begin with [`docs/understanding-dpip.md`](docs/understanding-dpip.md). It explains the project in ordinary language, gives a correlation example, describes C1-C6 and shows how to read a DPIP result.

Then use the repository according to your role:

- **Implementer/deployer:** [`docs/deployment-guide/`](docs/deployment-guide/) and [`reference-system/`](reference-system/).
- **Specification or assurance reviewer:** [`spec/dpip-v0.1-draft.md`](spec/dpip-v0.1-draft.md), [`examples/`](examples/) and [`results/`](results/).
- **Tooling/integration author:** [`schema/`](schema/), [`evidence/`](evidence/), [`scripts/`](scripts/) and [`docs/rahp-return-operations.md`](docs/rahp-return-operations.md).
- **Release/readiness reviewer:** [`readiness/v0.1.yaml`](readiness/v0.1.yaml), which remains authoritative for v0.1 readiness.

The existence of a v0.1 draft does **not** mean v0.1 is release-ready. The machine-readable readiness artifact and CI remain authoritative.

## Why this project exists

DTG components can individually support privacy while still producing a privacy failure when composed. Selective disclosure or an unlinkable proof is not sufficient if another required component introduces a durable correlator, excessive disclosure, linkable metadata, conflicting lifecycle semantics or unnecessary retained state.

DPIP provides a composition-level assurance layer: it states scoped privacy expectations, records what observers can actually see, binds conclusions to evidence, exercises adversarial tests and produces results that can be reviewed or automated.

## What DPIP owns — and does not own

DPIP does **not** redefine DTG Credentials, Trust Tasks, ZKP constructions, relationship artifacts, agent naming, VTA behavior, DID methods, transports, wallets, discovery policy or VTN governance.

Those components own their semantics and mechanisms. DPIP owns the **composition contract**: the conditions under which an implementation can make a scoped end-to-end privacy claim and the evidence needed to support that claim.

A useful portfolio boundary is:

```text
Portfolio Monitor:  What changed?
RAHP:               What could go wrong?
DPIP:               What privacy property does the composed system actually preserve?
Owning component:   What should change?
```

## Current interaction baseline

| ID | In ordinary language |
| --- | --- |
| **C1** | Privacy-preserving personhood presentation |
| **C2** | Privacy-preserving relationship proof |
| **C3** | Cross-community asymmetric relationship proof |
| **C4** | Privacy-preserving policy discovery |
| **C5** | Privacy-preserving lifecycle evaluation and precedence |
| **C6** | Privacy-preserving recovery and migration |

Reference flows RF-001 through RF-004 compose these concerns into whole-system integration hypotheses. The repository also contains the first implementation-backed RF-001 fixture/run, demonstrating that a useful DPIP result can legitimately contain a mixture of PASS, FAIL, CONSTRAINED and INDETERMINATE conclusions.

## How to read results

Do not reduce DPIP to a single green/red badge. Results are deliberately scoped.

- **PASS / SATISFIED:** available evidence supports the tested expectation for the stated scope.
- **FAIL:** the tested expectation is not met.
- **CONSTRAINED:** intended privacy exists only with an important limitation or residual correlation.
- **INDETERMINATE:** the question matters, but reliable evidence is insufficient to decide.
- **NOT_APPLICABLE:** the referred change/question does not affect the DPIP scope being examined.

Where available, read the plain-language disposition first and use the structured result for exact scope, evidence and automation. See [`docs/understanding-dpip.md`](docs/understanding-dpip.md#reading-a-dpip-result).

## Design posture

The profile is intended to remain:

- implementation-centric;
- construction-neutral where possible;
- compatible with evolving DTG component specifications;
- testable at composed-interaction boundaries;
- explicit about declared, observable and effective correlation scope;
- capable of turning pressure-test findings into reviewed requirements/tests or upstream issues;
- progressively translatable into machine-readable conformance and portfolio revalidation evidence.

## Repository structure

```text
spec/              specification drafts and architecture history
docs/              human-first and deployment guidance
examples/          canonical interaction profiles and tests
reference-system/  non-normative composed flows, findings and run material
schema/             machine-readable artifact formats
results/            conformance-result fixtures
evidence/           external evidence bindings
readiness/          release-readiness gates
portfolio/          cross-repository change-impact metadata
scripts/            validation and assurance tooling
```

## Status

Development draft. The executable baseline is substantial, but v0.1 MUST NOT be declared until the readiness gate reports ready.
