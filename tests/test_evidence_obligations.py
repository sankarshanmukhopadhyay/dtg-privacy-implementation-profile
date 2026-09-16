import copy
import importlib.util
import json
import pathlib
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("evidence_obligations", ROOT / "scripts" / "evidence_obligations.py")
mod = importlib.util.module_from_spec(SPEC)
assert SPEC.loader
SPEC.loader.exec_module(mod)

FIXTURE = ROOT / "fixtures" / "human-power" / "dpip-191-evidence-obligations.json"


class EvidenceObligationTests(unittest.TestCase):
    def setUp(self):
        self.items = json.loads(FIXTURE.read_text())["obligations"]

    def test_reference_register_is_valid_and_blocked_without_target(self):
        result = mod.summarize(self.items)
        self.assertEqual(result["count"], 3)
        self.assertEqual(result["terminal_count"], 3)
        self.assertTrue(all(x["blocker"] == "NO_TARGET" for x in result["obligations"]))
        self.assertTrue(all(not x["interop_admissible"] for x in result["obligations"]))

    def test_duplicate_ids_are_rejected(self):
        with self.assertRaisesRegex(ValueError, "duplicate obligation id"):
            mod.summarize([self.items[0], copy.deepcopy(self.items[0])])

    def test_runtime_evidence_requires_bound_target_when_not_no_target(self):
        ob = copy.deepcopy(self.items[0])
        ob["access"] = {"status": "BLOCKED", "blocker": "OPERATOR_ACCESS_REQUIRED"}
        with self.assertRaisesRegex(ValueError, "E3\+ evidence requires"):
            mod.validate(ob)

    def test_available_evidence_cannot_have_blocker(self):
        ob = copy.deepcopy(self.items[0])
        ob["access"] = {"status": "AVAILABLE", "blocker": "NO_TARGET"}
        with self.assertRaisesRegex(ValueError, "available evidence"):
            mod.validate(ob)

    def test_synthetic_source_does_not_satisfy_runtime_contract(self):
        ob = copy.deepcopy(self.items[0])
        ob["supplier"] = {"role": "INTEROP_LAB", "evidence_source_class": "BLACK_BOX_RUNTIME"}
        ob["access"] = {"status": "AVAILABLE", "blocker": "NONE"}
        ob["target"] = None
        with self.assertRaisesRegex(ValueError, "E3\+ evidence requires"):
            mod.validate(ob)

    def test_interop_accepts_observable_bound_black_box_case(self):
        ob = copy.deepcopy(self.items[0])
        ob["supplier"] = {"role": "INTEROP_LAB", "evidence_source_class": "BLACK_BOX_RUNTIME"}
        ob["target"] = {"repository": "example/target", "revision": "0123456789abcdef"}
        ob["access"] = {"status": "AVAILABLE", "blocker": "NONE"}
        ok, reason = mod.can_interop_acquire(ob)
        self.assertTrue(ok)
        self.assertEqual(reason, "ADMISSIBLE")

    def test_operator_only_case_is_not_interop_admissible(self):
        ob = copy.deepcopy(self.items[0])
        ob["target"] = {"repository": "example/target", "revision": "0123456789abcdef"}
        ob["access"] = {"status": "BLOCKED", "blocker": "OPERATOR_ACCESS_REQUIRED"}
        ok, reason = mod.can_interop_acquire(ob)
        self.assertFalse(ok)
        self.assertEqual(reason, "OPERATOR_ACCESS_REQUIRED")

    def test_no_observation_surface_is_assurability_gap(self):
        ob = copy.deepcopy(self.items[0])
        ob["target"] = {"repository": "example/target", "revision": "0123456789abcdef"}
        ob["access"] = {"status": "BLOCKED", "blocker": "NO_OBSERVATION_SURFACE"}
        self.assertEqual(mod.assurability(ob), "ASSURABILITY_GAP")

    def test_residual_risk_acceptance_requires_authority(self):
        ob = copy.deepcopy(self.items[0])
        ob["state"] = "ACCEPTED_RESIDUAL_RISK"
        ob["residual_risk_acceptance"] = {"scope": "bounded proposition"}
        with self.assertRaisesRegex(ValueError, "requires authority and scope"):
            mod.validate(ob)

    def test_authorized_residual_risk_acceptance_is_valid(self):
        ob = copy.deepcopy(self.items[0])
        ob["state"] = "ACCEPTED_RESIDUAL_RISK"
        ob["residual_risk_acceptance"] = {"authority": "named-governance-authority", "scope": "bounded proposition"}
        mod.validate(ob)


if __name__ == "__main__":
    unittest.main()
