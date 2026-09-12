import unittest
from pathlib import Path

import yaml


ROOT = Path(__file__).parents[1]


class VettedAdmissionEvidenceContractTests(unittest.TestCase):
    def setUp(self):
        self.registry = yaml.safe_load((ROOT / "portfolio" / "rahp-examination-bindings.yaml").read_text(encoding="utf-8"))
        self.requirements = yaml.safe_load((ROOT / "portfolio" / "evidence-requirements.yaml").read_text(encoding="utf-8"))["requirements"]
        self.bindings = yaml.safe_load((ROOT / "evidence" / "evidence-bindings.yaml").read_text(encoding="utf-8"))["bindings"]

    def test_issue_250_raw_interactions_are_canonically_bound(self):
        expected = {
            "pre-admission-manifest-discovery": ["C4"],
            "vetter-directory-discovery": ["C3", "C4"],
            "vetting-request-and-ticket-exchange": ["C3"],
            "vetter-grant-status-check": ["C5"],
        }
        aliases = self.registry["interaction_aliases"]
        for raw, canonical in expected.items():
            with self.subTest(raw=raw):
                self.assertEqual(canonical, aliases[raw]["canonical"])

    def test_issue_250_raw_reference_flows_are_canonically_bound(self):
        expected = {
            "active persona DID -> community manifest request -> pre-admission community observation": ["RF-002"],
            "vetter directory query -> DID/profile/location/contact/event metadata -> applicant UI": ["RF-002", "RF-001"],
            "out-of-band vetting ticket -> QR/link carrying ticket id and secret -> vetting request": ["RF-001"],
            "verified vetter grant -> credentialStatus URL -> bounded HTTPS status fetch": ["RF-003"],
        }
        aliases = self.registry["reference_flow_aliases"]
        for raw, canonical in expected.items():
            with self.subTest(raw=raw):
                self.assertEqual(canonical, aliases[raw]["canonical"])

    def test_vetting_binding_resolves_named_evidence_contracts(self):
        binding = next(item for item in self.bindings if item["id"] == "vetted-admission-privacy")
        expected = [
            "ER-VETTING-DISCOVERY-AB",
            "ER-VETTER-DIRECTORY-AB",
            "ER-STATUS-AB",
            "ER-VETTING-TICKET-AB",
            "ER-VETTING-RETENTION-AB",
        ]
        self.assertEqual(expected, binding["evidence_requirement_ids"])
        for requirement_id in expected:
            self.assertIn(requirement_id, self.requirements)

    def test_new_runtime_requirements_are_privacy_safe_and_rerunnable(self):
        for requirement_id in (
            "ER-VETTING-DISCOVERY-AB",
            "ER-VETTER-DIRECTORY-AB",
            "ER-VETTING-TICKET-AB",
            "ER-VETTING-RETENTION-AB",
        ):
            with self.subTest(requirement_id=requirement_id):
                requirement = self.requirements[requirement_id]
                self.assertEqual(["runtime-upstream-observation"], requirement["accepted_evidence_classes"])
                self.assertEqual("immutable-component-pins-required", requirement["source_pin_policy"])
                self.assertTrue(requirement["required_fields"])
                self.assertTrue(requirement["privacy_safe_capture_rule"])
                self.assertTrue(requirement["sufficiency_criterion"])
                self.assertTrue(requirement["rerun_trigger"])

    def test_ticket_evidence_never_requires_raw_secret_retention(self):
        requirement = self.requirements["ER-VETTING-TICKET-AB"]
        self.assertIn("Never persist raw ticket secrets", requirement["privacy_safe_capture_rule"])
        self.assertNotIn("ticket_secret", requirement["required_fields"])


if __name__ == "__main__":
    unittest.main()
