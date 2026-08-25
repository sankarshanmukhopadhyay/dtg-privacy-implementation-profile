# Lifecycle Privacy, Status and Precedence

This guidance is informative. It applies C5 and RF-003 to lifecycle evaluation without defining lifecycle semantics owned by DTG component specifications or deployment policy.

## Objective

Evaluate whether an artifact is currently effective, and how multiple lifecycle-bearing artifacts combine, without unnecessary identity, relationship, status-query or historical-context disclosure.

## Core rule

Cryptographic validity, lifecycle state and composed decision precedence are distinct.

A signature or proof can remain valid after an artifact is expired, suspended, superseded or otherwise non-effective. Likewise, several individually current artifacts can still yield an indeterminate composed result when no owning specification or deployment policy defines which lifecycle state controls.

## Dangerous implementation patterns

- accepting a signed/proven artifact solely because cryptographic verification succeeds;
- using one stable status handle across unrelated verifiers;
- querying a central status source for every presentation when a less correlatable mechanism is available;
- treating stale Trust Task evidence as current because the credential it accompanies is current;
- inventing precedence between credential, relationship, delegation and Trust Task lifecycle states;
- publishing a durable replacement/supersession chain that joins previously separate pairwise contexts;
- retaining complete lifecycle history when only current-effect evidence is required.

## DPIP controls

Primary invariants: P1, P2, P4, P5, P6 and P7.

Primary C5 controls: C5-R1 through C5-R7 and C5-T1 through C5-T6.

## Implementation pattern

1. Identify only lifecycle-bearing artifacts material to the trust decision.
2. Resolve cryptographic validity and lifecycle state separately.
3. Obtain the least revealing freshness/status evidence capable of supporting the decision.
4. Record the owning source for each lifecycle state.
5. Apply only an evidenced precedence rule. If no rule exists, report the composed decision as `INDETERMINATE`.
6. Expose only the history required to establish current effect, bounded predecessor/successor continuity, or required accountability.
7. Treat status handles, lookup endpoints, timestamps, replacement chains and lifecycle audit records as correlation surfaces.
8. Scope privacy claims to ordinary and privileged observers separately where their views differ.

## Evidence package

A C5 assessment should provide, where applicable:

- lifecycle state vocabulary and owning specification/policy;
- cryptographic-validity versus current-effect evaluation logic;
- status mechanism and identifier-scope description;
- status-source observer and logging analysis;
- freshness requirements and timestamp precision;
- precedence table or policy references for conflicting lifecycle states;
- Trust Task freshness/cancellation/supersession evidence;
- replacement/supersession-chain exposure rules;
- retention and audit-purpose inventory;
- C5 test results and residual-correlation statements.

## Precedence table pattern

A deployment may use a table similar to the following, but the actual semantics are owned outside DPIP:

| Artifact | Observed state | Owning source | Effect on decision | Evidence |
|---|---|---|---|---|
| relationship credential | current | credential/relationship spec | candidate input | versioned state evidence |
| delegation | suspended | delegation semantics | deployment-defined | status evidence |
| Trust Task | stale | Trust Task spec | deployment-defined | freshness evidence |

If the `Effect on decision` column cannot be justified from an owning specification or deployment policy, DPIP records the composed result as `INDETERMINATE` rather than inventing precedence.

## Historical-linkage rule

Restoration, migration, replacement and supersession may legitimately require continuity evidence. That does not authorize unrestricted historical correlation. Implementations should disclose or retain the minimum predecessor/successor relation required by the trust purpose and make privileged correlation explicit in the claim scope.

## Negative assurance questions

- Can a status source recognize the same holder or relationship across unrelated verifier contexts?
- Does proof validity override lifecycle state in implementation logic?
- Is there an undocumented precedence rule between lifecycle-bearing artifacts?
- Can replacement chains reconstruct previously pairwise relationship contexts?
- Does the verifier receive complete history when only current effect is needed?
- Do audit logs join status handles, holder identity, relationship state and decision history?

Any affirmative answer must be justified as required linkability or represented as a failed, constrained or indeterminate DPIP result.
