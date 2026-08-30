#!/usr/bin/env python3
"""Return completed RAHP-originated DPIP dispositions to their source issue."""
from __future__ import annotations
import argparse, json, os, re, sys, urllib.error, urllib.parse, urllib.request
from typing import Any
import yaml
DEFAULT_DPIP_REPO="sankarshanmukhopadhyay/dtg-privacy-implementation-profile"; DEFAULT_RAHP_REPO="sankarshanmukhopadhyay/rahp-toolkit"
SOURCE_LABEL="source:rahp"; COMPLETE_LABEL="run:complete"; RAHP_COMPLETE="assurance:dpip-complete"
RAHP_TRANSIENT=("assurance:dpip-candidate","assurance:dpip-requested","assurance:dpip-open")
CONCLUSIONS={"PASS","FAIL","CONSTRAINED","INDETERMINATE","NOT_APPLICABLE"}
DEFAULT_HUMAN_OUTCOMES={"PASS":"Privacy expectation met","FAIL":"Privacy expectation not met","CONSTRAINED":"Privacy works, but with important limitations","INDETERMINATE":"We do not have enough evidence to decide yet","NOT_APPLICABLE":"This privacy test does not apply here"}

def api(method,repo,path,token,payload=None):
    url=f"https://api.github.com/repos/{repo}/{path.lstrip('/')}"; data=None if payload is None else json.dumps(payload).encode()
    req=urllib.request.Request(url,data=data,method=method,headers={"Accept":"application/vnd.github+json","User-Agent":"dpip-rahp-return/1.0","X-GitHub-Api-Version":"2022-11-28","Authorization":f"Bearer {token}",**({"Content-Type":"application/json"} if data is not None else {})})
    with urllib.request.urlopen(req,timeout=30) as response: raw=response.read()
    return json.loads(raw) if raw else None

def yaml_blocks(text):
    out=[]
    for m in re.finditer(r"```ya?ml\s*\n(.*?)```",text or "",re.DOTALL|re.IGNORECASE):
        try: parsed=yaml.safe_load(m.group(1))
        except yaml.YAMLError: continue
        if isinstance(parsed,dict): out.append(parsed)
    return out

def source_record(body):
    for block in yaml_blocks(body):
        source=block.get("source")
        if isinstance(source,dict) and source.get("system")=="RAHP": return source
    raise ValueError("no machine-readable RAHP `source:` YAML block found")

def examination_record(comments):
    for comment in reversed(comments):
        for block in yaml_blocks(comment.get("body") or ""):
            examination=block.get("dpip_examination")
            if isinstance(examination,dict): return examination
    raise ValueError("no structured `dpip_examination:` conclusion found in DPIP comments")

def validate_assessor_result(result):
    errors=[]
    if not isinstance(result,dict): return ["assessor_result must be a mapping"]
    if result.get("schema")!="rahp-assessor-result/v1": errors.append("assessor_result.schema must be rahp-assessor-result/v1")
    if not str(result.get("assessor","")).strip(): errors.append("assessor_result.assessor is required")
    if not str(result.get("assessment_id","")).strip(): errors.append("assessor_result.assessment_id is required")
    if result.get("outcome") not in {"PASS","FAIL","INDETERMINATE","NOT_APPLICABLE"}: errors.append("assessor_result.outcome is not portable")
    for key in ("reason_code","residual_risk","action_required"):
        if not str(result.get(key,"")).strip(): errors.append(f"assessor_result.{key} is required")
    if not isinstance(result.get("evidence_used"),list): errors.append("assessor_result.evidence_used must be a list")
    return errors

def validate_examination(e):
    errors=[]; applicability=str(e.get("applicability","")).strip(); conclusion=str(e.get("conclusion","")).strip()
    if applicability not in {"applicable","not-applicable"}: errors.append("applicability must be applicable or not-applicable")
    if conclusion not in CONCLUSIONS: errors.append(f"unsupported conclusion {conclusion!r}")
    if applicability=="not-applicable" and conclusion!="NOT_APPLICABLE": errors.append("not-applicable intake must return NOT_APPLICABLE")
    if not str(e.get("evidence_summary","")).strip(): errors.append("evidence_summary is required")
    if not str(e.get("action","")).strip(): errors.append("action is required")
    if conclusion=="INDETERMINATE":
        plan=e.get("evidence_remediation_plan")
        if not isinstance(plan,dict) or not plan.get("requirements"): errors.append("INDETERMINATE requires a non-empty evidence_remediation_plan")
    if e.get("assessor_result") is not None:
        errors.extend(validate_assessor_result(e.get("assessor_result")))
        if e["assessor_result"].get("outcome") != conclusion:
            errors.append("assessor_result.outcome must equal DPIP conclusion")
    return errors

