import unittest
from pathlib import Path

import yaml

ROOT = Path(__file__).parents[1]


class ComposedPrivacyEvidenceContractTests(unittest.TestCase):
    def setUp(self):
        self.registry = yaml.safe_load((ROOT / "portfolio" / "rahp-examination-bindings.yaml").read_text(encoding="utf-8"))
        self.requirements = yaml.safe_load((ROOT / "portfolio" / "evidence-requirements.yaml").read_text(encoding="utf-8"))["requirements"]
        self.bindings = yaml.safe_load((ROOT / "evidence" / "evidence-bindings.yaml").read_text(encoding="utf-8"))["bindings"]
        self.rules = yaml.safe_load((ROOT / "portfolio" / "evidence-acquisition-rules.yaml").read_text(encoding="utf-8"))["surface_rules"]
        self.collectors = yaml.safe_load((ROOT / "collectors" / "registry.yaml").read_text(encoding="utf-8"))["collectors"]

    def test_witness_scope_has_canonical_semantic_bindings(self):
        self.assertEqual(["C3", "C5"], self.registry["interaction_aliases"]["vta-witness-member-link"]["canonical"])
        self.assertEqual(
            ["RF-001", "RF-003"],
            self.registry["reference_flow_aliases"]["relationship credential -> witness/session -> member-linked presentation -> VWC -> retained evidence"]["canonical"],
        )
        self.assertEqual(
            ["C3-PC-2", "C5-PC-2"],
            self.registry["claim_aliases"]["pairwise-relationship-DID-remains-bounded-to-declared-context"]["canonical"],
        )
        self.assertEqual(
            ["C3-PC-5", "C5-PC-4"],
            self.registry["claim_aliases"]["retained-session-and-outcome-evidence-do-not-create-unintended-linkage"]["canonical"],
        )

    def test_directory_scope_has_canonical_semantic_bindings(self):
        aliases = self.registry["interaction_aliases"]
        self.assertEqual(["C3", "C4"], aliases["holder-directory-composition"]["canonical"])
        self.assertEqual(["C3", "C4"], aliases["community-directory-discovery"]["canonical"])
        self.assertEqual(["C4"], aliases["directory-disclosure-manifest"]["canonical"])
        self.assertEqual(["C5"], aliases["directory-admin-event-hints"]["canonical"])
        self.assertEqual(
            ["RF-002", "RF-001"],
            self.registry["reference_flow_aliases"]["private contact annotation -> directoryRef -> community directory entry -> client-local rendering"]["canonical"],
        )

    def test_generic_requirements_are_runtime_bound_and_privacy_safe(self):
        for rid in ("ER-COMPOSED-IDENTIFIER-AB", "ER-COMPOSED-RETENTION-AB"):
            with self.subTest(rid=rid):
                req = self.requirements[rid]
                self.assertEqual(["runtime-upstream-observation"], req["accepted_evidence_classes"])
                self.assertEqual("immutable-component-pins-required", req["source_pin_policy"])
                self.assertEqual("composed-privacy-runtime-observer-v1", req["producer_capability"])
                self.assertTrue(req["required_fields"])
                self.assertTrue(req["privacy_safe_capture_rule"])
                self.assertTrue(req["sufficiency_criterion"])
                self.assertTrue(req["rerun_trigger"])

    def test_composed_binding_resolves_both_generic_requirements(self):
        binding = next(x for x in self.bindings if x["id"] == "composed-identifier-and-retention-privacy")
        self.assertEqual(
            ["ER-COMPOSED-IDENTIFIER-AB", "ER-COMPOSED-RETENTION-AB"],
            binding["evidence_requirement_ids"],
        )

    def test_all_issue_300_and_301_surfaces_compile_to_collectors(self):
        surfaces = [
            "pairwise relationship DID",
            "member DID in memberPresentation",
            "counterparty DID",
            "witness DID",
            "session/thread identifier",
            "VWC and relationship-credential digests",
            "retained witness:session and witness:outcome evidence",
            "audit caller/context/session/witness fields",
            "community-scoped directory entryId",
            "directoryRef vtcDid plus entryId",
            "membership DID visibility",
            "group identifiers and membership",
            "directory search, facets and enumeration behavior",
            "statementDigest and join-manifest disclosure",
            "external-card publication",
            "admin-note existence",
            "administrator event timing/topic metadata",
        ]
        for surface in surfaces:
            with self.subTest(surface=surface):
                self.assertIn(surface, self.rules)
                collector = self.rules[surface]["collector"]
                self.assertIn(collector, self.collectors)

    def test_raw_directory_invariants_are_not_model_gaps(self):
        for raw in (
            "holder-private-annotations-do-not-leave-holder-context",
            "directory-nonvisibility-does-not-become-membership-or-relationship-oracle",
            "disclosure-purpose-and-audience-remain-bounded",
            "retained-or-derived-metadata-does-not-defeat-local-only-annotation-boundary",
        ):
            self.assertIn(raw, self.registry["invariant_aliases"])


if __name__ == "__main__":
    unittest.main()
