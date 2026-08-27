#!/usr/bin/env python3
import argparse
import copy
from pathlib import Path
import sys
import yaml

EXECUTABLE_RULES = Path("executable-evaluations/registry.yaml")


def load_yaml(path):
    with open(path, "r", encoding="utf-8") as fh:
        return yaml.safe_load(fh)


def registry_claim_rules(interaction_id):
    if not EXECUTABLE_RULES.exists():
        return {}
    registry = yaml.safe_load(EXECUTABLE_RULES.read_text(encoding="utf-8")) or {}
    interactions = registry.get("interactions", {}) or {}
    interaction = interactions.get(interaction_id, {}) or {}
    return interaction.get("claims", {}) or {}


def executable_claim_rules(profile):
    interaction_id = profile["interaction"]["id"]
    external = registry_claim_rules(interaction_id)
    inline = profile.get("executable_evaluation", {}).get("claims", {}) or {}
    # Inline rules remain authoritative where an interaction already owns them.
    return {**external, **inline}


def has_executable_evaluation(profile):
    return bool(executable_claim_rules(profile))


def claim_status(rule, vector, evidence):
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

    if kind == "cross_context_join_rejection":
        join_id = str(rule["join_id"])
        joins = [item for item in evidence.get("join_attempts", []) if str(item.get("id")) == join_id]
        if len(joins) != 1:
            return "INDETERMINATE", f"Exactly one join attempt {join_id!r} is required."
        join = joins[0]
        contexts = [str(item) for item in join.get("context_ids", [])]
        if len(contexts) < 2 or len(set(contexts)) != len(contexts):
            return "INDETERMINATE", "The join attempt must span distinct contexts."
        result = str(join.get("result", "not-run"))
        if result == "joined":
            return "FAIL", f"Cross-context join {join_id} succeeded across {', '.join(contexts)}."
        if result == "not-joined":
            return "PASS", f"Cross-context join {join_id} did not join the supplied unrelated contexts."
        return "INDETERMINATE", f"Cross-context join {join_id} was not executed to a conclusive result."

    raise ValueError(f"Unsupported evaluation rule: {kind}")


def evaluate(profile, evidence):
    interaction = profile["interaction"]
    if evidence.get("interaction_id") != interaction["id"]:
        raise ValueError("Evidence interaction_id does not match profile interaction id")

    tests = {test["id"]: test for test in profile["tests"]}
    rules = executable_claim_rules(profile)
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
                status, notes = claim_status(rules[claim_id], vector, evidence)
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


def claim_result(outputs, vector_id, claim_id):
    output = next(item for item in outputs if item.get("_vector_id") == vector_id)
    return next(item for item in output["claim_results"] if item["claim_id"] == claim_id)


def self_test():
    c3_profile = load_yaml("examples/c3-asymmetric-cross-community-relationship.yaml")
    c3_evidence = load_yaml("observations/c3-cross-context-retained-binder.yaml")
    assert has_executable_evaluation(c3_profile)
    c3_outputs = evaluate(c3_profile, c3_evidence)
    c3_result = claim_result(c3_outputs, "retained-binder-reuse", "C3-PC-2")
    assert c3_result["status"] == "FAIL", c3_result
    unrelated_c3 = claim_result(c3_outputs, "retained-binder-reuse", "C3-PC-1")
    assert unrelated_c3["status"] == "INDETERMINATE", unrelated_c3
    c3_counter = copy.deepcopy(c3_evidence)
    c3_counter["join_attempts"][0]["result"] = "not-joined"
    c3_counter["join_attempts"][0]["explanation"] = "Counter-case: context-bounded binders did not join."
    assert claim_result(evaluate(c3_profile, c3_counter), "retained-binder-reuse", "C3-PC-2")["status"] == "PASS"

    c5_profile = load_yaml("examples/c5-lifecycle-privacy-precedence.yaml")
    c5_evidence = load_yaml("observations/c5-stable-status-handle.yaml")
    assert has_executable_evaluation(c5_profile)
    c5_outputs = evaluate(c5_profile, c5_evidence)
    c5_result = claim_result(c5_outputs, "stable-status-handle-reuse", "C5-PC-2")
    assert c5_result["status"] == "FAIL", c5_result
    unrelated_c5 = claim_result(c5_outputs, "stable-status-handle-reuse", "C5-PC-1")
    assert unrelated_c5["status"] == "INDETERMINATE", unrelated_c5
    c5_counter = copy.deepcopy(c5_evidence)
    c5_counter["join_attempts"][0]["result"] = "not-joined"
    c5_counter["join_attempts"][0]["explanation"] = "Counter-case: context-bounded status handles did not join."
    assert claim_result(evaluate(c5_profile, c5_counter), "stable-status-handle-reuse", "C5-PC-2")["status"] == "PASS"

    print("PASS evaluate_interaction self-test")
    return 0


def canonical_yaml(data):
    return yaml.safe_dump(data, sort_keys=False, allow_unicode=True)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--profile")
    parser.add_argument("--evidence")
    parser.add_argument("--output-dir")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        return self_test()
    if not (args.profile and args.evidence and args.output_dir):
        parser.error("--profile, --evidence and --output-dir are required unless --self-test is used")

    profile = load_yaml(args.profile)
    outputs = evaluate(profile, load_yaml(args.evidence))
    output_dir = Path(args.output_dir)
    failures = []

    for result in outputs:
        vector_id = result.pop("_vector_id")
        path = output_dir / f"{profile['interaction']['id'].lower()}-{vector_id.lower()}.yaml"
        rendered = canonical_yaml(result)
        if args.check:
            if not path.exists() or yaml.safe_load(path.read_text(encoding="utf-8")) != yaml.safe_load(rendered):
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
