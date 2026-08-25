# DPIP Specification Documents

## Implementer entry point

Use `dpip-v0.1-draft.md` as the current structured specification draft. It separates normative composition requirements from informative architecture and deployment guidance while preserving stable DPIP identifiers and the machine-readable readiness gate.

## Supporting documents

- `dpip-concept.md` — architectural rationale, original development baseline and evolution history.
- `../examples/` — canonical interaction requirements/tests (C1-C5).
- `../reference-system/` — non-normative composed reference flows and findings.
- `../docs/deployment-guide/` — implementer/deployer guidance.
- `../schema/` — machine-readable normative formats.
- `../results/` — conformance-result fixtures.
- `../evidence/` — external evidence bindings.
- `../readiness/v0.1.yaml` — authoritative release-readiness state.

## Normative versus informative

The v0.1 draft marks sections explicitly. Canonical YAML interaction requirements and validated schemas are part of the current executable profile baseline. Reference flows, concept/history documents and deployment examples remain informative unless a normative requirement explicitly references them.

## Release rule

The existence of `dpip-v0.1-draft.md` does not mean v0.1 is released. Promotion to v0.1 requires `readiness/v0.1.yaml` to report a ready state under CI validation.
