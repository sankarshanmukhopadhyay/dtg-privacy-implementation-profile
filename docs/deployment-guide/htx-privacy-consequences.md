# HTX Privacy-Consequence Guidance

This guidance is informative. It describes the user-facing privacy evidence DPIP expects around Human Trust Experience (HTX) boundaries. It does not define normative HTX interaction design.

## Privacy objective

A user should be able to understand the material privacy consequences of an interaction before authorizing it, especially where the interaction exposes identity, community affiliation, relationship intent, durable linkability, privileged observer access, or status/lifecycle information.

## Dangerous implementation patterns

- consent screens that say only “share credential” while hiding which identifiers or relationship context will become linkable;
- presenting selective disclosure as equivalent to unlinkability;
- failing to disclose that a public or community-visible relationship half constrains privacy of the complete relationship;
- failing to distinguish ordinary verifier visibility from administrator/auditor visibility;
- recovery or lifecycle actions that introduce new correlation without a user-visible consequence statement;
- policy-discovery queries that reveal target-specific relationship intent without warning.

## DPIP controls

- **P1 Data minimisation** — user-facing choices should align with the minimum evidence actually required.
- **P4 Compositional privacy** — HTX should describe the result of the complete interaction, not only the privacy feature of one credential or proof.
- **P5 Protocol-envelope privacy** — relevant metadata/linkability consequences should not disappear from the user model merely because they are outside the credential payload.
- **P8 User-visible disclosure context** — material disclosure, recipient, purpose, and linkability consequences should be understandable before authorization.

## Minimum consequence statement

For privacy-sensitive actions, the UX/HTX layer should be able to derive or display, in implementation-appropriate language:

1. **what is being proven or disclosed**;
2. **who can observe it**;
3. **whether a stable identifier or relationship signal is exposed**;
4. **whether the interaction can be linked to prior/future contexts**;
5. **whether privileged operators receive broader visibility**;
6. **whether the action creates persistent public/community state**;
7. **whether withdrawal, recovery, or status checking changes that privacy posture**.

## Evidence expected

- interaction screenshots or structured UI states;
- mapping from UI consequence statements to DPIP claims/correlation surfaces;
- test cases for hidden metadata or privileged-observer consequences;
- accessibility/plain-language review appropriate to the deployment;
- evidence that the UI does not label a `CONSTRAINED` or `FAIL` scoped claim as simply “private” or “unlinkable”.

## Negative tests

### HTX-T1 — proof-feature overclaim

A UI describes a presentation as “unlinkable” solely because the proof construction hides the holder identifier while public graph context remains correlatable. The UI fails the DPIP composition model.

### HTX-T2 — hidden privileged observer

An ordinary verifier sees only a pairwise identifier, but an administrator can reconstruct the complete relationship graph. If the authorization experience presents the interaction as private without the material operator visibility, P8 is not adequately supported.

### HTX-T3 — intent leakage during discovery

RF-002 requires a target-specific pre-flight query. The UI should not imply that no relationship intent is exposed if the target can infer the contemplated interaction.

### HTX-T4 — lifecycle privacy change

A status/recovery action changes the effective correlation scope. The user-facing flow should not reuse the previous privacy label without recalculating the consequence.

## Mapping to canonical interactions

- **C1** — distinguish predicate disclosure from presentation linkability.
- **C2/C3** — disclose relationship-level consequences separately from private-half protection.
- **C4/RF-002** — represent pre-flight intent exposure and target/community visibility.
- **C5/RF-003** — represent status/freshness queries, precedence uncertainty, and privacy changes caused by lifecycle operations.

## Principle

HTX does not determine whether a privacy claim is technically true. DPIP computes/assesses the scoped claim; HTX is responsible for making the material consequence of that assessed interaction intelligible at the authorization boundary.
