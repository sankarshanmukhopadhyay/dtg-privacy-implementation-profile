#!/usr/bin/env python3
"""Acquire normalized evidence from DPIP evidence plans without inventing runtime observations."""
from __future__ import annotations
import argparse, hashlib, json, os, re
from pathlib import Path
from typing import Any
import yaml
from rahp_intake import api

DEFAULT_REPO = "sankarshanmukhopadhyay/dtg-privacy-implementation-profile"
FIXTURES = Path("collector-fixtures")


def yaml_docs(text: str) -> list[dict[str, Any]]:
    out=[]
    for m in re.finditer(r"```ya?ml\s*\n(.*?)```", text or "", re.S|re.I):
        try: v=yaml.safe_load(m.group(1))
        except yaml.YAMLError: continue
        if isinstance(v,dict): out.append(v)
    return out


def latest_plan(comments: list[dict[str,Any]]) -> dict[str,Any]:
    for c in reversed(comments):
        for d in yaml_docs(c.get("body") or ""):
            if isinstance(d.get("evidence_plan"),dict): return d["evidence_plan"]
    raise ValueError("no evidence_plan found")


def fixture_value(collector: str, context: str) -> dict[str,Any] | None:
    path=FIXTURES/collector/f"{context}.yaml"
    return yaml.safe_load(path.read_text()) if path.exists() else None


def blocked_acquisition(plan: dict[str,Any]) -> dict[str,Any]:
    reasons=list(plan.get("unresolved_requirements",[]) or [])
    if not reasons:
        reasons=[f"evidence plan status is {plan.get('status','unknown')!r}, not 'ready'"]
    result={"evidence_acquisition":{
        "status":"acquisition-blocked",
        "source_issue":plan["source_issue"],
        "setup_digest":plan["setup_digest"],
        "contexts":plan.get("contexts",[]),
        "observed_surfaces":[],
        "join_attempts":[],
        "acquisition_gaps":[{"reason":reason} for reason in reasons],
        "source_pins":plan.get("source_pins",[]),
        "privacy_judgment":"not-made",
        "human_acceptance_required":True,
    }}
    result["evidence_acquisition"]["acquisition_digest"]=hashlib.sha256(json.dumps(result,sort_keys=True,separators=(",",":")).encode()).hexdigest()[:16]
    return result


def acquire(plan: dict[str,Any], fixture_loader=fixture_value) -> dict[str,Any]:
    if plan.get("status","ready") != "ready":
        return blocked_acquisition(plan)
    observations=[]; gaps=[]; by_task={}
    for task in plan.get("acquisition_tasks",[]):
        obs_ids=[]
        for ctx in task.get("contexts",[]):
            data=fixture_loader(task.get("collector",""),ctx)
            oid=f"OBS-{task['id']}-{ctx}"
            if not data:
                observations.append({"id":oid,"task_id":task["id"],"context_id":ctx,"observer":task["observer"],"component":task["component"],"surface":task["surface"],"state":"not-available","retention_stage":task["retention_stage"]})
                gaps.append({"task_id":task["id"],"collector":task.get("collector"),"component":task["component"],"observer":task["observer"],"context":ctx,"reason":"collector fixture/runtime access unavailable"})
            else:
                observations.append({"id":oid,"task_id":task["id"],"context_id":ctx,"observer":task["observer"],"component":task["component"],"surface":task["surface"],"state":data.get("state","observed"),"value_digest":data.get("value_digest"),"stability":data.get("stability"),"retention_stage":task["retention_stage"],"declared_scope":data.get("declared_scope"),"observable_scope":data.get("observable_scope")})
            obs_ids.append(oid)
        by_task[task["id"]]=obs_ids
    joins=[]
    obs_map={o["id"]:o for o in observations}
    for j in plan.get("join_attempts",[]):
        ids=[]
        for tid in j.get("task_ids",[]): ids.extend(by_task.get(tid,[]))
        available=[obs_map[i] for i in ids if obs_map[i].get("state")=="observed" and obs_map[i].get("value_digest")]
        result="not-run"; evidence=[]; explanation="Required runtime observations are unavailable."
        if len(available)>=2:
            digests={o["value_digest"] for o in available}
            evidence=[o["id"] for o in available]
            if len(digests)==1:
                result="joined"; explanation="Identical normalized stable value observed across required contexts."
            else:
                result="not-joined"; explanation="Available normalized values differ; this non-join does not establish global unlinkability."
        joins.append({"id":j["id"],"context_ids":j["contexts"],"input_observation_ids":ids,"basis":j["basis"],"result":result,"evidence":evidence or ["runtime evidence unavailable"],"explanation":explanation})
    status="acquired" if observations and not gaps else "acquisition-incomplete"
    result={"evidence_acquisition":{"status":status,"source_issue":plan["source_issue"],"setup_digest":plan["setup_digest"],"contexts":plan["contexts"],"observed_surfaces":observations,"join_attempts":joins,"acquisition_gaps":gaps,"source_pins":plan.get("source_pins",[]),"privacy_judgment":"not-made","human_acceptance_required":True}}
    result["evidence_acquisition"]["acquisition_digest"]=hashlib.sha256(json.dumps(result,sort_keys=True,separators=(",",":")).encode()).hexdigest()[:16]
    return result


