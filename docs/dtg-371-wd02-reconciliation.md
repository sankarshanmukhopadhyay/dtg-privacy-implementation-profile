# DTG #371 WD02 privacy reconciliation

The merged correlation-scope baseline changes source authority but does not satisfy DPIP runtime evidence requirements.

## Reconciled result

- `DTG-371-P02`: semantics confirmed; runtime disclosure/effective-correlation evidence still required.
- `DTG-371-P04`: independence of durability and scope confirmed; lifecycle implementation evidence still required.
- `DTG-371-P05`: original carriage-choice uncertainty is narrowed because the adopted direction carries scope in the credential. DPIP now evaluates the privacy consequences of that carriage rather than selecting a location.
- `DTG-371-P13`: declared/observable/effective separation remains a composition-level privacy proposition and requires fresh A/B observations.

The terminal privacy result remains **INDETERMINATE / AMBER**.

Upstream issue #38 is recorded as an external residual: enumerable digest-valued binders must be treated as potential join surfaces when present in tested compositions. DPIP does not prescribe the missing salt/blinding construction.

## Mutation boundary

`trustoverip/*` is read-only for this work. This reconciliation modifies only repositories owned by `sankarshanmukhopadhyay`.
