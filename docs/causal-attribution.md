# Causal attribution in DPIP judgments

DPIP separates five stages when runtime evidence appears to show a privacy failure:

1. **Observation** — what an observer actually received or read.
2. **Boundary analysis** — whether the declared privacy or authorization boundary was crossed.
3. **Causal attribution** — which executed mechanism made the observation possible.
4. **Proposition matching** — whether that mechanism is the mechanism named by the proposition under examination.
5. **Scoped judgment** — PASS, FAIL or INDETERMINATE for that proposition only.

## Governing invariant

> Observation of a prohibited outcome is not sufficient to FAIL a proposition about its causal mechanism.

A common value observed by two contexts proves an observable join. It does not, without more evidence, prove that a particular transport, identifier, credential, persistence mechanism or protocol surface independently caused that join.

When a prohibited effect is observed but attribution to the examined mechanism is absent or points to a different mechanism, DPIP records `INDETERMINATE / causal-attribution-insufficient` for the examined proposition. A separately evidenced proposition may still FAIL.

## Machine-readable attribution

Evidence producers may attach:

```yaml
causal_attribution:
  status: established
  mechanism: authorization-scope-bypass
  responsible_surface: enumeration-api
  proposition_match: false
  evidence:
    - observer-a-read-out-of-scope-record
    - observer-b-read-out-of-scope-record
alternative_mechanisms:
  cross-context-runtime-transport:
    status: not-evidenced
```

Names above are illustrative. The judgment engine treats the structure generically and must not contain target-specific names.

## Terminal semantics

- prohibited effect + established matching cause -> `FAIL`;
- prohibited effect + missing/different cause -> `INDETERMINATE / causal-attribution-insufficient`;
- valid experiment + no prohibited effect -> scoped `PASS`;
- malformed or uninterpretable evidence -> `INDETERMINATE` under the applicable evidence reason.

A terminal report should expose observation, attribution, judgment and excluded inference separately so reviewers can distinguish *what happened* from *why it happened*.

## Historical regression

The device-metadata sequence that motivated this rule is intentionally preserved as history. An early experiment over-attributed deterministic metadata to cross-context correlation. A methodology-corrected experiment later established a real observer-visible boundary crossing through a context-scope enforcement defect while explicitly leaving heartbeat transport untested. The correct assurance result is therefore a FAIL for the independently evidenced scope-enforcement proposition and INDETERMINATE for the unproven heartbeat-correlation mechanism.

The lesson is generic: correcting an inference must not erase a real observation, and discovering a real adjacent defect must not be used to rescue an unsupported causal conclusion.
