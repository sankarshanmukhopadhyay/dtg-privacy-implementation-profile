import copy
import json
import unittest
from pathlib import Path

from scripts.validate_privacy_observability_contract import validate_result


FIXTURE_DIR = Path(__file__).parents[1] / "contracts" / "fixtures"


def load_fixture(name):
    return json.loads((FIXTURE_DIR / name).read_text(encoding="utf-8"))


def base_result():
    return load_fixture("privacy-observability-supported-ab.json")


class PrivacyObservabilityContractTests(unittest.TestCase):
    def test_canonical_fixture_matrix_validates(self):
        expected = {
            "privacy-observability-supported-ab.json": "supported",
            "privacy-observability-observed-correlation.json": "not-supported",
            "privacy-observability-evidence-incomplete.json": "evidence-incomplete",
            "privacy-observability-outside-threat-model.json": "outside-threat-model",
        }
        for name, result in expected.items():
            with self.subTest(name=name):
                doc = load_fixture(name)
                self.assertEqual(result, doc["result"])
                self.assertEqual([], validate_result(doc))

    def test_bounded_supported_ab_case(self):
        self.assertEqual([], validate_result(base_result()))

    def test_observed_correlation_cannot_support_privacy(self):
        doc = base_result()
        doc["correlation"] = {"signal": "found", "effective_join": True}
        doc["result"] = "supported"
        self.assertTrue(any("correlation" in e for e in validate_result(doc)))

    def test_unavailable_runtime_requires_evidence_incomplete(self):
        doc = base_result()
        doc["executed"] = False
        doc["result"] = "supported"
        self.assertTrue(any("evidence-incomplete" in e for e in validate_result(doc)))

    def test_privileged_outside_threat_model_is_explicit(self):
        self.assertEqual([], validate_result(load_fixture("privacy-observability-outside-threat-model.json")))

    def test_composed_weak_signals_forming_join_is_negative(self):
        self.assertEqual([], validate_result(load_fixture("privacy-observability-observed-correlation.json")))

    def test_local_result_must_not_claim_deployment_wide_unlinkability(self):
        doc = base_result()
        doc["unsupported_inference"] = []
        self.assertTrue(any("deployment-wide" in e for e in validate_result(doc)))

    def test_runtime_unavailable_fixture_cannot_be_promoted_to_supported(self):
        doc = load_fixture("privacy-observability-evidence-incomplete.json")
        promoted = copy.deepcopy(doc)
        promoted["result"] = "supported"
        self.assertTrue(any("evidence-incomplete" in e for e in validate_result(promoted)))


if __name__ == "__main__":
    unittest.main()
