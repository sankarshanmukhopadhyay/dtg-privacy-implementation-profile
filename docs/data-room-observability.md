# Data Room observability experiments

Issue #214 defines the privacy evidence surface for private Data Rooms. The goal is to make membership privacy, metadata privacy and cross-room unlinkability observationally falsifiable rather than inferred from encryption or credential construction.

## Evidence boundary

DPIP produces privacy evidence. RAHP retains the terminal assurance judgment.

The canonical machine-readable return is `dpip-data-room-observability/v1`, validated by `contracts/data-room-observability-v1.schema.json`.

A result may be:

- `supported`
- `not-supported`
- `indeterminate`
- `evidence-incomplete`
- `outside-threat-model`

Absence of a correlation signal may be reported as `not-found` only when the experiment actually ran. When runtime capability is unavailable, use `not-tested` plus `evidence-incomplete`; do not manufacture a privacy PASS.

## Observation planes

Every experiment records observations separately for:

1. host;
2. verifier;
3. transport/mediator/network;
4. audit/logging infrastructure.

This separation matters because encrypted content can coexist with identifying metadata at another plane.

## Experiment family

### E1 — host observability inventory

Inventory request/response metadata, verifier transcripts, timestamps, network/source observations, audit records, room identifiers, invitation state, key-establishment artifacts, stable or pseudonymous identifiers, retries and failures.

### E2 — repeated-member unlinkability

Compare same-member and different-member operations across sessions and, where supported, transports or mediators.

### E3 — invitation and key-establishment leakage

Assess invitation, KeyPackage, welcome, commit, routing, notification and host-side state as possible early membership oracles.

### E4 — cross-room correlation

Exercise the same holder across otherwise private rooms and identify durable or high-confidence joins visible to each observation plane.

### E5 — purpose and metadata leakage

Assess title, notification, storage and activity metadata for sensitive purpose or relationship disclosure.

### E6 — Persona and room multi-context correlation

Assess whether Persona identifiers, disclosure records, verifier state or operational metadata join otherwise separate room contexts.

## Current pinned executability

The 2026-09-08 RAHP #481 evidence tranche rechecked the public OpenVTC Data Rooms implementation at `56cd6e5b7116777f1d9734e76c9a7b0569870e19` through `sankarshanmukhopadhyay/trust-protocol-interop-lab#185` / PR #186. Target-native `vti-rooms`, `vti-rooms-dtg`, `room-host`, and `vtc-service` room tests passed, but the implementation boundary remains unchanged for the privacy propositions governed here: private-room serving is still intentionally unavailable pending same-subject/common-control ZK support.

Therefore E2/E3/E4/E5/E6 still cannot produce runtime privacy conclusions for the private tier. The stronger non-private implementation evidence produced by the Interop Lab must not be promoted into private-tier unlinkability or invitation-privacy evidence.

The fixture `contracts/fixtures/data-room-observability-evidence-incomplete.json` remains the required current-state return for `P-ROOM-007`. It records the gap rather than treating MLS, host key separation, passing room tests, or fail-closed private-room behavior as proof of membership unlinkability. `P-ROOM-008` remains evidence-incomplete for the same executable-runtime reason.

The durable RAHP residual owner is [RAHP #481](https://github.com/sankarshanmukhopadhyay/rahp-toolkit/issues/481), whose canonical proposition definitions come from `profiles/dtg/coverage/data-rooms.yaml`. DPIP should rerun the relevant E-family experiments only when the required private-room execution surface exists or the upstream same-subject/common-control dependency changes materially.

## RAHP mapping

- P-ROOM-007 Membership unlinkability → E2/E4
- P-ROOM-008 Invitation/key-establishment privacy → E3
- P-ROOM-006 Host confidentiality → E1 for runtime corroboration; architectural confidentiality is assessed separately by RAHP
- P-PER-008 Cross-context correlation → E6
- P-PER-009 Cross-context aggregation/non-inference → DPIP supplies observability evidence where correlation is the privacy proposition; composed authority remains an Interop Lab responsibility

All returned evidence must retain the source/runtime revision, experiment configuration, observations, limitations, residual uncertainty and artifact locations.
