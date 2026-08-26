# RAHP return-path operations

DPIP returns completed RAHP-originated examinations to their source RAHP issues using an event-driven workflow. The automation transports a conclusion; it does not create one.

## Trigger

`Return completed DPIP dispositions to RAHP` runs when a DPIP issue receives the `run:complete` label. A manual `workflow_dispatch` mode can reconcile one issue or scan completed RAHP-originated issues.

The source issue must also carry `source:rahp`, and the DPIP issue body must contain the structured RAHP provenance created by the intake contract.

## Completion contract

Before `run:complete` is added, the DPIP issue must contain a comment with a machine-readable `dpip_examination:` block. The return tool refuses to guess a conclusion from prose, labels, or issue state.

The returned RAHP comment includes:

- DPIP issue number and link;
- applicability;
- conclusion;
- affected interactions/reference flows/claims/invariants when present;
- evidence summary;
- residual correlation when present;
- disposition/action.

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
