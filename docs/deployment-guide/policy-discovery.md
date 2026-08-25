# Privacy-Preserving Policy Discovery

This guidance is informative. It applies C4 and RF-002 to pre-flight discovery and policy evaluation without defining normative DTG discovery or VTN policy semantics.

## Objective

Allow an implementation to answer an admissibility question before relationship establishment while revealing no more requester identity, target context, relationship intent, routing metadata, or retained state than necessary.

## Dangerous implementation patterns

- requiring a durable requester DID, account identifier, wallet identifier, or relationship identifier merely to ask whether an interaction is allowed;
- reusing one discovery handle across multiple target communities;
- exposing a target-specific endpoint when a coarse or cached policy class would answer the question;
- storing rejected queries with requester identity, target, purpose and high-resolution time;
- treating a privacy-preserving pre-flight query as evidence that the later credential, Trust Task or proof exchange is also privacy-preserving;
- omitting operator, analytics, telemetry and audit systems from the observer model.

## DPIP controls

Primary invariants: P1, P2, P4, P5, P6 and P8.

Primary C4 controls: C4-R1 through C4-R6 and C4-T1 through C4-T5.

## Implementation pattern

1. Resolve the least-specific policy class or endpoint capable of answering the admissibility question.
2. Use a session- or target-scoped request handle rather than a durable cross-context requester identifier.
3. Submit only the policy facts required for the answer.
4. Return the minimum decision information required to proceed or stop.
5. Treat rejection records, endpoint selection, query IDs and timestamps as correlation surfaces.
6. Bound retention and privileged access to discovery records.
7. Evaluate the later DTG interaction independently; do not inherit the C4 result.

## Evidence package

An implementation claiming C4 should provide, as applicable:

- discovery/routing identifier scope and lifetime rules;
- policy input/output field inventory;
- evidence that unrelated targets do not require the same requester handle;
- endpoint-resolution and caching behaviour;
- rejection-log and telemetry inventory;
- retention purpose, duration, aggregation and deletion controls;
- operator/auditor observer matrix;
- C4 test results and residual intent-correlation statement.

## Declared, observable and effective scope

A discovery value's declared scope is not sufficient evidence of its effective privacy. For example, a request identifier may be declared `session`, observed by an operator through persistent logs, and therefore have an effective scope of `deployment-if-retained`. C4 assessments should record this divergence explicitly.

Likewise, hiding the requester identifier does not necessarily hide the relationship intent. A target-specific policy query can remain contextual evidence that a particular relationship or trust interaction was contemplated.

## Negative assurance questions

- Can two target communities join requests using a requester, wallet or routing identifier?
- Can an operator reconstruct rejected relationship attempts from logs?
- Does endpoint selection reveal the target context before that disclosure is needed?
- Can timing correlate a pre-flight query with a later relationship establishment?
- Does the implementation claim downstream privacy merely because policy discovery passed?

Any `yes` answer must either be justified as required linkability with a scoped claim or represented as a privacy failure/constraint.
