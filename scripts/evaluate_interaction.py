#!/usr/bin/env python3
import argparse
from pathlib import Path
import sys
import yaml


def load_yaml(path):
    with open(path, "r", encoding="utf-8") as fh:
        return yaml.safe_load(fh)


def claim_status(rule, vector):
    kind = rule["rule"]
    if kind == "forbidden_disclosures":
        if "disclosed_fields" not in vector:
            return "INDETERMINATE", "Disclosure observations were not supplied."
        observed = set(vector.get("disclosed_fields") or [])
        forbidden = [field for field in rule.get("fields", []) if field in observed]
        if forbidden:
            return "FAIL", "Forbidden disclosure observed: " + ", ".join(forbidden)
        return "PASS", "No configured forbidden disclosure was observed."

    if kind == "context_replay_rejection":
        original_key = rule["original_field"]
        changed_key = rule["changed_field"]
        if original_key not in vector or changed_key not in vector:
            return "INDETERMINATE", "Original and changed-context verification observations are both required."
        if vector[original_key] is True and vector[changed_key] is False:
            return "PASS", "Original context verified and changed-context replay was rejected."
        if vector[original_key] is True and vector[changed_key] is True:
            return "FAIL", "Presentation verified after the relying context changed."
        return "INDETERMINATE", "The supplied context observations do not establish the claim."

    raise ValueError(f"Unsupported evaluation rule: {kind}")


def evaluate(profile, evidence):
    interaction = profile["interaction"]
    if evidence.get("interaction_id") != interaction["id"]:
        raise ValueError("Evidence interaction_id does not match profile interaction id")

    tests = {test["id"]: test for test in profile["tests"]}
    rules = profile.get("executable_evaluation", {}).get("claims", {})
    claims = {claim["id"]: claim for claim in profile.get("privacy_claims", [])}
    outputs = []

    for vector in evidence.get("vectors", []):
        test_id = vector["test_id"]
        if test_id not in tests:
            raise ValueError(f"Unknown test_id {test_id}")

        applicable = set(tests[test_id].get("claims", []))
        claim_results = []
        for claim_id in claims:
            if claim_id not in applicable:
                status = "INDETERMINATE"
                notes = "This vector does not supply evidence for this privacy claim."
            elif claim_id not in rules:
                status = "INDETERMINATE"
                notes = "No executable DPIP rule is available for this claim."
            else:
                status, notes = claim_status(rules[claim_id], vector)
            claim_results.append({
                "claim_id": claim_id,
                "status": status,
                "evidence": [f"vector:{vector['id']}"],
                "notes": notes,
            })

        evaluated = [result for result in claim_results if result["claim_id"] in applicable]
        if not evaluated:
            test_status = "INDETERMINATE"
        elif any(result["status"] == "FAIL" for result in evaluated):
            test_status = "FAIL"
        elif any(result["status"] == "INDETERMINATE" for result in evaluated):
            test_status = "INDETERMINATE"
        elif any(result["status"] == "CONSTRAINED" for result in evaluated):
            test_status = "CONSTRAINED"
        else:
            test_status = "PASS"

        schema_test_status = "PASS" if test_status == "CONSTRAINED" else test_status
        if schema_test_status not in {"PASS", "FAIL", "INDETERMINATE", "NOT_RUN"}:
            schema_test_status = "INDETERMINATE"

        outputs.append({
            "dpip_version": profile["dpip_version"],
            "interaction_id": interaction["id"],
            "interaction_version": interaction["version"],
            "implementation": evidence["implementation"],
            "human_summary": {
                "outcome": test_status,
                "explanation": f"DPIP-native evaluation of {vector['id']} using {test_id}.",
                "action": "Use only the evaluated claim results; unevaluated privacy properties remain outside this result.",
            },
            "test_results": [{
                "test_id": test_id,
                "status": schema_test_status,
                "evidence": [f"vector:{vector['id']}"],
                "notes": f"Source cryptographic verification observation: {vector.get('crypto_verified', 'not supplied')}.",
            }],
            "claim_results": claim_results,
            "evidence_provenance": evidence.get("provenance", []),
            "_vector_id": vector["id"],
        })

    return outputs


def canonical_yaml(data):
    return yaml.safe_dump(data, sort_keys=False, allow_unicode=True)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--profile", required=True)
    parser.add_argument("--evidence", required=True)
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    profile = load_yaml(args.profile)
    outputs = evaluate(profile, load_yaml(args.evidence))
    output_dir = Path(args.output_dir)
    failures = []

    for result in outputs:
        vector_id = result.pop("_vector_id")
        path = output_dir / f"{profile['interaction']['id'].lower()}-{vector_id.lower()}.yaml"
        rendered = canonical_yaml(result)
        if args.check:
            if not path.exists() or path.read_text(encoding="utf-8") != rendered:
                failures.append(str(path))
        else:
            output_dir.mkdir(parents=True, exist_ok=True)
            path.write_text(rendered, encoding="utf-8")

    if failures:
        print("Generated DPIP result mismatch:", *failures, sep="\n- ", file=sys.stderr)
        return 1

    print(f"Evaluated {len(outputs)} vector(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
