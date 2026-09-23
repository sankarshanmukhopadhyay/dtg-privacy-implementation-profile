# RAHP #768 — persona reach, usage and timeline privacy examination

**DPIP owner:** #279  
**RAHP owner:** sankarshanmukhopadhyay/rahp-toolkit#768  
**Observed OpenVTC revision:** `95955004e2d9b8d1f456696674bf06648f52d45a`  
**Source introduction:** `OpenVTC/verifiable-trust-infrastructure@9d41d463a8e1bc80c77a5bf352a9be4349d4605a`  
**Trust Tasks source:** `trustoverip/dtgwg-trust-tasks-tf@1fcde9e7b0856449e23dca20625ae0d5f5d4d36a`  
**Assessment date:** 2026-09-23

## Scope and evidence boundary

This examination asks what privacy conclusion is justified by the current source and target-native tests.

No attributable two-context runtime capture was supplied to DPIP for this examination. DPIP therefore does not infer a runtime unlinkability PASS from architecture or unit/integration tests. Where the proposition requires observation of what multiple actors can actually correlate, the correct result is **EVIDENCE_REQUIRED**.

## Positive controls established by source

The current source establishes meaningful minimisation and access controls:

1. **Reach is enforced.** A pool face may be `Anywhere` or limited to explicit context IDs. Binding outside the declared reach is refused.
2. **Omission does not silently widen reach.** Updating a face without a reach value preserves the existing reach.
3. **Narrowing is constrained by current use.** The implementation refuses narrowing that would leave a currently worn face outside its permitted reach.
4. **Usage/timeline are holder-only surfaces.** The dispatcher classifies the reads as holder-only, and target-native census/access tests pin the holder-only boundary.
5. **Timeline excludes face value/private label.** The timeline records event type/time/context-relevant lifecycle information but not the face's value or private label.
6. **Face deletion removes its per-face event log.** The implementation does not retain that `pft:` history as a live face timeline after deletion.

These controls materially reduce exposure and must be credited.

## Material privacy surface established by source

The same source establishes that the feature intentionally creates a **longitudinal, per-face history**:

- the event log is append-only and keyed by face;
- a face's history spans every context in which that face was worn;
- timeline joins the event log with disclosure records;
- events include composed, worn, unworn, expired, disclosed, valueChanged, promoted, retired and reinstated;
- usage exposes current bindings, their `until` values and the face reach.

Consequently, the holder-visible result is deliberately capable of representing a cross-context relationship/activity map for one face. The privacy question is not whether such a map can exist: source evidence says that it does. The remaining question is whether that map can escape the intended holder boundary, be retained elsewhere, or become joinable by an observer not entitled to it.

## Proposition results

### P1 — current-usage disclosure

**Result: BOUNDED_DISCLOSURE.**

The holder receives context identifiers/current bindings, binding lifetime and reach information because that is the purpose of the task. Source evidence supports a holder-only access boundary. It does not establish that every deployment/logging/telemetry surface avoids retaining or exposing the returned identifiers.

### P2 — longitudinal timeline

**Result: BOUNDED_DISCLOSURE.**

The timeline is intentionally longitudinal. Omitting values and private labels is a strong minimisation control, but an ordered sequence of context/lifecycle/disclosure events can itself be distinctive. The source supports the existence of this fingerprint at the holder surface; it does not support a claim that no other observer can correlate it.

### P3 — cross-context composition

**Result: CORRELATION_OBSERVED (holder scope); EVIDENCE_REQUIRED (external-observer scope).**

The implementation explicitly states that one face's history spans every context in which it was worn. This is an intentional holder-side cross-context join, not an inferred weakness.

Whether an operator, relying party, peer, telemetry system or retained evidence surface can reproduce that join requires attributable multi-context runtime evidence that is not present in this assessment.

### P4 — retention and deletion

**Result: BOUNDED_DISCLOSURE / EVIDENCE_REQUIRED.**

Source evidence establishes an append-only per-face event log during the face lifetime and removal of that log on face deletion. It also establishes that timeline joins disclosure records. Source inspection alone does not establish the fate of all copies in logs, backups, telemetry, disclosure-side records or deployment storage after deletion.

### P5 — holder-only access boundary

**Result: PRIVACY_PRESERVED for the source-pinned dispatcher boundary; EVIDENCE_REQUIRED for deployment-wide enforcement.**

The implementation classifies these operations as holder-only and carries target-native tests/census intended to refuse context-scoped administrative access to holder-only tasks. That is positive implementation evidence.

It is not evidence that every deployment, alternate observation surface or operational log preserves the same boundary.

## Overall DPIP result

**EVIDENCE_REQUIRED with bounded positive findings.**

There is no basis for a privacy-failure claim merely because the holder can inspect their own cross-context usage history. Conversely, there is not enough attributable runtime evidence to claim end-to-end privacy preservation across operator, peer, relying-party, telemetry and retained-evidence surfaces.

The current source narrows the residual substantially:

> Can an observer outside the holder boundary reconstruct or retain the per-face cross-context usage/timeline join, including after lifecycle changes or face deletion?

That is the remaining proposition.

## Exact evidence trigger

A future rerun becomes decision-changing when an attributable A/B capture is available with at least two contexts and records, for each observer class:

- same face worn in A and B;
- reach limited to A and attempted use in B;
- wear → unwear → rewear;
- expiry and disclosure;
- promotion;
- retirement → reinstatement;
- deletion;
- repeated usage/timeline reads;
- post-deletion inspection of service storage/log/backup/telemetry surfaces where observable.

The capture must distinguish holder, service/operator, relying party/peer and retained evidence.

## Return to RAHP

RAHP #768 may close its broad assessment as **assessment-complete / specialist result EVIDENCE_REQUIRED** if it records this narrower runtime-observer proposition and its exact retest trigger. It should not leave the generic source-change assessment open indefinitely.

DPIP #279 is terminal for this source-only epoch. A new or reopened examination is warranted only when the runtime evidence trigger is met or the authoritative semantics materially change.
