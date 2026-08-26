# RAHP return-path operations

DPIP returns completed RAHP-originated examinations to their source RAHP issues using an event-driven workflow. The automation transports a conclusion; it does not create one.

## Trigger

`Return completed DPIP dispositions to RAHP` runs when a DPIP issue receives the `run:complete` label. A manual `workflow_dispatch` mode can reconcile one issue or scan completed RAHP-originated issues.

The source issue must also carry `source:rahp`, and the DPIP issue body must contain the structured RAHP provenance created by the intake contract.

## Completion contract

Before `run:complete` is added, the DPIP issue must contain a comment with a machine-readable `dpip_examination:` block. The return tool refuses to guess a technical conclusion from prose, labels or issue state.

A completed examination may additionally carry:

```yaml
human_summary:
  outcome: Privacy works, but with important limitations
  explanation: >-
    The private identifier is protected from the ordinary verifier, but an
    operator-visible value can still link the two contexts.
  action: >-
    Keep the private identifier protection, but do not claim end-to-end
    unlinkability until the remaining correlation is removed or accepted.
```

The human summary is **not** a replacement for the formal disposition. It is a faithful explanatory view of the same conclusion for specification editors, implementers and other readers who should not have to decode DPIP status vocabulary before understanding the result.

When an explicit `human_summary` is absent, the return tool provides a conservative default outcome label and derives the explanation/action from the authoritative structured evidence summary, residual-correlation and action fields. It does not change the formal conclusion.

## Returned RAHP comment

The return comment presents information in this order:

1. DPIP issue/link;
2. **plain-language result** — outcome, explanation and what to do;
3. a collapsible structured `dpip_disposition:` block containing the authoritative machine-readable fields;
4. the reminder that DPIP completion closes only the privacy handoff subflow.

The structured block includes:

- DPIP issue number;
- applicability;
- formal conclusion;
- the human summary;
- affected interactions/reference flows/claims/invariants when present;
- evidence summary;
- residual correlation when present;
- disposition/action.

Typical plain-language outcome labels are:

| Formal conclusion | Default plain-language outcome |
| --- | --- |
| `PASS` | Privacy expectation met |
| `FAIL` | Privacy expectation not met |
| `CONSTRAINED` | Privacy works, but with important limitations |
| `INDETERMINATE` | We do not have enough evidence to decide yet |
| `NOT_APPLICABLE` | This privacy test does not apply here |

The comment is marked deterministically so reconciliation cannot post it twice.

## Activation

Configure this repository secret:

- `RAHP_HANDOFF_TOKEN` — a narrowly scoped fine-grained token able to read metadata and read/write **Issues** only in `sankarshanmukhopadhyay/rahp-toolkit`.

The normal repository `GITHUB_TOKEN` remains read-only for DPIP issue access. Cross-repository writes use only the dedicated token.

Without `RAHP_HANDOFF_TOKEN`, the workflow validates the return tooling but exits without modifying RAHP.

## RAHP lifecycle effect

A successful return adds:

```text
assurance:dpip-complete
```

and removes the transient candidate/requested/open labels if they remain.

The return automation deliberately does **not** close the RAHP issue. DPIP completion may resolve only one sub-question within a wider RAHP or security assessment.

## Reconciliation and retry discipline

A completed `INDETERMINATE` examination is still complete. It is not re-opened because the Portfolio Monitor sees the same source revision again. Re-examination requires the material evidence condition recorded by DPIP, a materially changed source revision, or a changed DPIP target/question.
