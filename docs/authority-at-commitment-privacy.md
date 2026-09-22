# Authority-at-Commitment Privacy Profile

## Purpose

C9 applies DPIP to the authority-at-material-commitment pattern. The authority question is legitimate: a counterparty may need to know that an agent can make the exact commitment. The privacy failure is assuming that verification requires disclosure of the entire mandate or delegation graph.

## Privacy boundary

A verifier may need to establish propositions such as:

- the actor derives authority from the stated principal;
- the authority is current at the commitment time;
- the exact action is within scope and material limits;
- required approval covers this exact action; and
- revocation/status evidence is fresh enough.

Those propositions do **not** automatically require disclosure of unrelated counterparties, wider authority scope, organizational hierarchy, total budget authority, internal approval history or reusable identifiers across contexts.

C9 is construction-neutral. Selective disclosure, ZKP, bounded attestations, pairwise/scoped identifiers or ordinary minimized credentials can satisfy the profile if the observable interaction meets the requirements.

## Evidence requirement

Specification intent is not enough to award PASS. Runtime or implementation evidence should show what the verifier, resolver and other observers actually receive. Where that evidence is missing, DPIP records INDETERMINATE.

## Relationship to authority semantics

DPIP does not decide whether authority exists. GAAM/TSMM and the owning authorization policy define that proposition; TIS may carry it. DPIP asks whether the composed proof and status-check interaction reveals or correlates more than the relying purpose requires.
