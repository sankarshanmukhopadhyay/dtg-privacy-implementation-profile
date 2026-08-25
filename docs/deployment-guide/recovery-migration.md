# Recovery and Migration Privacy Guidance

This guidance is informative. It identifies privacy controls and evidence expected when a wallet/VTA, key set, relationship context, or credential store is recovered or migrated. It does not define normative recovery protocols for DTG components.

## Privacy objective

Recovery or migration should restore continuity of control without collapsing pairwise contexts, exposing a master correlation index, or creating a new durable identifier that links previously separated interactions.

## Dangerous implementation patterns

- restoring all pairwise identifiers into one operator-visible account index;
- using one recovery identifier or support ticket as a permanent join key across relationship contexts;
- exporting plaintext relationship graphs or proof transcripts as part of backup;
- re-keying every context from one stable recovery seed without analysing cross-context observability;
- migration logs that map old and new identifiers indefinitely;
- recovery ceremonies that reveal unrelated credentials or communities to an operator.

## DPIP controls

- **P1 Data minimisation** — recover only the material needed for the intended continuity outcome.
- **P2 Contextual unlinkability** — recovery MUST NOT silently make previously separated contexts joinable.
- **P4 Compositional privacy** — a privacy-preserving credential/proof stack can still fail if recovery creates a global binder.
- **P5 Protocol-envelope privacy** — recovery tokens, support identifiers and migration transaction IDs are correlation surfaces.
- **P6 Storage minimisation** — backup, escrow and migration records require explicit retention purpose and lifetime.
- **P8 User-visible disclosure context** — users should understand when recovery exposes relationships or identity to another actor.

## Evidence expected

An implementation assessment should provide:

1. inventory of backup/recovery identifiers and their intended scope;
2. mapping of old-to-new identifiers and deletion/retention rules;
3. key derivation/separation description;
4. operator/support observer matrix;
5. encrypted backup contents and minimisation rationale;
6. test showing unrelated pairwise contexts do not become joinable after recovery;
7. migration telemetry/log inventory;
8. user-facing disclosure of any unavoidable correlation introduced by recovery.

## Negative and adversarial tests

### RM-T1 — global recovery binder

Recover two previously unrelated pairwise contexts and determine whether a stable recovery account, ticket, seed-derived identifier, or migration record lets an observer join them. If yes, the affected P2/P4 claim fails or becomes constrained.

### RM-T2 — old/new identifier bridge

Verify that old-to-new identifier mapping is not retained beyond its justified migration purpose. Indefinite retention creates a new historical correlation surface.

### RM-T3 — operator graph reconstruction

Pressure-test whether a recovery operator can reconstruct the holder's full relationship graph even though ordinary verifiers cannot. Any such capability must be represented in effective privacy scope.

### RM-T4 — unrelated evidence disclosure

Attempt recovery of one relationship context while withholding unrelated credentials and communities. Requiring unrelated disclosure violates P1 unless an owning protocol supplies a justified requirement.

## Declared, observable, and effective scope

A recovery identifier can be declared `recovery-session` while being observable in support, backup, analytics, and account systems. The effective scope therefore follows the complete observable deployment, not the label chosen by the wallet.

Example:

```yaml
recovery_handle:
  declared_scope: recovery-session
  observable_scope: support-and-wallet-operator
  effective_scope: cross-context-if-reused
```

## Relationship to future canonical interactions

Recovery/migration should become a dedicated canonical interaction after C5/RF-003 stabilises. Until then, deployments can use this guide to add recovery-specific correlation surfaces and negative tests to their conformance package.
