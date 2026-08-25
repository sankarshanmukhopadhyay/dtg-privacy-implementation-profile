# P7 Lifecycle Review

Status: design input for the v0.1 specification restructuring; C5/RF-003 applies the conclusions immediately.

## Current invariant

P7 currently focuses on withdrawal, relationship termination, credential status and revocation without unnecessary exposure.

## Finding

C5/RF-003 shows that this framing is too narrow for composed DTG implementation assessment. A privacy-preserving lifecycle decision can also depend on expiry, suspension, supersession, restoration, replacement, freshness and the precedence between states owned by different component specifications.

The privacy problem has two parts:

1. **lifecycle evidence privacy** — obtaining and retaining current-effect evidence must not introduce unnecessary correlation; and
2. **lifecycle decision correctness** — privacy-preserving proof or status evidence must not be combined using an invented or undocumented precedence rule.

## Recommended v0.1 refinement

During the v0.1 specification restructuring tracked in #29, P7 should evolve from a revocation-oriented invariant toward **Privacy-preserving lifecycle correctness**, along the following lines:

> Withdrawal, expiry, suspension, supersession, restoration, replacement, status and other lifecycle facts MUST be evaluable without unnecessary disclosure or correlation. Where multiple lifecycle-bearing artifacts participate in a composed decision, the implementation MUST identify the owning lifecycle semantics and MUST NOT invent precedence that is not supported by an owning specification or deployment policy.

## Boundary

This refinement does not make DPIP the owner of credential, relationship, delegation or Trust Task lifecycle semantics. DPIP owns only the composition requirement: the implementation must obtain lifecycle evidence privacy-preservingly, identify the owning semantics, and represent the final result as `INDETERMINATE` when the required precedence is not evidenced.

C5-R1 through C5-R7 and RF-003 are the executable pressure test for this proposed refinement.
