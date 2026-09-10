# Public repository baseline

This record captures the repository-owned controls reviewed under issue #176. It is repository assurance evidence, not external certification.

| Control | State | Evidence | Residual risk |
|---|---|---|---|
| Purpose, maturity, adopter paths and authority boundaries | PASS | `README.md`, `docs/`, `readiness/v0.1.yaml` | None identified in this baseline pass. |
| Explicit repository license | PASS | `LICENSE`, README `License` section | Apache-2.0 applies repository-wide to repository-owned artifacts; separately identified third-party material retains its original terms. |
| Security reporting and supported versions | PASS | `SECURITY.md` | GitHub private-vulnerability-reporting enablement remains hosted setting evidence. |
| Contribution/community/support guidance | PASS | `CONTRIBUTING.md`, `SUPPORT.md`, `CODE_OF_CONDUCT.md`, issue + PR templates | None identified. |
| Dependency update management | PASS | `.github/dependabot.yml` | Hosted Dependabot enablement remains platform evidence. |
| Default-branch governance | PASS | active `protect-main` observed 2026-09-05: PRs, resolved conversations, linear history, deletion/non-fast-forward protection, strict required `validate` check, no bypass actors | Required check name must remain aligned with actual CI. |
| Evidence / privacy fail-safe semantics | PASS | README + contracts/evidence/results/readiness surfaces | Workflow green is not privacy PASS; missing/inadmissible evidence remains INDETERMINATE. |
| Release/readiness provenance | PASS | `readiness/v0.1.yaml`, release docs | Publication remains explicit maintainer judgment. |
| Documentation and executable examples | PASS | `docs/`, `examples/`, `executable-evaluations/`, workflows | None identified in this baseline pass. |
| Authority boundary | PASS | README `What DPIP owns — and does not own` | DPIP does not redefine component or deployment/governance authority. |

## Completion boundary

Repository-owned governance/community-health gaps identified by issue #176 are now closed. The licensing residual is resolved by the repository-wide Apache-2.0 decision recorded under issue #201; this PASS is repository evidence, not external certification or a claim about separately licensed third-party material.