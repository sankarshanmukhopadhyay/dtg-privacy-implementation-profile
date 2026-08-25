# RF-001 Deployment Privacy Guidance

This guidance is informative. It describes the implementation controls and evidence expected when using RF-001 as a DPIP pressure-test harness. It does not define normative DTG component behaviour.

## Wallet / VTA

### Objective

Preserve context separation while composing the private relationship proof.

### Dangerous patterns

- reusing one holder or relationship binding across unrelated verifiers;
- emitting stable wallet/device telemetry alongside otherwise unlinkable presentations;
- retaining proof inputs or relationship identifiers beyond their declared operational purpose;
- recovery or backup processes that collapse pairwise contexts into one operator-visible index.

### DPIP controls

- P2 Contextual unlinkability;
- P4 Compositional privacy;
- P6 Storage minimisation;
- C3-R2, C3-R4, C3-R8.

### Expected evidence

- key/identifier separation configuration;
- proof-binding scope description;
- storage/retention inventory;
- telemetry inventory and correlation analysis;
- recovery-path privacy analysis.

## Trust Task / exchange envelope

### Objective

Carry the evidence required to establish the relationship predicate without creating a durable protocol-envelope correlator.

### Dangerous patterns

- stable `threadId`, task, subject, or exchange identifiers reused across contexts;
- envelope identifiers copied into logs, status systems, or verifier analytics;
- requiring disclosure of a durable subject identifier solely to bind evidence to the exchange.

### DPIP controls

- P2 Contextual unlinkability;
- P4 Compositional privacy;
- P5 Protocol-envelope privacy;
- C3-R2 and C3-T4.

### Expected evidence

- envelope field inventory;
- identifier lifetime/scope rules;
- proof-input binding semantics;
- negative test showing a durable binder is not required;
- retention/logging treatment for exchange identifiers.

RF-001 currently treats this interface as an unresolved upstream dependency (RF-001-F001); deployments MUST NOT infer C3-PC-2 PASS from the reference flow alone.

## Proof construction and verifier

### Objective

Prove only the required reciprocal relationship predicate and keep construction-level privacy claims narrower than end-to-end privacy claims.

### Dangerous patterns

- reusable commitments/equality tokens across verifiers;
- treating hidden private-half identifiers as proof that the relationship itself is unlinkable;
- treating proof verification as evidence of VTN anchoring, cross-VTN policy acceptance, or DTG-edge conformance.

### DPIP controls

- P3 Selective provability;
- P4 Compositional privacy;
- C3-R2, C3-R4, C3-R6, C3-R7;
- C3-T1, C3-T2, C3-T5, C3-T6.

### Expected evidence

- immutable construction/test-vector reference;
- exact predicate statement;
- visible and reusable values inventory;
- verifier policy separating proof result from trust-context result;
- residual-correlation statement.

## Graph, storage, audit, and privileged observers

### Objective

Ensure publication, retention, and operator visibility do not silently widen the privacy claim.

### Dangerous patterns

- a full administrative relationship graph behind an access-control flag while claiming end-to-end unlinkability;
- durable audit records joining pairwise identifiers to named members;
- retaining reciprocal halves, proof transcripts, and task identifiers in one queryable store;
- ignoring operator/auditor/telemetry roles when enumerating observers.

### DPIP controls

- P2 Contextual unlinkability;
- P4 Compositional privacy;
- P6 Storage minimisation;
- C3-R5 and C3-R8;
- C3-PC-3 and C3-PC-5.

### Expected evidence

- observer matrix including privileged roles;
- data-retention purpose and lifetime;
- graph/admin endpoint exposure analysis;
- audit-linkage rationale;
- deletion/rotation controls;
- scoped claim showing where privileged correlation remains.

## Minimum RF-001 deployment evidence package

An RF-001 assessment should contain, at minimum:

1. component/version inventory;
2. assumption register;
3. correlation-surface inventory;
4. wallet/VTA separation evidence;
5. Trust Task/envelope field and binding analysis;
6. immutable proof-construction evidence where available;
7. verifier trust-context policy;
8. graph/storage/audit observer and retention analysis;
9. C3 test results;
10. scoped claim results with residual correlation;
11. unresolved findings and upstream dependencies.

A deployment with unresolved assumptions may still be evaluated, but its conformance result MUST represent affected claims as `INDETERMINATE` or `CONSTRAINED` rather than silently promoting them to `PASS`.
