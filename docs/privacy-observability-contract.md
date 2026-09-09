# Reusable privacy observability contract

`dpip-privacy-observability-result/v1` is the DPIP-owned, implementation-neutral semantic layer for privacy observation and experiment results.

The contract deliberately excludes generic producer identity, immutable source pins, execution identity, artifact integrity/provenance and freshness/invalidation. Those belong to RAHP's `rahp-evidence-producer-result/v1` envelope. A producer may therefore place a DPIP observability result inside the RAHP evidence observation payload without RAHP learning privacy-specific interpretation semantics.

The contract models observer planes, direct observables, derived/joinable signals, privilege assumptions, threat-model scope, comparison structure, correlation/effective joins, specialist result state, unsupported inference and residual uncertainty.

The existing `dpip-data-room-observability/v1` contract remains a compatibility/profile contract. Data Room E1–E6 continue to be profile instances while their reusable observer/experiment semantics are factored into this generic DPIP layer.

A bounded `supported` result never means deployment-wide unlinkability. An unexecuted experiment must return `evidence-incomplete`; observed correlation/effective join cannot support the privacy proposition; privileged observations outside the declared threat model must remain explicit.

The first Interop migration target is the current Data Room runtime producer. The Lab continues to own target-specific execution and raw observations; DPIP owns privacy interpretation; RAHP owns generic evidence validation and terminal assurance reconciliation.
