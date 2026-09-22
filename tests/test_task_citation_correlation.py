import importlib.util
import unittest
from pathlib import Path

MODULE = Path(__file__).parents[1] / "scripts" / "task_citation_correlation.py"
spec = importlib.util.spec_from_file_location("task_citation_correlation", MODULE)
module = importlib.util.module_from_spec(spec)
assert spec.loader
spec.loader.exec_module(module)


def package(vectors):
    return {
        "schema": "interop-task-citation-convergence-evidence/v1",
        "vectors": vectors,
    }


class TaskCitationCorrelationTests(unittest.TestCase):
    def test_fixture_only_correlation_remains_evidence_incomplete(self):
        result = module.to_privacy_observability(
            package(
                [
                    {
                        "id": "fixture",
                        "surface": "fixture",
                        "classification": "supported",
                        "correlation": "confirmed",
                    }
                ]
            )
        )
        self.assertEqual("evidence-incomplete", result["result"])
        self.assertFalse(result["executed"])
        self.assertEqual("not-tested", result["correlation"]["signal"])
        self.assertTrue(
            any("Fixture-only correlation" in item for item in result["residual_uncertainty"])
        )

    def test_observed_runtime_stable_join_is_bounded_negative_result(self):
        result = module.to_privacy_observability(
            package(
                [
                    {
                        "id": "runtime",
                        "surface": "target-runtime",
                        "classification": "supported",
                        "correlation": "confirmed",
                    }
                ]
            )
        )
        self.assertEqual("not-supported", result["result"])
        self.assertTrue(result["executed"])
        self.assertTrue(result["correlation"]["effective_join"])

    def test_observed_runtime_no_join_can_support_only_bounded_claim(self):
        result = module.to_privacy_observability(
            package(
                [
                    {
                        "id": "runtime",
                        "surface": "target-runtime",
                        "classification": "supported",
                        "correlation": "contradicted",
                    }
                ]
            )
        )
        self.assertEqual("supported", result["result"])
        self.assertTrue(result["executed"])
        self.assertFalse(result["correlation"]["effective_join"])
        self.assertIn(
            "deployment-wide unlinkability",
            result["unsupported_inference"],
        )

    def test_not_implemented_runtime_does_not_become_pass(self):
        result = module.to_privacy_observability(
            package(
                [
                    {
                        "id": "runtime",
                        "surface": "target-runtime",
                        "classification": "not-implemented",
                        "correlation": "unresolved",
                    }
                ]
            )
        )
        self.assertEqual("evidence-incomplete", result["result"])
        self.assertFalse(result["executed"])
        self.assertEqual("inconclusive", result["correlation"]["signal"])

    def test_unknown_package_schema_fails_closed(self):
        with self.assertRaises(ValueError):
            module.to_privacy_observability({"schema": "other/v1", "vectors": []})


if __name__ == "__main__":
    unittest.main()
