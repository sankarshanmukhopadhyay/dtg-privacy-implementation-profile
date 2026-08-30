# DPIP release governance

DPIP uses semantic version tags (`vX.Y.Z`) as the authoritative release identity.

## Cadence

While DPIP is pre-1.0, the project runs a **monthly release-readiness review**. The scheduled GitHub Actions workflow opens an assigned review issue on the first day of each month. The review asks whether a coherent assurance-capability boundary has landed.

The calendar creates a decision checkpoint; it does **not** require an empty release. Releases may also be cut between monthly reviews when a coherent capability increment warrants one.

## Release execution

Releases are created only through the **Cut governed DPIP release** GitHub Actions workflow. The release lifecycle is deliberately split into candidate selection and publication:

1. identify the semantic version for a coherent capability boundary;
2. select an unused Indian lake codename from the pinned repository pool with `python scripts/release_governance.py select --version vX.Y.Z --persist` on a branch;
3. review and merge the resulting `config/release-codename-history.json` candidate binding;
4. record human release judgment for the already-known **version + codename + evidence**;
5. dispatch the release workflow;
6. the workflow validates semantic version syntax, repository assurance checks, pool/provenance/history policy, and the persisted binding;
7. publication refuses an existing tag/release and consumes the persisted codename rather than selecting a new one;
8. the semantic tag/GitHub Release is created only when dry-run mode is disabled.

A human therefore decides **whether and what to release**. Actions makes the mechanics reproducible and cannot silently rename an accepted candidate.

## Lake codenames

The authoritative codename pool remains `release/lake-codenames.txt`, derived from:

<https://en.wikipedia.org/wiki/List_of_lakes_of_India>

Additional machine-readable governance state is held in:

- `config/release-codename-policy.json` — provenance, identity boundary, and selection rules;
- `config/release-codename-history.json` — persisted `candidate` / `published` version-to-codename bindings.

The external page is **not scraped at release time**. Changes to the pool are ordinary reviewed repository changes. Unused names are preferred while available; reuse is currently forbidden. An existing semantic version binding is idempotent and must not be changed to a different codename.

The lake codename is presentation metadata only. It does not replace semantic versioning and has no effect on DPIP conformance, privacy claims, evidence, or assurance semantics.

## Visible judgment

A release-readiness decision should leave enough history to answer:

- Which assurance propositions and capabilities changed?
- What tests or pressure cases challenged those changes?
- What remains uncertain, constrained, or deferred?
- Which semantic version and codename were accepted?
- Why did the maintainer decide that the current repository state constitutes a coherent release boundary?

A release should not be used to hide unresolved assurance gaps. Where an `INDETERMINATE` result remains, release notes should state whether it is an accepted known limitation or a release blocker.
