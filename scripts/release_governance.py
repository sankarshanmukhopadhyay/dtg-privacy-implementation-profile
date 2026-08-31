#!/usr/bin/env python3
"""Enforce DPIP semantic-version and persisted lake-codename release governance.

Operational contract:
- Validates the codename pool, policy/history, semantic version requests, and persisted version-to-codename binding.
- May generate/select governance metadata when explicitly invoked by the governed release process.
- Release metadata has no privacy-assurance meaning and cannot alter DPIP examination outcomes.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import secrets
import sys
from pathlib import Path

POOL = Path("release/lake-codenames.txt")
POLICY = Path("config/release-codename-policy.json")
HISTORY = Path("config/release-codename-history.json")
VERSION_RE = re.compile(r"^v(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)$")


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def load_pool(path: Path = POOL) -> list[str]:
    names = [line.strip() for line in path.read_text(encoding="utf-8").splitlines() if line.strip() and not line.lstrip().startswith("#")]
    if not names:
        raise ValueError("lake codename pool is empty")
    lowered = [name.casefold() for name in names]
    if len(lowered) != len(set(lowered)):
        raise ValueError("lake codename pool contains duplicates")
    if any(len(name) < 3 for name in names):
        raise ValueError("lake codename pool contains malformed entry")
    return names


def validate_version(version: str) -> None:
    if not VERSION_RE.fullmatch(version):
        raise ValueError("version must be semantic tag form vX.Y.Z")


def load_governance() -> tuple[list[str], dict, dict]:
    names = load_pool()
    policy = load_json(POLICY)
    history = load_json(HISTORY)
    if policy.get("schemaVersion") != 1 or history.get("schemaVersion") != 1:
        raise ValueError("release codename policy/history schemaVersion must be 1")
    if policy.get("pool") != str(POOL):
        raise ValueError("release codename policy must reference the authoritative lake pool")
    if not str(policy.get("source", {}).get("url", "")).startswith("https://"):
        raise ValueError("release codename source URL must use https")
    if policy.get("selection", {}).get("liveSourceFetchAtRelease") is not False:
        raise ValueError("release-time external source fetching must remain disabled")
    if policy.get("selection", {}).get("persistBeforeAcceptance") is not True:
        raise ValueError("codename selection must be persisted before acceptance")
    releases = history.get("releases", [])
    versions = [item.get("version") for item in releases]
    if len(versions) != len(set(versions)):
        raise ValueError("codename history contains duplicate versions")
    available = {name.casefold() for name in names}
    codenames: list[str] = []
    for item in releases:
        validate_version(item.get("version", ""))
        codename = item.get("codename", "")
        if codename.casefold() not in available:
            raise ValueError(f"history codename is not in the pinned pool: {codename!r}")
        if item.get("status") not in {"candidate", "published"}:
            raise ValueError(f"invalid codename history status for {item.get('version')}")
        codenames.append(codename.casefold())
    if not policy.get("selection", {}).get("allowReuseAfterExhaustion", False) and len(codenames) != len(set(codenames)):
        raise ValueError("codename reuse is forbidden by policy")
    minimum = int(policy.get("minimumPoolSize", 20))
    if len(names) < minimum:
        raise ValueError(f"lake codename pool must contain at least {minimum} entries")
    return names, policy, history


def select_codename(names: list[str], used: list[str], allow_reuse: bool = False) -> str:
    used_lower = {value.casefold() for value in used}
    available = [name for name in names if name.casefold() not in used_lower]
    if available:
        return secrets.choice(available)
    if allow_reuse:
        return secrets.choice(names)
    raise ValueError("lake codename pool exhausted and reuse is forbidden")


def existing_binding(version: str, history: dict) -> dict | None:
    return next((item for item in history.get("releases", []) if item.get("version") == version), None)


def persist_candidate(version: str, codename: str) -> None:
    history = load_json(HISTORY)
    existing = existing_binding(version, history)
    if existing:
        if existing.get("codename") != codename:
            raise ValueError("version is already bound to a different codename")
        return
    history.setdefault("releases", []).append({"version": version, "codename": codename, "status": "candidate"})
    HISTORY.write_text(json.dumps(history, indent=2) + "\n", encoding="utf-8")


def write_output(codename: str, existing: bool) -> None:
    print(codename)
    if os.getenv("GITHUB_OUTPUT"):
        with open(os.environ["GITHUB_OUTPUT"], "a", encoding="utf-8") as fh:
            fh.write(f"codename={codename}\n")
            fh.write(f"existing={'true' if existing else 'false'}\n")


def self_test() -> int:
    names, policy, history = load_governance()
    validate_version("v0.1.0")
    try:
        validate_version("0.1")
    except ValueError:
        pass
    else:
        raise AssertionError("invalid version accepted")
    assert select_codename(["Lake A", "Lake B"], ["Lake A"]) == "Lake B"
    try:
        select_codename(["Lake A"], ["Lake A"], allow_reuse=False)
    except ValueError:
        pass
    else:
        raise AssertionError("exhausted non-reuse pool did not fail")
    if history.get("releases"):
        item = history["releases"][0]
        assert existing_binding(item["version"], history)["codename"] == item["codename"]
    assert policy["selection"]["persistBeforeAcceptance"] is True
    print(f"PASS release_governance self-test ({len(names)} codenames)")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=["validate", "select", "binding", "self-test"])
    parser.add_argument("--version")
    parser.add_argument("--persist", action="store_true")
    args = parser.parse_args()
    if args.command == "self-test":
        return self_test()
    names, policy, history = load_governance()
    if args.version:
        validate_version(args.version)
    if args.command == "validate":
        print(f"PASS release governance: {len(names)} codenames, {len(history.get('releases', []))} persisted bindings")
        return 0
    if not args.version:
        raise ValueError("--version is required")
    bound = existing_binding(args.version, history)
    if args.command == "binding":
        if not bound:
            raise ValueError("release version has no persisted codename candidate; select and commit it before acceptance")
        write_output(bound["codename"], True)
        return 0
    if bound:
        write_output(bound["codename"], True)
        return 0
    used = [item["codename"] for item in history.get("releases", [])]
    chosen = select_codename(names, used, allow_reuse=bool(policy["selection"].get("allowReuseAfterExhaustion", False)))
    if args.persist:
        persist_candidate(args.version, chosen)
        load_governance()
    write_output(chosen, False)
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except ValueError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(2)
