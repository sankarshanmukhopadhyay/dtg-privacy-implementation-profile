#!/usr/bin/env python3
"""Admit valid RAHP-originated DPIP requests without prejudging privacy results."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from typing import Any

import yaml

DEFAULT_REPO = "sankarshanmukhopadhyay/dtg-privacy-implementation-profile"
SOURCE_LABEL = "source:rahp"
REQUESTED = "run:requested"
IN_PROGRESS = "run:in-progress"


def api(method: str, repo: str, path: str, token: str, payload: Any | None = None) -> Any:
    url = f"https://api.github.com/repos/{repo}/{path.lstrip('/')}"
    data = None if payload is None else json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=data,
        method=method,
        headers={
            "Accept": "application/vnd.github+json",
            "User-Agent": "dpip-rahp-intake/1.0",
            "X-GitHub-Api-Version": "2022-11-28",
            "Authorization": f"Bearer {token}",
            **({"Content-Type": "application/json"} if data is not None else {}),
        },
    )
    with urllib.request.urlopen(req, timeout=30) as response:
        raw = response.read()
    return json.loads(raw) if raw else None


def yaml_blocks(body: str) -> list[dict[str, Any]]:
    blocks: list[dict[str, Any]] = []
    for match in re.finditer(r"```ya?ml\s*\n(.*?)```", body or "", re.DOTALL | re.IGNORECASE):
        try:
            value = yaml.safe_load(match.group(1))
        except yaml.YAMLError:
            continue
        if isinstance(value, dict):
            blocks.append(value)
    return blocks


def intake_payload(body: str) -> tuple[dict[str, Any], dict[str, Any]]:
    source: dict[str, Any] | None = None
    requested: dict[str, Any] | None = None
    for block in yaml_blocks(body):
        if isinstance(block.get("source"), dict):
            source = block["source"]
        if isinstance(block.get("requested_examination"), dict):
            requested = block["requested_examination"]
    if source is None:
        raise ValueError("missing machine-readable `source:` YAML block")
    if requested is None:
        raise ValueError("missing machine-readable `requested_examination:` YAML block")
    return source, requested


def validate(source: dict[str, Any], requested: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if source.get("system") != "RAHP":
        errors.append("source.system must be RAHP")
    for key in ("repository", "issue"):
        if not source.get(key):
            errors.append(f"source.{key} is required")
    changed = source.get("changed_artifact")
    if not isinstance(changed, dict):
        errors.append("source.changed_artifact must be a mapping")
    else:
        for key in ("repository", "revision"):
            if not str(changed.get(key, "")).strip():
                errors.append(f"source.changed_artifact.{key} is required")

    targets: list[str] = []
    for key in ("interactions", "reference_flows", "invariants", "claims"):
        value = requested.get(key, [])
        if value is not None and not isinstance(value, list):
            errors.append(f"requested_examination.{key} must be a list")
        elif isinstance(value, list):
            targets.extend(str(item).strip() for item in value if str(item).strip())
    if not targets:
        errors.append("requested_examination must identify at least one interaction, reference flow, invariant, or claim")
    if not str(requested.get("question", "")).strip():
        errors.append("requested_examination.question is required")
    return errors


def admission_identity(issue_number: int, source: dict[str, Any], requested: dict[str, Any]) -> tuple[str, str]:
    material = {"source": source, "requested_examination": requested}
    digest = hashlib.sha256(json.dumps(material, sort_keys=True, separators=(",", ":")).encode()).hexdigest()[:16]
    return f"<!-- dpip-rahp-admission:{issue_number}:{digest} -->", digest


def labels(issue: dict[str, Any]) -> set[str]:
    return {str(item.get("name")) for item in issue.get("labels", [])}


def list_requested(repo: str, token: str) -> list[dict[str, Any]]:
    label = urllib.parse.quote(f"{SOURCE_LABEL},{REQUESTED}", safe=",")
    return api("GET", repo, f"issues?state=open&labels={label}&per_page=100", token) or []


def comments(repo: str, number: int, token: str) -> list[dict[str, Any]]:
    return api("GET", repo, f"issues/{number}/comments?per_page=100", token) or []


def post_once(repo: str, number: int, marker: str, body: str, token: str) -> None:
    if any(marker in (item.get("body") or "") for item in comments(repo, number, token)):
        return
    api("POST", repo, f"issues/{number}/comments", token, {"body": f"{marker}\n{body}"})


def admit(repo: str, issue: dict[str, Any], token: str) -> None:
    number = int(issue["number"])
    try:
        source, requested = intake_payload(issue.get("body") or "")
        problems = validate(source, requested)
        marker, digest = admission_identity(number, source, requested)
        if problems:
            post_once(
                repo,
                number,
                marker,
                "## DPIP intake admission blocked\n\n"
                + "The request remains `run:requested`; no privacy conclusion has been made.\n\n"
                + "Problems:\n"
                + "\n".join(f"- {p}" for p in problems),
                token,
            )
            print(f"BLOCKED #{number}: {'; '.join(problems)}")
            return

        requested_targets = {
            key: requested.get(key, [])
            for key in ("interactions", "reference_flows", "invariants", "claims", "suspected_surfaces")
            if requested.get(key)
        }
        admission = {
            "dpip_admission": {
                "status": "admitted",
                "intake_digest": digest,
                "source_system": "RAHP",
                "requested_scope": requested_targets,
                "question": requested["question"],
                "next_state": "run:in-progress",
                "privacy_judgment": "not-made",
                "next_action": "DPIP applicability, profile/claim binding, evidence selection, and scoped examination",
            }
        }
        post_once(
            repo,
            number,
            marker,
            "## DPIP intake admitted\n\n"
            "The RAHP referral is structurally sufficient to begin DPIP examination. Admission validates the request boundary only; it does **not** establish applicability, evidence sufficiency, or a PASS/FAIL result.\n\n"
            f"```yaml\n{yaml.safe_dump(admission, sort_keys=False).rstrip()}\n```",
            token,
        )
        api("POST", repo, f"issues/{number}/labels", token, {"labels": [IN_PROGRESS]})
        try:
            api("DELETE", repo, f"issues/{number}/labels/{urllib.parse.quote(REQUESTED, safe='')}", token)
        except urllib.error.HTTPError as exc:
            if exc.code != 404:
                raise
        print(f"ADMITTED #{number}")
    except Exception as exc:
        marker = f"<!-- dpip-rahp-admission-error:{number} -->"
        post_once(
            repo,
            number,
            marker,
            "## DPIP intake admission blocked\n\n"
            f"The request remains `run:requested`; no privacy conclusion has been made.\n\nError: `{exc}`",
            token,
        )
        print(f"BLOCKED #{number}: {exc}", file=sys.stderr)


def run(repo: str, token: str, issue_number: int | None = None) -> int:
    if issue_number is not None:
        issue = api("GET", repo, f"issues/{issue_number}", token)
        if not issue or issue.get("pull_request"):
            return 0
        if not {SOURCE_LABEL, REQUESTED}.issubset(labels(issue)):
            print(f"SKIP #{issue_number}: not a source:rahp + run:requested intake")
            return 0
        admit(repo, issue, token)
        return 0
    for issue in list_requested(repo, token):
        if not issue.get("pull_request"):
            admit(repo, issue, token)
    return 0


def self_test() -> int:
    body = """```yaml
source:
  system: RAHP
  repository: example/rahp
  issue: 1
  changed_artifact:
    repository: example/spec
    revision: abc123
```
```yaml
requested_examination:
  interactions: [C3]
  invariants: [P2]
  question: Does the composed interaction preserve the declared privacy scope?
```"""
    source, requested = intake_payload(body)
    assert validate(source, requested) == []
    marker, digest = admission_identity(1, source, requested)
    assert digest in marker
    bad = dict(requested)
    bad["question"] = ""
    assert "requested_examination.question is required" in validate(source, bad)
    print("PASS rahp_intake self-test")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--issue-number", type=int)
    args = parser.parse_args()
    if args.self_test:
        return self_test()
    token = os.environ.get("GITHUB_TOKEN", "")
    if not token:
        sys.exit("GITHUB_TOKEN is required")
    repo = os.environ.get("DPIP_REPOSITORY", DEFAULT_REPO)
    return run(repo, token, args.issue_number)


if __name__ == "__main__":
    raise SystemExit(main())
