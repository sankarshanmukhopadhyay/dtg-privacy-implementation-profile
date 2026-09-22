# Predicate-Defined Audience Privacy Pressure Test

## Purpose

A bounded-but-unenumerated audience creates a privacy question only when
membership establishment exposes or makes joinable information about the person
or relationship. Collective authority by itself is not an automatic DPIP
finding.

The synthetic fixture in `fixtures/predicate-audience/cases.json` distinguishes:

- raw membership disclosure and globally stable membership identifiers — privacy
  materiality is warranted and the bounded test fails;
- a proof that establishes only audience membership while keeping identifiers
  scoped to the audience — retained as the privacy-preserving counter-case;
- missing observability evidence — `INDETERMINATE`, never PASS;
- collective-authority semantics without a predicate-audience disclosure
  surface — not automatically a DPIP matter.

## Authority boundary

DPIP evaluates minimisation, observability, linkability and correlation. It does
not decide whether membership or a threshold establishes authorization. That
decision remains with the governing authority/policy layer and terminal
portfolio assurance remains with RAHP.