def human_summary(e):
    supplied=e.get("human_summary")
    if isinstance(supplied,dict): return {k:str(supplied[k]).strip() for k in ("outcome","explanation","action")}
    explanation=str(e["evidence_summary"]).strip(); residual=str(e.get("residual_correlation","")).strip()
    if residual: explanation+=f" Remaining limitation: {residual}"
    return {"outcome":DEFAULT_HUMAN_OUTCOMES[str(e["conclusion"])],"explanation":explanation,"action":str(e["action"]).strip()}

def has_label(issue,name): return any(label.get("name")==name for label in issue.get("labels",[]))
def get_candidates(repo,token,number):
    if number is not None: return [api("GET",repo,f"issues/{number}",token)]
    labels=urllib.parse.quote(f"{SOURCE_LABEL},{COMPLETE_LABEL}",safe=","); return api("GET",repo,f"issues?state=all&labels={labels}&per_page=100",token) or []
def return_marker(repo,number): return f"<!-- dpip-return:{repo}#{number} -->"

def compact_plan(plan):
    requirements=[]
    for item in plan.get("requirements",[]):
        requirements.append({k:item.get(k) for k in ("id","proposition","evidence_class","producer","context_boundary","required_fields","privacy_safe_capture_rule","acceptance_criterion","rerun_target","priority","routing_target") if item.get(k) is not None})
    return {"plan_digest":plan.get("plan_digest"),"requirements":requirements,"rerun_policy":plan.get("rerun_policy")}

def disposition_body(dpip_repo,issue,e):
    plain=human_summary(e); disposition={"dpip_issue":issue["number"],"applicability":e["applicability"],"conclusion":e["conclusion"],"human_summary":plain}
    for key in ("affected_interactions","affected_reference_flows","affected_claims","affected_invariants"):
        if e.get(key): disposition[key]=e[key]
    disposition["evidence_summary"]=e["evidence_summary"]
    if e.get("residual_correlation"): disposition["residual_correlation"]=e["residual_correlation"]
    disposition["action"]=e["action"]
    if isinstance(e.get("evidence_remediation_plan"),dict): disposition["evidence_remediation_plan"]=compact_plan(e["evidence_remediation_plan"])
    if isinstance(e.get("assessor_result"),dict): disposition["assessor_result"]=e["assessor_result"]
    payload={"dpip_disposition":disposition}; marker=return_marker(dpip_repo,issue["number"])
    remediation=""
    if disposition.get("evidence_remediation_plan"):
        remediation="\n\n### Evidence remediation required\n\nThe structured disposition below identifies the minimum evidence packages, their producers, privacy-safe capture rules, sufficiency criteria, routing targets, and pinned rerun target. This is the action generated by the INDETERMINATE result; it is not a privacy failure finding."
    return f"{marker}\n## DPIP disposition returned\n\nDPIP examination: {issue['html_url']}\n\n### Plain-language result: {plain['outcome']}\n\n{plain['explanation']}\n\n**What to do:** {plain['action']}{remediation}\n\n<details><summary>Structured DPIP disposition</summary>\n\n```yaml\n{yaml.safe_dump(payload,sort_keys=False).rstrip()}\n```\n\n</details>\n\nDPIP owns the technical conclusion above; this comment closes only the DPIP handoff subflow. Any wider RAHP/security assessment remains independently governed."

