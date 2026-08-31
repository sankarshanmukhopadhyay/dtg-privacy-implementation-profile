#!/usr/bin/env python3
"""Validate portable RAHP↔DPIP assessor-result and evidence-remediation contract fixtures.

Operational contract:
- Validates local contract schemas and representative fixtures, including deterministic INDETERMINATE/model-gap semantics.
- Contract validation proves producer/consumer payload compatibility only; it does not establish a privacy result or successful cross-repository delivery.
"""
from __future__ import annotations
import json
from pathlib import Path
import jsonschema

ROOT=Path(__file__).resolve().parent.parent


def validate() -> None:
    assessor_schema=json.loads((ROOT/'contracts/rahp-assessor-result-v1.schema.json').read_text())
    remediation_schema=json.loads((ROOT/'contracts/rahp-evidence-remediation-v1.schema.json').read_text())
    fixture=json.loads((ROOT/'contracts/fixtures/indeterminate-model-gap.json').read_text())
    jsonschema.Draft202012Validator(assessor_schema).validate(fixture['assessor_result'])
    jsonschema.Draft202012Validator(remediation_schema).validate(fixture['remediation'])
    assert fixture['assessor_result']['outcome']=='INDETERMINATE'
    assert fixture['assessor_result']['reason_code']=='model-gap'
    assert fixture['remediation']['status']=='model-gap'
    assert fixture['remediation']['requirements']


def main() -> int:
    validate(); print('PASS portable RAHP assessor/remediation contract fixtures'); return 0

if __name__=='__main__': raise SystemExit(main())
