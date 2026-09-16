import copy
import importlib.util
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "human_power_privacy.py"
FIXTURE = ROOT / "fixtures" / "human-power" / "interop-121-evidence.json"

spec = importlib.util.spec_from_file_location("human_power_privacy", SCRIPT)
mod = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(mod)


class HumanPowerPrivacyTests(unittest.TestCase):
    def setUp(self):
        self.package = json.loads(FIXTURE.read_text(encoding="utf-8"))

    def test_package_validates_and_is_synthetic(self):
        mod.validate_package(self.package)
        self.assertEqual(mod.evidence_maturity(self.package), "synthetic-pressure-test")

    def test_190_detects_bounded_disclosure_and_correlation_failures(self):
        result = mod.evaluate_compelled_disclosure(self.package)
        self.assertEqual(result["outcome"], "FAIL")
        self.assertIn("expanded-disclosure-exceeds-minimal-and-is-not-purpose-bound", result["reasons"])
        self.assertIn("stable-identifier-demand-expands-declared-correlation-scope", result["reasons"])
        self.assertIn("retention-expands-effective-scope-across-sessions", result["reasons"])
        self.assertFalse(result["deployment_claim_supported"])

    def test_190_preserves_governed_counter_cases(self):
        result = mod.evaluate_compelled_disclosure(self.package)
        counter = result["bounded_findings"]["counter_cases"]
        self.assertIn("purpose-bound-enhanced-assurance-preserved", counter)
        self.assertIn("governed-stable-account-scope-remains-aligned", counter)

    def test_190_does_not_infer_coercion(self):
        result = mod.evaluate_compelled_disclosure(self.package)
        self.assertEqual(result["bounded_findings"]["refusal_context"]["coercion_judgment"], "not-made-by-dpip")
        self.assertIn("coercion", result["authority_boundary"]["dpip_does_not_own"])

    def test_190_missing_required_observation_is_indeterminate(self):
        package = copy.deepcopy(self.package)
        for item in package["results"]:
            if item["case"]["id"] == "CORRELATION_CROSS_SESSION":
                item["evidence_state"] = "EVIDENCE_REQUIRED"
        result = mod.evaluate_compelled_disclosure(package)
        self.assertEqual(result["outcome"], "INDETERMINATE")
        self.assertIn("CORRELATION_CROSS_SESSION", result["residual"]["evidence_required_cases"])

    def test_191_observes_extra_feature_and_less_revealing_alternative(self):
        result = mod.evaluate_proxy_inference(self.package)
        findings = result["bounded_findings"]
        self.assertTrue(findings["observable_extra_feature"])
        self.assertEqual(findings["feature"], "community_membership")
        self.assertTrue(findings["controlled_outcome_difference"])
        self.assertTrue(findings["less_revealing_alternative_observed"])

    def test_191_remains_indeterminate_without_sensitive_inference_observation(self):
        result = mod.evaluate_proxy_inference(self.package)
        self.assertEqual(result["outcome"], "INDETERMINATE")
        self.assertIn("sensitive-or-social-inference-not-observed", result["reasons"])
        self.assertIn("cross-context-proxy-effect-not-observed", result["reasons"])
        self.assertFalse(result["deployment_claim_supported"])

    def test_191_does_not_classify_discrimination_or_legitimacy(self):
        result = mod.evaluate_proxy_inference(self.package)
        self.assertEqual(result["bounded_findings"]["discrimination_or_legitimacy_judgment"], "not-made-by-dpip")
        self.assertIn("discrimination", result["authority_boundary"]["dpip_does_not_own"])

    def test_governed_feature_counter_case_has_no_undeclared_feature(self):
        result = mod.evaluate_proxy_inference(self.package)
        self.assertFalse(result["bounded_findings"]["governed_counter_case_has_undeclared_features"])

    def test_missing_proxy_case_fails_closed(self):
        package = copy.deepcopy(self.package)
        package["results"] = [item for item in package["results"] if item["case"]["id"] != "DECISION_FEATURE_PRIMARY_ONLY"]
        package["case_count"] -= 1
        result = mod.evaluate_proxy_inference(package)
        self.assertEqual(result["outcome"], "INDETERMINATE")
        self.assertIn("DECISION_FEATURE_PRIMARY_ONLY", result["residual"]["missing_cases"])

    def test_schema_mismatch_is_rejected(self):
        package = copy.deepcopy(self.package)
        package["schema"] = "unexpected/v1"
        with self.assertRaises(ValueError):
            mod.validate_package(package)

    def test_bundle_returns_both_issue_results(self):
        bundle = mod.evaluate(self.package)
        self.assertEqual(bundle["schema"], "dpip-human-power-privacy-bundle/v1")
        self.assertEqual([r["dpip_issue"] for r in bundle["results"]], [190, 191])
        self.assertTrue(all(r["outcome"] in mod.OUTCOMES for r in bundle["results"]))


if __name__ == "__main__":
    unittest.main()
