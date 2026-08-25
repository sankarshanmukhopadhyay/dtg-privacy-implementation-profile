# DPIP Reference Composed System

This directory contains a **non-normative integration hypothesis** used to pressure-test DPIP against a coherent DTG flow before every upstream DTG specification or implementation natively publishes DPIP metadata.

It is intentionally not a reference implementation of DTG and does not redefine DTG semantics. It is a test harness for composition.

## What this system is for

The reference system lets DPIP ask, across one end-to-end execution:

- which component owns each semantic step;
- what evidence crosses component boundaries;
- which identifiers, bindings, graph entries, status handles, transcripts, or retained records become observable;
- how declared, observable, and effective correlation scope differ;
- which DPIP interaction requirements/tests/claims apply;
- which assumptions are supported by current DTG artifacts and which remain unresolved;
- whether a gap belongs in DPIP or should be raised against an owning DTG repository.

## Governance rule

A passing reference flow means that DPIP can evaluate the stated integration hypothesis. It **does not** establish that the hypothetical behaviour is normative DTG behaviour.

Every flow step therefore distinguishes:

- `owner` — the DTG specification/component area that should own the semantics;
- `assumption_status` — whether the reference system is using confirmed, candidate, or unresolved semantics;
- `dpip_mappings` — the DPIP interactions/tests/claims exercised at that step.

When a flow exposes a missing semantic or interface requirement, the finding should identify its owner rather than silently adding the requirement to DPIP.

## Initial flow

`flows/rf-001-relationship-establishment-and-proof.yaml` composes a relationship lifecycle across credential/relationship semantics, wallet/VTA behaviour, Trust Task-like exchange, privacy-preserving proof, verifier policy, graph/publication behaviour, and retained state.

It deliberately includes an asymmetric case where one relationship half is public/correlatable and the reciprocal half is pairwise/private. This makes the flow suitable for exercising C1-C3, especially C3's scoped privacy and effective-correlation model.
