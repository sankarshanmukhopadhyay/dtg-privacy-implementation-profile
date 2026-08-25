# Privileged Observer Privacy Guidance

This guidance is informative. It extends DPIP's observer model beyond holders, issuers and verifiers to administrators, auditors, moderators, support staff, telemetry processors, infrastructure operators and other privileged roles.

## Privacy objective

A deployment MUST NOT claim end-to-end unlinkability or contextual privacy by analysing only ordinary protocol participants when privileged infrastructure can reconstruct the same relationship, identity or interaction history.

## Privileged observer classes

Implementers should explicitly enumerate, where applicable:

- wallet/VTA operator;
- discovery/routing operator;
- Trust Task service operator;
- verifier administrator;
- VTN/community administrator;
- relationship graph administrator;
- auditor/compliance reviewer;
- support/recovery operator;
- moderator or dispute-resolution role;
- telemetry/logging/analytics processor;
- infrastructure/database administrator.

## Dangerous implementation patterns

- pairwise identifiers for verifiers combined with a global administrative lookup table;
- “privacy-preserving” relationship graphs that expose complete adjacency to administrators;
- central telemetry joining wallet, Trust Task, status and proof identifiers;
- audit logs retained indefinitely without scoped purpose;
- support/recovery systems that correlate all user contexts;
- privileged APIs omitted from threat models because access control is assumed to make correlation irrelevant.

## DPIP controls

- **P2 Contextual unlinkability** — effective scope includes privileged joinability where it materially affects the claim.
- **P4 Compositional privacy** — hidden identifiers at one layer do not erase broader visibility elsewhere.
- **P5 Protocol-envelope privacy** — logs, routes, status calls and task identifiers remain correlation surfaces.
- **P6 Storage minimisation** — privileged stores require explicit purpose, retention, deletion and access rationale.
- **P8 User-visible disclosure context** — material privileged visibility should be reflected where relevant to authorization.

## Observer matrix

A deployment evidence package should maintain an observer matrix such as:

| Surface | Ordinary verifier | Operator | Auditor | Telemetry processor | Effective consequence |
|---|---|---|---|---|---|
| Pairwise subject identifier | yes | yes | maybe | maybe | pairwise only if privileged stores cannot join contexts |
| Relationship graph | partial | full | full/limited | no | relationship unlinkability constrained for privileged scope |
| Trust Task identifier | yes | yes | maybe | yes | cross-flow linkage possible if analytics reuses it |
| Status lookup | maybe | yes | logs | yes | verifier-holder interaction can become observable |

## Evidence expected

1. role and access inventory;
2. data stores visible to each privileged role;
3. join keys available across stores;
4. retention and deletion policies;
5. access-control and purpose limitation evidence;
6. administrative API inventory;
7. telemetry pipeline inventory;
8. negative test attempting graph reconstruction or cross-context joining;
9. scoped privacy result reflecting any residual privileged correlation.

## Adversarial tests

### PO-T1 — administrative graph reconstruction

Start from identifiers that are pairwise for ordinary verifiers and determine whether a privileged endpoint or database can map them to one subject or relationship graph. If yes, contextual privacy is at least `CONSTRAINED` for that observer scope.

### PO-T2 — telemetry join

Present independently privacy-preserving C1/C3 interactions and test whether telemetry fields, device identifiers, task IDs or timestamps let an analytics processor join them.

### PO-T3 — audit-purpose expansion

Determine whether data retained for narrowly stated audit purposes is queryable for unrelated relationship discovery. Broad queryability widens effective scope even when access is authenticated.

### PO-T4 — recovery operator correlation

Run recovery/migration and test whether the support path reveals or permanently indexes unrelated relationship contexts.

## Claim-scoping rule

DPIP should prefer statements such as:

```text
ordinary-verifier unlinkability: PASS
privileged-operator unlinkability: FAIL
contextual privacy: CONSTRAINED
```

over a single unqualified `unlinkable: true` assertion.

Access control can reduce risk; it does not make correlation capability disappear from the privacy model.
