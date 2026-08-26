#!/usr/bin/env python3
"""Return completed RAHP-originated DPIP dispositions to their source issue."""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from typing import Any

import yaml

DEFAULT_DPIP_REPO = "sankarshanmukhopadhyay/dtg-privacy-implementation-profile"
DEFAULT_RAHP_REPO = "sankarshanmukhopadhyay/rahp-toolkit"
SOURCE_LABEL = "source:rahp"
COMPLETE_LABEL = "run:complete"
RAHP_COMPLETE = "assurance:dpip-complete"
RAHP_TRANSIENT = (
    "assurance:dpip-candidate",
    "assurance:dpip-requested",
    "assurance:dpip-open",
)
CONCLUSIONS = {"PASS", "FAIL", "CONSTRAINED", "INDETERMINATE", "NOT_APPLICABLE"}
DEFAULT_HUMAN_OUTCOMES = {
    "PASS": "Privacy expectation met",
    "FAIL": "Privacy expectation not met",
    "CONSTRAINED": "Privacy works, but with important limitations",
    "INDETERMINATE": "We do not have enough evidence to decide yet",
    "NOT_APPLICABLE": "This privacy test does not apply here",
}


def api(method: str, repo: str, path: str, token: str, payload: Any | None = None) -> Any:
    url = f"https://api.github.com/repos/{repo}/{path.lstrip('/')}"
    data = None if payload is None else json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=data,
        method=method,
        headers={
            "Accept": "application/vnd.github+json",
            "User-Agent": "dpip-rahp-return/1.0",
            "X-GitHub-Api-Version": "2022-11-28",
            "Authorization": f"Bearer {token}",
            **({"Content-Type": "application/json"} if data is not None else {}),
        },
    )
    with urllib.request.urlopen(req, timeout=30) as response:
        raw = response.read()
    return json.loads(raw) if raw else None


def yaml_blocks(text: str) -> list[dict[str, Any]]:
    blocks: list[dict[str, Any]] = []
    for match in re.finditer(r"```ya?ml\s*\n(.*?)```", text or "", re.DOTALL | re.IGNORECASE):
        try:
            parsed = yaml.safe_load(match.group(1))
        except yaml.YAMLError:
            continue
        if isinstance(parsed, dict):
            blocks.append(parsed)
    return blocks


def source_record(body: str) -> dict[str, Any]:
    for block in yaml_blocks(body):
        source = block.get("source")
        if isinstance(source, dict) and source.get("system") == "RAHP":
            return source
    raise ValueError("no machine-readable RAHP `source:` YAML block found")


def examination_record(comments: list[dict[str, Any]]) -> dict[str, Any]:
    for comment in reversed(comments):
        for block in yaml_blocks(comment.get("body") or ""):
            examination = block.get("dpip_examination")
            if isinstance(examination, dict):
                return examination
    raise ValueError("no structured `dpip_examination:` conclusion found in DPIP comments")


