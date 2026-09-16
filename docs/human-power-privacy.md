# Human-power privacy evidence consumption

DPIP consumes the Trust Protocol Interop Lab human-power observation package to answer bounded privacy-depth questions while preserving the authority boundary between execution evidence, privacy judgment, and RAHP harm/assurance judgment.

## Authority and scope

The evidence path is:

```text
Interop Lab observation package
        |
        v
DPIP privacy-depth evaluation
        |
        v
RAHP human-power reconciliation
```

The Interop Lab establishes observable execution facts. DPIP may judge minimisation, observability, linkability/correlation, and privacy evidence sufficiency. RAHP retains coercion/power-asymmetry, consequential-use harm, and terminal portfolio assurance authority.

DPIP MUST NOT infer discrimination, legitimate consent, substantive decision fairness, coercion, or a portfolio assurance result from this evidence.

## Source pin

The repository fixture pins the completed Interop Lab #121 program:

- repository: `sankarshanmukhopadhyay/trust-protocol-interop-lab`
- merge revision: `1c3d3367329313cc0b7eb4a3bc972e221e4bc4d9`
- producer workflow run: `35049810013`
- artifact: `human-power-pressure-evidence`
- artifact digest: `sha256:df03e239254f786108ba41ba1c84c8d3f57197a480ec22c15587271b90638a07`

The checked-in fixture is a deterministic, reviewable projection of the cases needed by DPIP #190 and #191. It is not a substitute for the immutable workflow artifact; the pin above is the audit link to that producer epoch.

## Evidence maturity

The #121 cases are `synthetic-pressure-test` evidence. This distinction is normative for DPIP processing:

- synthetic evidence may establish that a privacy proposition and evaluator are executable and falsifiable;
- synthetic evidence may produce a bounded PASS, FAIL, or INDETERMINATE for the pressure-test proposition;
- synthetic evidence MUST NOT establish that any named production implementation behaves the same way;
- a target/deployment claim requires target-specific runtime evidence with implementation revision and observer provenance.

`deployment_claim_supported` is therefore false for the pinned #121 package.

## DPIP #190 — compelled expanded disclosure

DPIP evaluates the privacy-depth components of the pressure cases:

- disclosure beyond an available minimal proof;
- whether the extra disclosure is purpose-bound;
- stable-identifier demand versus declared scoped/pairwise correlation;
- observed cross-session retention versus declared correlation scope;
- governed enhanced-assurance and governed stable-account counter-cases;
- refusal consequences only as context for the privacy/minimisation question.

The pinned synthetic package establishes bounded negative privacy observations where expanded disclosure is not purpose-bound and where effective correlation expands beyond the declared scope. It deliberately does not turn service denial or refusal mechanics into a coercion judgment.

## DPIP #191 — proxy inference from trust metadata

The decision-feature pressure cases establish that:

- `community_membership` may be evaluated despite not being a declared decision feature;
- the controlled fixture records a different outcome when that extra metadata feature is present;
- a primary-eligibility-only path exists as a less-revealing comparison;
- a governed, declared and purpose-bound `service_region` feature exists as a counter-case.

They do **not** establish:

- that community membership maps to a sensitive or socially consequential characteristic;
- that such an inference is observable across unrelated contexts;
- that a target implementation performs such inference;
- discrimination or substantive decision illegitimacy.

Accordingly, DPIP #191 terminates `INDETERMINATE` with precise evidence requirements rather than inventing the missing inference.

## Reproduction

```bash
python -m unittest tests/test_human_power_privacy.py -v
python scripts/human_power_privacy.py \
  --input fixtures/human-power/interop-121-evidence.json \
  --output /tmp/dpip-human-power-result.json \
  --check
```

The generated bundle uses `dpip-human-power-privacy-bundle/v1`; each specialist result uses `dpip-human-power-privacy-result/v1`.

## Fail-closed rules

1. Package/result schema mismatch is rejected.
2. Missing required cases or `EVIDENCE_REQUIRED` cases produce DPIP `INDETERMINATE`.
3. Synthetic evidence never sets `deployment_claim_supported` true.
4. A governed counter-case is retained so the evaluator cannot encode simplistic rules such as “more disclosure always fails” or “stable identifiers always fail.”
5. DPIP #191 cannot promote observed metadata use into sensitive/social inference without evidence of that inference.
6. RAHP remains responsible for the final human-power/harm reconciliation.

## Extending to a target runtime

Do not create a generic runtime experiment merely because the synthetic program exists. A target-specific Interop Lab case should be opened only when a DPIP/RAHP result names a concrete missing observation, for example:

```text
implementation repository + immutable revision
observer identity/scope
specific decision or disclosure surface
required A/B or cross-context observation
expected evidence contract
owning DPIP/RAHP proposition
```

This keeps runtime acquisition demand-driven and auditable rather than speculative.