def publish(repo:str,number:int,token:str)->None:
    comments=api("GET",repo,f"issues/{number}/comments?per_page=100",token) or []
    result=acquire(latest_plan(comments)); digest=result["evidence_acquisition"]["acquisition_digest"]
    marker=f"<!-- dpip-evidence-acquisition:{number}:{digest} -->"
    if any(marker in (c.get("body") or "") for c in comments): return
    status=result["evidence_acquisition"]["status"]
    body=f"{marker}\n## DPIP deterministic evidence acquisition — {status}\n\nCollectors record only available evidence; unavailable runtime access remains explicit. This is **not** a privacy disposition.\n\n```yaml\n{yaml.safe_dump(result,sort_keys=False).rstrip()}\n```"
    api("POST",repo,f"issues/{number}/comments",token,{"body":body})


def self_test()->int:
    plan={"status":"ready","source_issue":65,"setup_digest":"x","contexts":[{"id":"A","role":"a","relationship":"unrelated"},{"id":"B","role":"b","relationship":"unrelated"}],"source_pins":[],"acquisition_tasks":[{"id":"EA-X","surface":"stable handle","component":"status","observer":"status-source","contexts":["A","B"],"retention_stage":"retained","availability":"missing","falsification_purpose":"join","collector":"status"}],"join_attempts":[{"id":"JOIN-X","task_ids":["EA-X"],"contexts":["A","B"],"basis":"identical handle","expected_question":"join?"}]}
    def same(_c,ctx): return {"state":"observed","value_digest":"sha256:same","stability":"stable"}
    joined=acquire(plan,same)["evidence_acquisition"]
    assert joined["status"]=="acquired" and joined["join_attempts"][0]["result"]=="joined"
    missing=acquire(plan,lambda _c,_x:None)["evidence_acquisition"]
    assert missing["status"]=="acquisition-incomplete" and len(missing["acquisition_gaps"])==2
    blocked_plan=dict(plan); blocked_plan["status"]="needs-review"; blocked_plan["unresolved_requirements"]=["unmapped evidence surface: unknown"]
    blocked=acquire(blocked_plan,same)["evidence_acquisition"]
    assert blocked["status"]=="acquisition-blocked"
    assert not blocked["observed_surfaces"] and "unmapped evidence surface" in blocked["acquisition_gaps"][0]["reason"]
    assert blocked["privacy_judgment"]=="not-made"
    print("PASS evidence_acquire self-test"); return 0


def main()->int:
    p=argparse.ArgumentParser(); p.add_argument("--self-test",action="store_true"); p.add_argument("--issue-number",type=int); a=p.parse_args()
    if a.self_test:return self_test()
    token=os.getenv("GITHUB_TOKEN",""); repo=os.getenv("DPIP_REPOSITORY",DEFAULT_REPO)
    if not token or not a.issue_number:return 2
    publish(repo,a.issue_number,token); return 0

if __name__=="__main__": raise SystemExit(main())