def validate_examination(examination: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    applicability = str(examination.get("applicability", "")).strip()
    if applicability not in {"applicable", "not-applicable"}:
        errors.append("applicability must be applicable or not-applicable")
    conclusion = str(examination.get("conclusion", "")).strip()
    if conclusion not in CONCLUSIONS:
        errors.append(f"unsupported conclusion {conclusion!r}")
    if applicability == "not-applicable" and conclusion != "NOT_APPLICABLE":
        errors.append("not-applicable intake must return NOT_APPLICABLE")
    if not str(examination.get("evidence_summary", "")).strip():
        errors.append("evidence_summary is required")
    if not str(examination.get("action", "")).strip():
        errors.append("action is required")
    human = examination.get("human_summary")
    if human is not None:
        if not isinstance(human, dict):
            errors.append("human_summary must be an object when present")
        else:
            for field in ("outcome", "explanation", "action"):
                if not str(human.get(field, "")).strip():
                    errors.append(f"human_summary.{field} is required when human_summary is present")
    return errors


def human_summary(examination: dict[str, Any]) -> dict[str, str]:
    supplied = examination.get("human_summary")
    if isinstance(supplied, dict):
        return {
            "outcome": str(supplied["outcome"]).strip(),
            "explanation": str(supplied["explanation"]).strip(),
            "action": str(supplied["action"]).strip(),
        }
    conclusion = str(examination["conclusion"])
    explanation = str(examination["evidence_summary"]).strip()
    residual = str(examination.get("residual_correlation", "")).strip()
    if residual:
        explanation = f"{explanation} Remaining limitation: {residual}"
    return {
        "outcome": DEFAULT_HUMAN_OUTCOMES[conclusion],
        "explanation": explanation,
        "action": str(examination["action"]).strip(),
    }


def has_label(issue: dict[str, Any], name: str) -> bool:
    return any(label.get("name") == name for label in issue.get("labels", []))


def get_candidates(dpip_repo: str, token: str, issue_number: int | None) -> list[dict[str, Any]]:
    if issue_number is not None:
        issue = api("GET", dpip_repo, f"issues/{issue_number}", token)
        return [issue] if issue else []
    labels = urllib.parse.quote(f"{SOURCE_LABEL},{COMPLETE_LABEL}", safe=",")
    return api("GET", dpip_repo, f"issues?state=all&labels={labels}&per_page=100", token) or []


def return_marker(dpip_repo: str, issue_number: int) -> str:
    return f"<!-- dpip-return:{dpip_repo}#{issue_number} -->"


def disposition_body(dpip_repo: str, issue: dict[str, Any], examination: dict[str, Any]) -> str:
    plain = human_summary(examination)
    payload: dict[str, Any] = {
        "dpip_disposition": {
            "dpip_issue": issue["number"],
            "applicability": examination["applicability"],
            "conclusion": examination["conclusion"],
            "human_summary": plain,
        }
    }
    disposition = payload["dpip_disposition"]
    mapping = (
        ("affected_interactions", "affected_interactions"),
        ("affected_reference_flows", "affected_reference_flows"),
        ("affected_claims", "affected_claims"),
        ("affected_invariants", "affected_invariants"),
    )
    for source_key, target_key in mapping:
        value = examination.get(source_key)
        if value:
            disposition[target_key] = value
    disposition["evidence_summary"] = examination["evidence_summary"]
    if examination.get("residual_correlation"):
        disposition["residual_correlation"] = examination["residual_correlation"]
    disposition["action"] = examination["action"]
    marker = return_marker(dpip_repo, issue["number"])
    return (
        f"{marker}\n## DPIP disposition returned\n\n"
        f"DPIP examination: {issue['html_url']}\n\n"
        f"### Plain-language result: {plain['outcome']}\n\n"
        f"{plain['explanation']}\n\n"
        f"**What to do:** {plain['action']}\n\n"
        "<details><summary>Structured DPIP disposition</summary>\n\n"
        f"```yaml\n{yaml.safe_dump(payload, sort_keys=False).rstrip()}\n```\n\n"
        "</details>\n\n"
        "DPIP owns the technical conclusion above; this comment closes only the DPIP handoff subflow. "
        "Any wider RAHP/security assessment remains independently governed."
    )


def process_issue(dpip_repo: str, default_rahp_repo: str, issue: dict[str, Any], dpip_token: str, rahp_token: str) -> bool:
    if not (has_label(issue, SOURCE_LABEL) and has_label(issue, COMPLETE_LABEL)):
        print(f"SKIP {dpip_repo}#{issue.get('number')}: not a completed RAHP-originated intake")
        return False
    source = source_record(issue.get("body") or "")
    rahp_repo = str(source.get("repository") or default_rahp_repo)
    rahp_issue = int(source["issue"])
    comments = api("GET", dpip_repo, f"issues/{issue['number']}/comments?per_page=100", dpip_token) or []
    examination = examination_record(comments)
    problems = validate_examination(examination)
    if problems:
        raise ValueError("; ".join(problems))
    marker = return_marker(dpip_repo, issue["number"])
    source_comments = api("GET", rahp_repo, f"issues/{rahp_issue}/comments?per_page=100", rahp_token) or []
    if any(marker in (comment.get("body") or "") for comment in source_comments):
        print(f"EXISTS return for {dpip_repo}#{issue['number']} on {rahp_repo}#{rahp_issue}")
    else:
        api("POST", rahp_repo, f"issues/{rahp_issue}/comments", rahp_token, {"body": disposition_body(dpip_repo, issue, examination)})
        print(f"RETURNED {dpip_repo}#{issue['number']} to {rahp_repo}#{rahp_issue}")
    api("POST", rahp_repo, f"issues/{rahp_issue}/labels", rahp_token, {"labels": [RAHP_COMPLETE]})
    for label in RAHP_TRANSIENT:
        try:
            api("DELETE", rahp_repo, f"issues/{rahp_issue}/labels/{urllib.parse.quote(label, safe='')}", rahp_token)
        except urllib.error.HTTPError as exc:
            if exc.code != 404:
                raise
    return True


def run(dpip_repo: str, rahp_repo: str, dpip_token: str, rahp_token: str, issue_number: int | None) -> int:
    failures = 0
    for issue in get_candidates(dpip_repo, dpip_token, issue_number):
        try:
            process_issue(dpip_repo, rahp_repo, issue, dpip_token, rahp_token)
        except Exception as exc:
            failures += 1
            print(f"FAIL {dpip_repo}#{issue.get('number')}: {exc}", file=sys.stderr)
    return 1 if failures else 0


def self_test() -> int:
    body = """```yaml
source:
  system: RAHP
  repository: example/rahp
  issue: 42
```"""
    assert source_record(body)["issue"] == 42
    comments = [{"body": """```yaml
dpip_examination:
  applicability: applicable
  conclusion: INDETERMINATE
  affected_interactions: [C3]
  evidence_summary: Runtime evidence is missing.
  residual_correlation: Envelope fingerprinting remains unresolved.
  action: Obtain a runtime trace before making the privacy claim.
  human_summary:
    outcome: We do not have enough evidence to decide yet
    explanation: The change is privacy-relevant, but the required runtime trace is missing.
    action: Capture the runtime trace and rerun this examination.
```"""}]
    examination = examination_record(comments)
    assert not validate_examination(examination)
    assert human_summary(examination)["outcome"].startswith("We do not")
    rendered = disposition_body("example/dpip", {"number": 7, "html_url": "https://example.invalid/7"}, examination)
    assert "Plain-language result" in rendered and "Structured DPIP disposition" in rendered
    bad = dict(examination)
    bad["applicability"] = "not-applicable"
    assert validate_examination(bad)
    print("PASS rahp_return self-test")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--issue-number", type=int, default=None)
    parser.add_argument("--dpip-repository", default=os.getenv("DPIP_REPOSITORY", DEFAULT_DPIP_REPO))
    parser.add_argument("--rahp-repository", default=os.getenv("RAHP_REPOSITORY", DEFAULT_RAHP_REPO))
    args = parser.parse_args()
    if args.self_test:
        return self_test()
    dpip_token = os.getenv("GITHUB_TOKEN", "")
    rahp_token = os.getenv("RAHP_HANDOFF_TOKEN", "")
    if not dpip_token:
        print("GITHUB_TOKEN is required", file=sys.stderr)
        return 2
    if not rahp_token:
        print("RAHP_HANDOFF_TOKEN is not configured; completed DPIP dispositions were not returned.")
        return 0
    return run(args.dpip_repository, args.rahp_repository, dpip_token, rahp_token, args.issue_number)


if __name__ == "__main__":
    raise SystemExit(main())
