import unittest

from scripts.validate_privacy_observability_contract import validate_result


def base_result():
    return {
        "schema": "dpip-privacy-observability-result/v1",
        "experiment": {
            "id": "privacy-ab-unlinkability",
            "privacy_proposition": "Repeated interactions should not expose a stable join at the declared observer planes.",
            "comparison": {"kind": "A/B", "scenarios": ["A", "B"]},
            "required_observer_planes": ["host", "verifier"],
            "minimum_evidence_class": "runtime-observation",
            "reproducibility": "source-pinned"
        },
        "observer_planes": [
            {
                "id": "host",
                "direct_observables": ["request timing"],
                "derived_or_joinable": [],
                "privilege": "ordinary",
                "threat_model": "in-scope"
            },
            {
                "id": "verifier",
                "direct_observables": ["presented claims"],
                "derived_or_joinable": [],
                "privilege": "ordinary",
                "threat_model": "in-scope"
            }
        ],
        "correlation": {"signal": "not-found", "effective_join": False},
        "result": "supported",
        "executed": True,
        "unsupported_inference": ["deployment-wide unlinkability"],
        "residual_uncertainty": ["network observer not measured"]
    }


class PrivacyObservabilityContractTests(unittest.TestCase):
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
        doc = base_result()
        doc["observer_planes"].append({
            "id": "deployment-privileged",
            "direct_observables": ["raw service logs"],
            "derived_or_joinable": ["account join"],
            "privilege": "privileged",
            "threat_model": "outside"
        })
        doc["result"] = "outside-threat-model"
        self.assertEqual([], validate_result(doc))

    def test_composed_weak_signals_forming_join_is_negative(self):
        doc = base_result()
        doc["observer_planes"][0]["derived_or_joinable"] = ["coarse timing bucket"]
        doc["observer_planes"][1]["derived_or_joinable"] = ["coarse presentation class"]
        doc["correlation"] = {"signal": "found", "effective_join": True, "composition": ["host", "verifier"]}
        doc["result"] = "not-supported"
        self.assertEqual([], validate_result(doc))

    def test_local_result_must_not_claim_deployment_wide_unlinkability(self):
        doc = base_result()
        doc["unsupported_inference"] = []
        self.assertTrue(any("deployment-wide" in e for e in validate_result(doc)))


if __name__ == "__main__":
    unittest.main()
