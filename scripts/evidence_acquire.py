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


def normalized_observation(task: dict[str,Any], ctx: str, data: dict[str,Any] | None) -> tuple[dict[str,Any], dict[str,Any] | None]:
    oid=f"OBS-{task['id']}-{ctx}"
    base={"id":oid,"task_id":task["id"],"context_id":ctx,"observer":task["observer"],"component":task["component"],"surface":task["surface"],"retention_stage":task["retention_stage"]}
    if not data:
        return ({**base,"state":"not-available","evidence_class":"none"},
                {"task_id":task["id"],"collector":task.get("collector"),"component":task["component"],"observer":task["observer"],"context":ctx,"reason":"collector fixture/runtime access unavailable"})

    state=data.get("state","observed")
    evidence_class=data.get("evidence_class", "runtime-or-executable-fixture" if state=="observed" else "source")
    observation={**base,"state":state,"evidence_class":evidence_class,
                 "value_digest":data.get("value_digest"),"stability":data.get("stability"),
                 "declared_scope":data.get("declared_scope"),"observable_scope":data.get("observable_scope")}
    if data.get("source_provenance") is not None:
        observation["source_provenance"]=data["source_provenance"]
    if data.get("supported_proposition") is not None:
        observation["supported_proposition"]=data["supported_proposition"]

    if state=="source-backed":
        provenance=observation.get("source_provenance")
        proposition=observation.get("supported_proposition")
        if not isinstance(provenance,dict) or not provenance.get("revision") or not provenance.get("locator") or not proposition:
            raise ValueError(f"source-backed evidence for {task['id']}:{ctx} lacks attributable revision/locator/proposition")
        return observation,{"task_id":task["id"],"collector":task.get("collector"),"component":task["component"],"observer":task["observer"],"context":ctx,"reason":"runtime observation unavailable; attributable source evidence present"}

    return observation,None


def acquire(plan: dict[str,Any], fixture_loader=fixture_value) -> dict[str,Any]:
    if plan.get("status","ready") != "ready":
        return blocked_acquisition(plan)
    observations=[]; gaps=[]; by_task={}
    for task in plan.get("acquisition_tasks",[]):
        obs_ids=[]
        for ctx in task.get("contexts",[]):
            observation,gap=normalized_observation(task,ctx,fixture_loader(task.get("collector",""),ctx))
            observations.append(observation)
            if gap: gaps.append(gap)
            obs_ids.append(observation["id"])
        by_task[task["id"]]=obs_ids
    joins=[]
    obs_map={o["id"]:o for o in observations}
    for j in plan.get("join_attempts",[]):
        ids=[]
        for tid in j.get("task_ids",[]): ids.extend(by_task.get(tid,[]))
        available=[obs_map[i] for i in ids if obs_map[i].get("state")=="observed" and obs_map[i].get("value_digest")]
        source_backed=[obs_map[i] for i in ids if obs_map[i].get("state")=="source-backed"]
        result="not-run"; evidence=[]; explanation="Required runtime observations are unavailable."
        if len(available)>=2:
            digests={o["value_digest"] for o in available}
            evidence=[o["id"] for o in available]
            if len(digests)==1:
                result="joined"; explanation="Identical normalized stable value observed across required contexts."
            else:
                result="not-joined"; explanation="Available normalized values differ; this non-join does not establish global unlinkability."
        elif source_backed:
            evidence=[o["id"] for o in source_backed]
            explanation="Attributable source evidence is present, but source evidence is not an A/B runtime observation; the join remains not-run."
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
    body=f"{marker}\n## DPIP deterministic evidence acquisition — {status}\n\nCollectors distinguish runtime/executable observations from attributable source-backed evidence. Source evidence can narrow the evidence model but cannot by itself produce an A/B join result. This is **not** a privacy disposition.\n\n```yaml\n{yaml.safe_dump(result,sort_keys=False).rstrip()}\n```"
    api("POST",repo,f"issues/{number}/comments",token,{"body":body})


def self_test()->int:
    plan={"status":"ready","source_issue":65,"setup_digest":"x","contexts":[{"id":"A","role":"a","relationship":"unrelated"},{"id":"B","role":"b","relationship":"unrelated"}],"source_pins":[],"acquisition_tasks":[{"id":"EA-X","surface":"stable handle","component":"status","observer":"status-source","contexts":["A","B"],"retention_stage":"retained","availability":"missing","falsification_purpose":"join","collector":"status"}],"join_attempts":[{"id":"JOIN-X","task_ids":["EA-X"],"contexts":["A","B"],"basis":"identical handle","expected_question":"join?"}]}
    def same(_c,ctx): return {"state":"observed","value_digest":"sha256:same","stability":"stable"}
    joined=acquire(plan,same)["evidence_acquisition"]
    assert joined["status"]=="acquired" and joined["join_attempts"][0]["result"]=="joined"
    missing=acquire(plan,lambda _c,_x:None)["evidence_acquisition"]
    assert missing["status"]=="acquisition-incomplete" and len(missing["acquisition_gaps"])==2

    source={"state":"source-backed","evidence_class":"specification","source_provenance":{"repository":"example/spec","revision":"abc123","locator":"spec.md#field"},"supported_proposition":"The field is defined by the pinned specification."}
    source_only=acquire(plan,lambda _c,_x:source)["evidence_acquisition"]
    assert source_only["status"]=="acquisition-incomplete"
    assert all(o["state"]=="source-backed" for o in source_only["observed_surfaces"])
    assert source_only["join_attempts"][0]["result"]=="not-run"
    assert "not an A/B runtime observation" in source_only["join_attempts"][0]["explanation"]
    assert all("source evidence present" in g["reason"] for g in source_only["acquisition_gaps"])

    def mixed(_c,ctx):
        return same(_c,ctx) if ctx=="A" else source
    mixed_result=acquire(plan,mixed)["evidence_acquisition"]
    assert mixed_result["join_attempts"][0]["result"]=="not-run"
    assert len([o for o in mixed_result["observed_surfaces"] if o["state"]=="observed"])==1

    blocked_plan=dict(plan); blocked_plan["status"]="needs-review"; blocked_plan["unresolved_requirements"]=["unmapped evidence surface: unknown"]
    blocked=acquire(blocked_plan,same)["evidence_acquisition"]
    assert blocked["status"]=="acquisition-blocked"
    assert not blocked["observed_surfaces"] and "unmapped evidence surface" in blocked["acquisition_gaps"][0]["reason"]
    assert blocked["privacy_judgment"]=="not-made"

    # Exercise the actual producer -> Markdown/YAML transport -> consumer contract.
    from evidence_plan import render_plan_comment
    rendered=render_plan_comment(65,plan)
    recovered=latest_plan([{"body":rendered}])
    assert recovered==plan
    print("PASS evidence_acquire self-test"); return 0


def main()->int:
    p=argparse.ArgumentParser(); p.add_argument("--self-test",action="store_true"); p.add_argument("--issue-number",type=int); a=p.parse_args()
    if a.self_test:return self_test()
    token=os.getenv("GITHUB_TOKEN",""); repo=os.getenv("DPIP_REPOSITORY",DEFAULT_REPO)
    if not token or not a.issue_number:return 2
    publish(repo,a.issue_number,token); return 0

if __name__=="__main__": raise SystemExit(main())
