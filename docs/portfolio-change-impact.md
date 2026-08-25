# Portfolio Change-Impact and DPIP Revalidation

DPIP records which external DTG repositories can affect specific interactions, requirements, tests, claims and reference flows. The purpose is to support portfolio monitoring and targeted revalidation without treating every upstream change as an automatic conformance failure.

## Model

Each dependency record identifies:

- repository and functional area;
- impact type: semantics, interface, construction, deployment, evidence, observer model or lifecycle;
- affected DPIP IDs;
- required response: `required`, `review-required`, `evidence-refresh` or `informational`.

## Interpretation

A repository change does **not** automatically invalidate DPIP conformance. Instead:

- `required` means the affected DPIP artifacts should be re-evaluated before relying on the prior result;
- `review-required` means maintainers should determine whether the change actually alters a DPIP assumption or boundary;
- `evidence-refresh` means the DPIP semantics can remain stable while construction/evidence provenance is refreshed;
- `informational` records a relationship that does not itself trigger revalidation.

## Portfolio-monitor output pattern

A monitor can consume `portfolio/change-impact.yaml` and produce a result such as:

```text
trustoverip/dtgwg-trust-tasks-spec changed
  impact: interface + lifecycle
  revalidation: required
  affected: C3-R2, C3-T4, C3-PC-2, C5-T6, RF-001, RF-003
```

The monitor should then mark the existing privacy assurance as **revalidation required**, not `FAIL`, until the affected DPIP tests are rerun or reviewed.

## Evidence refresh

The ZKP dependency illustrates a different case. A new proof construction or immutable test vector may improve the evidence supporting C3 without changing DPIP's construction-neutral privacy semantics. That dependency is therefore normally an `evidence-refresh` trigger.

## Expansion

The initial registry covers repositories already referenced by DPIP's current composed flows. As R-Cards, naming/discovery, VTA/HTX and other DTG portfolio components expose stable repository/specification interfaces, they should be added with the exact DPIP artifacts their changes can affect.