def process_issue(dpip_repo,default_rahp_repo,issue,dpip_token,rahp_token):
    if not(has_label(issue,SOURCE_LABEL) and has_label(issue,COMPLETE_LABEL)): print(f"SKIP {dpip_repo}#{issue.get('number')}: not a completed RAHP-originated intake"); return False
    source=source_record(issue.get("body") or ""); rahp_repo=str(source.get("repository") or default_rahp_repo); rahp_issue=int(source["issue"])
    comments=api("GET",dpip_repo,f"issues/{issue['number']}/comments?per_page=100",dpip_token) or []; examination=examination_record(comments); problems=validate_examination(examination)
    if problems: raise ValueError("; ".join(problems))
    marker=return_marker(dpip_repo,issue["number"]); source_comments=api("GET",rahp_repo,f"issues/{rahp_issue}/comments?per_page=100",rahp_token) or []
    if any(marker in (c.get("body") or "") for c in source_comments): print(f"EXISTS return for {dpip_repo}#{issue['number']} on {rahp_repo}#{rahp_issue}")
    else: api("POST",rahp_repo,f"issues/{rahp_issue}/comments",rahp_token,{"body":disposition_body(dpip_repo,issue,examination)}); print(f"RETURNED {dpip_repo}#{issue['number']} to {rahp_repo}#{rahp_issue}")
    api("POST",rahp_repo,f"issues/{rahp_issue}/labels",rahp_token,{"labels":[RAHP_COMPLETE]})
    for label in RAHP_TRANSIENT:
        try: api("DELETE",rahp_repo,f"issues/{rahp_issue}/labels/{urllib.parse.quote(label,safe='')}",rahp_token)
        except urllib.error.HTTPError as exc:
            if exc.code!=404: raise
    return True

def run(dpip_repo,rahp_repo,dpip_token,rahp_token,number):
    failures=0
    for issue in get_candidates(dpip_repo,dpip_token,number):
        try: process_issue(dpip_repo,rahp_repo,issue,dpip_token,rahp_token)
        except Exception as exc: failures+=1; print(f"FAIL {dpip_repo}#{issue.get('number')}: {exc}",file=sys.stderr)
    return 1 if failures else 0

def self_test():
    body="""```yaml\nsource:\n  system: RAHP\n  repository: example/rahp\n  issue: 42\n```"""; assert source_record(body)["issue"]==42
    examination={"applicability":"applicable","conclusion":"INDETERMINATE","affected_interactions":["C3"],"evidence_summary":"Runtime evidence is missing.","residual_correlation":"Unresolved.","action":"Supply bounded evidence and rerun.","assessor_result":{"schema":"rahp-assessor-result/v1","assessor":"dpip","assessment_id":"dpip:7","outcome":"INDETERMINATE","reason_code":"evidence-required","evidence_used":[],"residual_risk":"Unresolved.","action_required":"Supply bounded evidence and rerun."},"human_summary":{"outcome":"We do not have enough evidence to decide yet","explanation":"Runtime evidence is missing.","action":"Supply bounded evidence and rerun."},"evidence_remediation_plan":{"plan_digest":"abc","requirements":[{"id":"R1","proposition":"test joinability","producer":"implementation","routing_target":"upstream-runtime"}],"rerun_policy":"new pinned run"}}
    assert not validate_examination(examination); rendered=disposition_body("example/dpip",{"number":7,"html_url":"https://example.invalid/7"},examination); assert "evidence_remediation_plan" in rendered and "Evidence remediation required" in rendered
    missing=dict(examination); missing.pop("evidence_remediation_plan"); assert validate_examination(missing)
    print("PASS rahp_return self-test"); return 0

def main():
    p=argparse.ArgumentParser(); p.add_argument("--self-test",action="store_true"); p.add_argument("--issue-number",type=int); p.add_argument("--dpip-repository",default=os.getenv("DPIP_REPOSITORY",DEFAULT_DPIP_REPO)); p.add_argument("--rahp-repository",default=os.getenv("RAHP_REPOSITORY",DEFAULT_RAHP_REPO)); a=p.parse_args()
    if a.self_test: return self_test()
    dt=os.getenv("GITHUB_TOKEN",""); rt=os.getenv("RAHP_HANDOFF_TOKEN","")
    if not dt: print("GITHUB_TOKEN is required",file=sys.stderr); return 2
    if not rt: print("RAHP_HANDOFF_TOKEN is not configured; completed DPIP dispositions were not returned."); return 0
    return run(a.dpip_repository,a.rahp_repository,dt,rt,a.issue_number)
if __name__=="__main__": raise SystemExit(main())
