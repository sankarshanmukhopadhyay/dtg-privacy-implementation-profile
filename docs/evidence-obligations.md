# DPIP evidence obligations

## Purpose

A DPIP `INDETERMINATE` result must not collapse into an unstructured request for “more evidence”. A material unresolved proposition can instead be represented as `dpip-evidence-obligation/v1`: a machine-verifiable statement of what is unknown, who can supply evidence, who may observe it, why evidence is unavailable, what would falsify the proposition, and which downstream assurance proposition consumes the result.

DPIP remains the privacy specialist. It does not manufacture operator-only evidence, infer governance legitimacy from technical observations, or replace RAHP terminal assurance judgment.

## Evidence roles

An obligation separates four roles where applicable:

- **supplier** — actor capable of producing the evidence;
- **observer** — actor/vantage point authorised to make the observation;
- **custodian** — actor retaining raw or restricted evidence (represented in extensions where needed);
- **assurance authority** — actor entitled to interpret or accept the residual risk.

Supplier roles include `TARGET_MAINTAINER`, `TARGET_OPERATOR`, `INDEPENDENT_ASSESSOR`, `INTEROP_LAB`, `GOVERNANCE_AUTHORITY`, `DATA_CONTROLLER`, `THIRD_PARTY_PROCESSOR`, and `UNKNOWN`.

## Evidence maturity

| Level | Meaning |
| --- | --- |
| E0 | assertion or declaration only |
| E1 | static implementation/configuration evidence |
| E2 | deterministic synthetic execution |
| E3 | target-specific controlled runtime evidence |
| E4 | repeated/independent runtime evidence |
| E5 | deployment lifecycle evidence |

Result and maturity are independent. A synthetic `FAIL` may be valid at E2 while `deployment_claim_supported` remains false. E3+ obligations require an immutable target revision unless the explicit blocker is `NO_TARGET`.

## Blockers

Canonical blockers are `NO_TARGET`, `NO_OBSERVATION_SURFACE`, `OPERATOR_ACCESS_REQUIRED`, `GOVERNANCE_AUTHORITY_REQUIRED`, `SENSITIVE_EVIDENCE`, `NO_INSTRUMENTATION`, `NON_REPRODUCIBLE`, `VERSION_UNBOUND`, `COST_DISPROPORTIONATE`, and `AUTHORITY_UNCLEAR`. `NONE` is valid only when evidence is available.

`NO_OBSERVATION_SURFACE`, `NO_INSTRUMENTATION`, and `NON_REPRODUCIBLE` are treated as assurability gaps: the problem is not merely that evidence has not yet been supplied, but that the property cannot currently be demonstrated with the required assurance quality.

## Lifecycle

Obligations use bounded states: `IDENTIFIED`, `QUALIFIED`, `EXPERIMENT_DESIGNED`, `EVIDENCE_ACQUIRED`, `REEVALUATED`, and the terminal/bounded states `SATISFIED`, `FALSIFIED`, `INDETERMINATE`, `ACCEPTED_RESIDUAL_RISK`, `SUPERSEDED`, or `BLOCKED`.

Residual-risk acceptance is not anonymous. `ACCEPTED_RESIDUAL_RISK` requires a named authority and bounded scope.

## Interop Lab admission

Interop Lab is appropriate only when the required fact is legitimately observable through static implementation evidence, black-box runtime evidence, or explicitly delegated white-box access. An operator-only or governance-only proposition remains blocked until the appropriate supplier participates. The Lab must not create synthetic evidence and present it as deployment evidence.

## Reference exemplar: DPIP #191

`fixtures/human-power/dpip-191-evidence-obligations.json` converts the three residual evidence requirements from #191 into executable obligations:

1. observer-bound mapping from trust metadata to the claimed sensitive/social characteristic;
2. cross-context reuse/linkability of the metadata or derived inference;
3. material influence of the nominated feature on a consequential target decision.

All three intentionally remain `BLOCKED` with `NO_TARGET`. This is the correct scientific state: no concrete implementation has been nominated, so another synthetic experiment would not resolve the deployment proposition. DPIP therefore remains `INDETERMINATE` for the proxy-inference proposition until target-bound evidence is supplied.

## Governance invariants

1. No material evidence gap disappears without a terminal/bounded disposition.
2. Synthetic evidence cannot satisfy a target-runtime or deployment obligation.
3. An observer cannot attest to facts outside the declared observation surface.
4. Interop Lab cannot satisfy operator-only evidence without operator evidence/access.
5. DPIP cannot infer normative legitimacy from technical evidence.
6. A privacy failure does not mechanically become a broader RAHP harm finding.
7. Material unresolved privacy uncertainty cannot silently become assurance `PASS`.
8. Residual-risk acceptance requires named authority and scope.
9. Target-specific evidence must bind to an immutable target revision.
10. Evidence from a superseded target revision must be requalified before reuse.

## Reproduction

```bash
python -m unittest discover -s tests -p 'test_evidence_obligations.py' -v
python scripts/evidence_obligations.py \
  --input fixtures/human-power/dpip-191-evidence-obligations.json \
  --check
```

A green run establishes contract consistency only. It does not establish any real-world proxy-inference, discrimination, legitimacy, or deployment claim.
