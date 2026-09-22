import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "predicate_audience_privacy.py"
FIXTURE = ROOT / "fixtures" / "predicate-audience" / "cases.json"

spec = importlib.util.spec_from_file_location("predicate_audience_privacy", SCRIPT)
mod = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(mod)


def cases():
    payload = json.loads(FIXTURE.read_text(encoding="utf-8"))
    return {case["id"]: case for case in payload["cases"]}


def test_raw_membership_and_global_identifier_fail_privacy_boundary():
    result = mod.evaluate(cases()["PA-RAW-MEMBERSHIP-CORRELATION"])
    assert result["outcome"] == "FAIL"
    assert "raw-membership-disclosed" in result["reasons"]
    assert "identifier-correlation-scope-exceeds-required-audience" in result["reasons"]


def test_scoped_privacy_preserving_membership_proof_is_retained_as_counter_case():
    result = mod.evaluate(cases()["PA-SCOPED-PROOF"])
    assert result["outcome"] == "PASS"
    assert result["materiality"] == "warranted"


def test_missing_observability_evidence_remains_indeterminate():
    result = mod.evaluate(cases()["PA-OBSERVABILITY-MISSING"])
    assert result["outcome"] == "INDETERMINATE"


def test_collective_authority_alone_does_not_auto_invoke_privacy_finding():
    result = mod.evaluate(cases()["PA-COLLECTIVE-AUTHORITY-ONLY"])
    assert result["outcome"] == "NOT_APPLICABLE"
    assert result["materiality"] == "not-automatic"


def test_dpip_does_not_make_authorization_decision():
    source = SCRIPT.read_text(encoding="utf-8")
    assert "does not determine whether collective authority or audience membership grants" in source
