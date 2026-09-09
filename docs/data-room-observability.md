# Data Room observability experiments

Issue #214 defines the privacy evidence surface for private Data Rooms. The goal is to make membership privacy, metadata privacy and cross-room unlinkability observationally falsifiable rather than inferred from encryption or credential construction.

## Graduation and ownership boundary

The Data Room E1–E6 family is now treated as a **profile instance** of DPIP's reusable privacy-observability model rather than as the generic model itself.

The steady-state ownership boundary is:

```text
Interop Lab / evidence producer
        ↓ target-specific execution and raw observations
DPIP privacy observability semantics
        ↓ scoped privacy interpretation
rahp-assessor-result/v1
        ↓
RAHP terminal reconciliation
```

DPIP owns the meaning of privacy observations, observer/threat-model scope, correlation/join interpretation and the bounded specialist result. Target-specific runtime execution remains in the Interop Lab or another evidence producer. RAHP owns generic evidence/assessor contracts and terminal assurance reconciliation.

The reusable machine-readable privacy result is `dpip-privacy-observability-result/v1`, validated by `contracts/privacy-observability-result-v1.schema.json`. The existing `dpip-data-room-observability/v1` contract remains a compatibility/profile-level representation during migration; it must not become a competing generic provenance or execution envelope.

Generic producer identity, immutable source pins, execution identity, artifact integrity/provenance and freshness/invalidation belong to the RAHP portable producer envelope. DPIP does not duplicate those fields in its reusable privacy result.

A DPIP privacy result may be:

- `supported`
- `not-supported`
- `indeterminate`
- `evidence-incomplete`
- `outside-threat-model`

Absence of a correlation signal may be reported as `not-found` only when the experiment actually ran. When runtime capability is unavailable, use `not-tested` plus `evidence-incomplete`; do not manufacture a privacy PASS. A DPIP specialist `PASS` is bounded to its declared experiment and observer scope and is not a RAHP terminal assurance PASS.

## Reusable observation planes

The reusable contract can represent:

1. host/service operator;
2. verifier/relying party;
3. transport/mediator/network observer;
4. audit/logging/telemetry infrastructure;
5. privileged/deployment observer where explicitly required;
6. an explicitly named additional plane where a profile genuinely needs one.

Each plane records direct observables, derived/joinable signals, privilege assumptions and threat-model scope. This separation matters because encrypted content can coexist with identifying metadata at another plane, and two individually weak signals can compose into an effective join.

## Data Room E1–E6 profile instances

E1–E6 remain stable Data Room experiment identifiers. Their profile-specific subjects and surfaces stay here, while their observer/comparison/result semantics use the reusable DPIP contract.

### E1 — host observability inventory

Inventory request/response metadata, verifier transcripts, timestamps, network/source observations, audit records, room identifiers, invitation state, key-establishment artifacts, stable or pseudonymous identifiers, retries and failures.

Reusable pattern: single/composed observer inventory with explicit host, transport and audit planes. It does not imply confidentiality or unlinkability merely because a particular surface is absent.

### E2 — repeated-member unlinkability

Compare same-member and different-member operations across sessions and, where supported, transports or mediators.

Reusable pattern: A/B or multi-context unlinkability pressure experiment. A supported result requires executed comparison evidence and no effective join at the declared observer planes.

### E3 — invitation and key-establishment leakage

Assess invitation, KeyPackage, welcome, commit, routing, notification and host-side state as possible early membership oracles.

Reusable pattern: observer inventory plus A/B comparison over setup/key-establishment surfaces. Runtime unavailability remains `evidence-incomplete`.

### E4 — cross-room correlation

Exercise the same holder across otherwise private rooms and identify durable or high-confidence joins visible to each observation plane.

Reusable pattern: multi-context correlation pressure experiment. A discovered effective join is `not-supported` for the bounded privacy proposition; absence of a join is not deployment-wide unlinkability.

### E5 — purpose and metadata leakage

Assess title, notification, storage and activity metadata for sensitive purpose or relationship disclosure.

Reusable pattern: metadata-observability inventory with explicit observer and threat-model scope, optionally composed where multiple weak metadata signals produce a useful join.

### E6 — Persona and room multi-context correlation

Assess whether Persona identifiers, disclosure records, verifier state or operational metadata join otherwise separate room contexts.

Reusable pattern: multi-context/composition correlation experiment. Persona/room composition remains a profile instance; the generic semantics are observer scope, joinability, execution state, bounded result and unsupported inference.

## Characterization fixtures

The reusable contract is pressure-tested with canonical fixtures for:

- bounded supported A/B evidence;
- observed-correlation negative privacy evidence;
- runtime unavailable → `evidence-incomplete`;
- privileged observer → `outside-threat-model`.

These fixtures are contract evidence, not claims about a particular production deployment.

## Current pinned Data Room executability

The 2026-09-08 RAHP #481 evidence tranche rechecked the public OpenVTC Data Rooms implementation at `56cd6e5b7116777f1d9734e76c9a7b0569870e19` through `sankarshanmukhopadhyay/trust-protocol-interop-lab#185` / PR #186. Target-native `vti-rooms`, `vti-rooms-dtg`, `room-host`, and `vtc-service` room tests passed, but the implementation boundary remains unchanged for the privacy propositions governed here: private-room serving is still intentionally unavailable pending same-subject/common-control ZK support.

Therefore E2/E3/E4/E5/E6 still cannot produce runtime privacy conclusions for the private tier. The stronger non-private implementation evidence produced by the Interop Lab must not be promoted into private-tier unlinkability or invitation-privacy evidence.

The fixture `contracts/fixtures/data-room-observability-evidence-incomplete.json` remains the required current-state compatibility return for `P-ROOM-007`. It records the gap rather than treating MLS, host key separation, passing room tests, or fail-closed private-room behavior as proof of membership unlinkability. `P-ROOM-008` remains evidence-incomplete for the same executable-runtime reason.

The durable RAHP residual owner is [RAHP #481](https://github.com/sankarshanmukhopadhyay/rahp-toolkit/issues/481), whose canonical proposition definitions come from `profiles/dtg/coverage/data-rooms.yaml`. DPIP should rerun the relevant E-family experiments only when the required private-room execution surface exists or the upstream same-subject/common-control dependency changes materially.

## RAHP mapping

- P-ROOM-007 Membership unlinkability → E2/E4
- P-ROOM-008 Invitation/key-establishment privacy → E3
- P-ROOM-006 Host confidentiality → E1 for runtime corroboration; architectural confidentiality is assessed separately by RAHP
- P-PER-008 Cross-context correlation → E6
- P-PER-009 Cross-context aggregation/non-inference → DPIP supplies observability interpretation where correlation is the privacy proposition; composed authority remains an Interop Lab/RAHP assurance responsibility

All target-specific evidence must retain attributable source/runtime identity and artifacts in the producer envelope. The DPIP result retains experiment configuration, observer scope, correlation interpretation, limitations and residual uncertainty. The portable `rahp-assessor-result/v1` carries that bounded specialist disposition back to RAHP without transferring privacy semantics into RAHP core.
