# Task-citation and outcome-evidence correlation examination

Issue #271 is the fresh DPIP examination epoch for the Credential × Trust Tasks × VTI convergence coordinated in RAHP #690.

## Proposition

A credential presentation can preserve selective disclosure at the credential layer while still exposing a stable task citation, task digest, outcome-evidence identifier, or retained transcript value that lets unrelated relying contexts join the interaction.

DPIP therefore evaluates correlation at the composed interaction boundary rather than treating successful proof verification as evidence of unlinkability.

## Evidence source

The canonical downstream producer is Interop Lab #233. Its machine-readable package uses the schema:

interop-task-citation-convergence-evidence/v1

DPIP consumes that package through:

scripts/task_citation_correlation.py

## Admission rules

The mapper deliberately fails closed:

- fixture-only evidence can demonstrate a pressure case but cannot establish target-runtime privacy;
- not-implemented and not-observable remain evidence-incomplete;
- an observed stable join at target runtime returns a bounded negative privacy result;
- absence of an observed join can support only the source-pinned observer scope and never deployment-wide unlinkability.

## Observer boundary

The required observer planes are:

- verifier: presentation-visible citation, digest, commitments, and outcome-evidence references;
- audit: retained task documents, outcome evidence, and presentation transcript identifiers.

A future committed-citation or proof-hidden construction must be reassessed as a new source-pinned epoch if its observable surfaces change.

## Non-inference rules

- proof validity does not imply presentation unlinkability;
- hidden credential attributes do not imply hidden task citation;
- valid outcome evidence does not imply action authority;
- fixture behavior does not prove target implementation behavior;
- absence of runtime evidence does not imply privacy PASS.

## Closure

Issue #271 can close when the mapper has consumed attributable source-pinned runtime evidence from the current implementation boundary and produced a terminal bounded DPIP result. If runtime support remains unavailable, the correct terminal state for this epoch is INDETERMINATE / evidence-required with the missing surfaces named explicitly.
