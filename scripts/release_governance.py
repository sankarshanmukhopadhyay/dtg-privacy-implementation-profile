#!/usr/bin/env python3
"""DPIP release governance helper."""
from __future__ import annotations
import argparse, os, re, secrets, sys
from pathlib import Path

POOL=Path("release/lake-codenames.txt")
VERSION_RE=re.compile(r"^v(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)$")


def load_pool(path:Path=POOL)->list[str]:
    names=[line.strip() for line in path.read_text(encoding="utf-8").splitlines() if line.strip() and not line.lstrip().startswith("#")]
    if not names: raise ValueError("lake codename pool is empty")
    if len(names)!=len(set(names)): raise ValueError("lake codename pool contains duplicates")
    if any(len(n)<3 for n in names): raise ValueError("lake codename pool contains malformed entry")
    return names


def validate_version(version:str)->None:
    if not VERSION_RE.fullmatch(version): raise ValueError("version must be semantic tag form vX.Y.Z")


def select_codename(names:list[str], used:list[str])->str:
    used_lower={u.casefold() for u in used}
    available=[n for n in names if n.casefold() not in used_lower]
    return secrets.choice(available or names)


def self_test()->int:
    names=load_pool(); assert len(names)>=20
    validate_version("v0.1.0")
    try: validate_version("0.1")
    except ValueError: pass
    else: raise AssertionError("invalid version accepted")
    chosen=select_codename(["Lake A","Lake B"],["Lake A"]); assert chosen=="Lake B"
    print(f"PASS release_governance self-test ({len(names)} codenames)"); return 0


def main()->int:
    p=argparse.ArgumentParser(); p.add_argument("command",choices=["validate","select","self-test"]); p.add_argument("--version"); p.add_argument("--used-file"); a=p.parse_args()
    if a.command=="self-test": return self_test()
    names=load_pool()
    if a.version: validate_version(a.version)
    if a.command=="validate": print(f"PASS release governance: {len(names)} codenames"); return 0
    used=[]
    if a.used_file and Path(a.used_file).exists(): used=[x.strip() for x in Path(a.used_file).read_text().splitlines() if x.strip()]
    chosen=select_codename(names,used)
    print(chosen)
    if os.getenv("GITHUB_OUTPUT"):
        with open(os.environ["GITHUB_OUTPUT"],"a",encoding="utf-8") as fh: fh.write(f"codename={chosen}\n")
    return 0

if __name__=="__main__":
    try: raise SystemExit(main())
    except ValueError as exc:
        print(f"ERROR: {exc}",file=sys.stderr); raise SystemExit(2)
