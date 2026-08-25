# DPIP Finding Promotion and Adversarial Regression Workflow

DPIP findings originate from composed reference flows, implementation evidence, RAHP-style pressure tests, interoperability failures, or specification review. A finding is not automatically a normative DPIP requirement.

## Lifecycle

1. **Candidate** — the finding is observed and has provenance, owner, affected DPIP IDs and evidence.
2. **Reviewed** — the composition impact and owning layer are understood; maintainers decide whether action belongs in DPIP, upstream, deployment guidance, or accepted risk.
3. **Promoted** — the finding becomes one of:
   - a DPIP requirement;
   - a DPIP positive/negative/adversarial test;
   - DPIP deployment guidance;
   - an upstream issue owned by another specification;
   - an explicitly accepted risk.
4. **Resolved regression** — after the issue is addressed, the finding remains represented by a stable test/evidence reference so the failure does not silently return.

## Governance rules

- A reference-flow assumption does not become normative merely because it generated a finding.
- Component semantics and interfaces remain owned by their component specifications.
- DPIP may promote the **composition requirement** needed to evaluate privacy even when the implementation mechanism remains upstream-owned.
- A finding promoted upstream should link the upstream issue/PR and retain the DPIP impact IDs.
- A resolved privacy failure should normally retain at least one negative/adversarial regression vector.
- Evidence maturity and finding maturity are distinct. A reviewed finding can still depend on candidate evidence.

## Machine-readable promotion record

A finding may carry:

```yaml
promotion:
  state: resolved-regression
  target_type: dpip-test
  target_refs: [C3-T2, C3-T3, C3-T7]
  rationale: Pairwise identifier privacy does not establish relationship-level unlinkability.
  regression_refs: [C3-R4, C3-R5, C3-R8, C3-PC-3, C3-PC-5]
```

Promotion states are `candidate`, `reviewed`, `promoted-dpip`, `promoted-upstream`, `resolved-regression`, and `not-promoted`.

## RF-001 worked example

`RF-001-F003` began as a privacy-overclaim finding: the private half of an asymmetric relationship remained pairwise, but the reciprocal half and graph were publicly observable. The finding was promoted into scoped privacy claims, correlation-scope semantics, and C3 negative/adversarial tests. It is now recorded as `resolved-regression`, with C3-T2, C3-T3 and C3-T7 retaining the failure mode as executable evidence.

By contrast, `RF-001-F001` remains `reviewed`: the composition requirement is understood, but the missing privacy-compatible Trust Task binding interface is upstream-owned and should only become an upstream issue when the exact interface gap can be stated without DPIP inventing Trust Task semantics.

## Maintainer disposition questions

For each finding, ask:

1. Is the failure in DPIP's composition model or an owning component interface/semantic?
2. Can the finding be expressed as a construction-neutral privacy requirement?
3. Is there enough evidence to promote it, or should it remain candidate?
4. Does it require an upstream issue, deployment guidance, a new test, or accepted risk?
5. If resolved, what test/evidence must remain so the failure cannot regress silently?
