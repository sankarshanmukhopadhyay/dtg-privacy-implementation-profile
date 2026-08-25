#!/usr/bin/env python3
from __future__ import annotations
import json
import sys
from pathlib import Path
import yaml
from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
FINDING_SCHEMA = json.loads((ROOT / "schema" / "finding.schema.json").read_text())


def main() -> int:
    failed = False
    registry_paths = sorted((ROOT / "reference-system" / "findings").glob("*.yaml"))
    all_findings: dict[str, dict] = {}
    validator = Draft202012Validator(FINDING_SCHEMA)

    for path in registry_paths:
        data = yaml.safe_load(path.read_text())
        errors = [e.message for e in validator.iter_errors(data)]
        for finding in data.get("findings", []):
            fid = finding["id"]
            if fid in all_findings:
                errors.append(f"duplicate finding id {fid}")
            all_findings[fid] = finding
        if errors:
            failed = True
            print(f"FAIL {path.relative_to(ROOT)}")
            for error in errors:
                print(f"  - {error}")
        else:
            print(f"PASS {path.relative_to(ROOT)}")

    readiness_path = ROOT / "readiness" / "v0.1.yaml"
    readiness = yaml.safe_load(readiness_path.read_text())
    problems: list[str] = []
    statuses = {c["id"]: c["status"] for c in readiness.get("criteria", [])}
    for criterion in readiness.get("criteria", []):
        for fid in criterion.get("blocking_findings", []):
            if fid not in all_findings:
                problems.append(f"{criterion['id']}: unknown blocking finding {fid}")
    for fid in readiness.get("release_gate", {}).get("current_blockers", []):
        finding = all_findings.get(fid)
        if not finding:
            problems.append(f"release gate: unknown blocker {fid}")
        elif finding.get("status") == "resolved":
            problems.append(f"release gate: resolved finding {fid} cannot remain a current blocker")

    blocking_open = [
        f["id"] for f in all_findings.values()
        if f.get("severity") == "blocking" and f.get("status") not in {"resolved", "accepted-risk"}
    ]
    declared_blockers = set(readiness.get("release_gate", {}).get("current_blockers", []))
    for fid in blocking_open:
        if fid not in declared_blockers:
            problems.append(f"open blocking finding {fid} missing from release_gate.current_blockers")

    if readiness.get("status") == "ready":
        if blocking_open:
            problems.append("status cannot be ready while blocking findings remain open")
        if any(v == "FAIL" for v in statuses.values()):
            problems.append("status cannot be ready while a readiness criterion is FAIL")

    if problems:
        failed = True
        print(f"FAIL {readiness_path.relative_to(ROOT)}")
        for problem in problems:
            print(f"  - {problem}")
    else:
        print(f"PASS {readiness_path.relative_to(ROOT)}")
        print(f"v0.1 status: {readiness.get('status')}; blockers: {', '.join(blocking_open) or 'none'}")

    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
