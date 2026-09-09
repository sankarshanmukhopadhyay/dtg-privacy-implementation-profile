import json
import unittest
from pathlib import Path

from scripts.evaluate_privacy_observability import to_assessor_result


FIXTURE_DIR = Path(__file__).parents[1] / "contracts" / "fixtures"
RAHP_CONSUMER_KEYS = {
    "schema", "assessor", "assessment_id", "outcome", "reason_code",
    "evidence_used", "residual_risk", "action_required", "source_pins",
    "provenance", "details",
}


def fixture(name):
    return json.loads((FIXTURE_DIR / name).read_text(encoding="utf-8"))


class PrivacyObservabilitySpecialistReturnTests(unittest.TestCase):
    def test_supported_maps_to_bounded_pass(self):
        result = to_assessor_result(fixture("privacy-observability-supported-ab.json"))
        self.assertEqual("rahp-assessor-result/v1", result["schema"])
        self.assertEqual("PASS", result["outcome"])
        self.assertEqual("bounded-privacy-supported", result["reason_code"])
        self.assertIn("DPIP", result["assessor"])
        self.assertIn("deployment-wide unlinkability", result["residual_risk"])
        self.assertTrue(all(isinstance(item, str) and item for item in result["evidence_used"]))
        self.assertLessEqual(set(result), RAHP_CONSUMER_KEYS)
        self.assertIn("RAHP owns terminal assurance reconciliation", result["details"]["ownership_boundary"])

    def test_observed_correlation_maps_to_fail(self):
        result = to_assessor_result(fixture("privacy-observability-observed-correlation.json"))
        self.assertEqual("FAIL", result["outcome"])
        self.assertEqual("observed-correlation", result["reason_code"])

    def test_evidence_incomplete_maps_to_indeterminate(self):
        result = to_assessor_result(fixture("privacy-observability-evidence-incomplete.json"))
        self.assertEqual("INDETERMINATE", result["outcome"])
        self.assertEqual("evidence-incomplete", result["reason_code"])
        self.assertIn("do not infer PASS", result["action_required"])

    def test_outside_threat_model_maps_to_not_applicable(self):
        result = to_assessor_result(fixture("privacy-observability-outside-threat-model.json"))
        self.assertEqual("NOT_APPLICABLE", result["outcome"])
        self.assertEqual("outside-threat-model", result["reason_code"])


if __name__ == "__main__":
    unittest.main()
