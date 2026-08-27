# DPIP release governance

DPIP uses semantic version tags (`vX.Y.Z`) as the authoritative release identity.

## Cadence

While DPIP is pre-1.0, the project runs a **monthly release-readiness review**. The scheduled GitHub Actions workflow opens an assigned review issue on the first day of each month. The review asks whether a coherent assurance-capability boundary has landed.

The calendar creates a decision checkpoint; it does **not** require an empty release. Releases may also be cut between monthly reviews when a coherent capability increment warrants one.

## Release execution

Releases are created only through the **Cut governed DPIP release** GitHub Actions workflow. The workflow:

1. validates semantic version syntax;
2. runs the repository's full validation and assurance self-tests;
3. refuses an already existing tag;
4. selects an Indian lake codename from the pinned repository pool;
5. prefers an unused codename while unused names remain;
6. records the selected codename, target SHA, validation status, and human release judgment in the GitHub Release;
7. creates the semantic tag/release only when dry-run mode is disabled.

A human therefore decides **whether and what to release**. The workflow makes the release mechanics reproducible.

## Lake codenames

The codename pool is maintained at `release/lake-codenames.txt` and is derived from:

<https://en.wikipedia.org/wiki/List_of_lakes_of_India>

The external page is **not scraped at release time**. This prevents network availability or later edits to the source page from changing a release decision. Changes to the codename pool are ordinary reviewed repository changes.

The lake codename is presentation metadata only. It does not replace semantic versioning and has no effect on DPIP conformance, privacy claims, evidence, or assurance semantics.

## Visible judgment

A release-readiness decision should leave enough history to answer:

- Which assurance propositions and capabilities changed?
- What tests or pressure cases challenged those changes?
- What remains uncertain, constrained, or deferred?
- Why did the maintainer decide that the current repository state constitutes a coherent release boundary?

A release should not be used to hide unresolved assurance gaps. Where an `INDETERMINATE` result remains, release notes should state whether it is an accepted known limitation or a release blocker.
