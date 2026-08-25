# RF-001 RUN-001

This package is DPIP's first implementation-backed RF-001 execution fixture. It is deliberately non-normative: the fixture exists to exercise the composed assurance pipeline and produce evidence about this exact run, not to stand in for missing DTG component semantics.

## What was executed

Two unrelated private relationship contexts were instantiated with distinct pairwise identifiers, task identifiers and proof binders. The verifier did not receive either private identifier. Public relationship signals were retained, while a privileged operator index and shared telemetry device identifier were deliberately made available to test whether broader deployment observers could correlate contexts.

RF-001 S-01 through S-07 are recorded in `observations/run-observations.yaml`. Adversarial join attempts are recorded in `adversarial/join-attempts.yaml`. The implementation manifest is `implementation.yaml`, and finding reconciliation is captured in `findings-reconciliation.yaml`.

Machine-readable evidence bindings are registered at `evidence/rf001-run001.yaml`; the scoped conformance result is `results/rf001-run001.yaml`.

## Result

The run demonstrates a mixed outcome rather than a green badge:

- private-half non-disclosure: `PASS` for this fixture;
- private identifier cross-context unlinkability: `INDETERMINATE` because Trust Task binding semantics and immutable ZKP construction evidence remain unresolved upstream dependencies;
- relationship unlinkability: `FAIL` because the public half and graph are deliberately correlatable;
- presentation unlinkability: `CONSTRAINED`;
- contextual/graph unlinkability: `CONSTRAINED`, with privileged operator and telemetry correlation broader than ordinary-verifier visibility.

## Evidence rule

The generated fixture artifacts can be verified evidence of what this DPIP fixture did at their pinned commits. They are not verified evidence that DTG Credentials, Trust Tasks, ZKP, VTA, or any deployment will behave the same way. Upstream issue/design inputs remain candidate evidence until immutable implementation/construction artifacts exist.
