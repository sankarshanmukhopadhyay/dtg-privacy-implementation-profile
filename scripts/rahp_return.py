#!/usr/bin/env python3
"""Return completed RAHP-originated DPIP dispositions to their source issue.

Operational contract:
- Reads terminal DPIP examination state, validates/normalizes the portable return contract, and writes a durable outbox record before cross-repository delivery.
- Delivers the exact disposition to the originating RAHP issue and records acknowledgement for idempotent retry.
- Transport failure leaves machine-visible pending work; scheduled reconciliation may retry without recomputing the examination.
- Successful return means RAHP received the DPIP result, not that the RAHP portfolio is GREEN.
"""
from __future__ import annotations
import argparse, hashlib, json, os, re, sys, urllib.error, urllib.parse, urllib.request
from typing import Any
import yaml
DEFAULT_DPIP_REPO="sankarshanmukhopadhyay/dtg-privacy-implementation-profile"; DEFAULT_RAHP_REPO="sankarshanmukhopadhyay/rahp-toolkit"
SOURCE_LABEL="source:rahp"; COMPLETE_LABEL="run:complete"; MODEL_GAP_LABEL="model-gap"; RAHP_COMPLETE="assurance:dpip-complete"
RAHP_TRANSIENT=("assurance:dpip-candidate","assurance:dpip-requested","assurance:dpip-open")
CONCLUSIONS={"PASS","FAIL","CONSTRAINED","INDETERMINATE","NOT_APPLICABLE"}
DEFAULT_HUMAN_OUTCOMES={"PASS":"Privacy expectation met","FAIL":"Privacy expectation not met","CONSTRAINED":"Privacy works, but with important limitations","INDETERMINATE":"We do not have enough evidence to decide yet","NOT_APPLICABLE":"This privacy test does not apply here"}
OUTBOX_VERSION="v1"


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


def _scope_tokens(e):
    values=[]
    for key in ("affected_invariants","affected_claims","affected_interactions","affected_reference_flows"):
        for value in e.get(key,[]) or []:
            text=str(value).strip()
            if text and text not in values: values.append(text)
    return values


def synthesize_model_gap_plan(e):
    scope=_scope_tokens(e)
    basis={"scope":scope,"evidence_summary":str(e.get("evidence_summary","")).strip(),"action":str(e.get("action","")).strip()}
    digest=hashlib.sha256(json.dumps(basis,sort_keys=True,separators=(",",":")).encode()).hexdigest()[:12]
    proposition=("; ".join(scope) if scope else "material privacy proposition not yet mapped to a canonical DPIP evidence requirement")
    requirement={
        "id":f"MODEL-GAP-{digest}","proposition":proposition,"evidence_class":"model/evidence-contract-definition","producer":"dpip-evidence-model",
        "context_boundary":"original pinned RAHP referral scope",
        "required_fields":["proposition","accepted_evidence_classes","producer_lineage","sufficiency_criterion","privacy_safe_capture_rule"],
        "privacy_safe_capture_rule":"Define the minimum evidence contract without collecting unrelated identifiers or expanding the referral correlation scope.",
        "acceptance_criterion":"Register a canonical evidence requirement for this proposition/surface, bind an attributable producer and accepted evidence class, then execute a new comparable pinned examination.",
        "rerun_target":"new comparable pinned DPIP examination derived from the original RAHP referral","priority":"high","routing_target":"dpip-model-gap",
    }
    plan={"status":"model-gap","reason_code":"model-gap","requirements":[requirement],"rerun_policy":"Create a new comparable examination after the evidence contract is registered; do not mutate the completed historical examination."}
    plan["plan_digest"]=hashlib.sha256(json.dumps(plan,sort_keys=True,separators=(",",":")).encode()).hexdigest()[:16]
    return plan


def effective_remediation_plan(e):
    plan=e.get("evidence_remediation_plan")
    if isinstance(plan,dict) and plan.get("requirements"): return plan
    if str(e.get("conclusion","")).strip()=="INDETERMINATE": return synthesize_model_gap_plan(e)
    return None


def terminal_labels(e):
    plan=effective_remediation_plan(e)
    return [MODEL_GAP_LABEL] if isinstance(plan,dict) and plan.get("status")=="model-gap" else []


def validate_examination(e):
    errors=[]; applicability=str(e.get("applicability","")).strip(); conclusion=str(e.get("conclusion","")).strip()
    if applicability not in {"applicable","not-applicable"}: errors.append("applicability must be applicable or not-applicable")
    if conclusion not in CONCLUSIONS: errors.append(f"unsupported conclusion {conclusion!r}")
    if applicability=="not-applicable" and conclusion!="NOT_APPLICABLE": errors.append("not-applicable intake must return NOT_APPLICABLE")
    if not str(e.get("evidence_summary","")).strip(): errors.append("evidence_summary is required")
    if not str(e.get("action","")).strip(): errors.append("action is required")
    if conclusion=="INDETERMINATE":
        plan=effective_remediation_plan(e)
        if not isinstance(plan,dict) or not plan.get("requirements"): errors.append("INDETERMINATE must resolve to a non-empty evidence remediation or model-gap plan")
    if e.get("assessor_result") is not None:
        errors.extend(validate_assessor_result(e.get("assessor_result")))
        if e["assessor_result"].get("outcome") != conclusion: errors.append("assessor_result.outcome must equal DPIP conclusion")
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
def outbox_digest(payload): return hashlib.sha256(payload.encode()).hexdigest()[:20]
def outbox_marker(number,digest): return f"<!-- rahp-return-outbox:{OUTBOX_VERSION}:{number}:{digest} -->"
def ack_marker(number,digest): return f"<!-- rahp-return-ack:{OUTBOX_VERSION}:{number}:{digest} -->"


def compact_plan(plan):
    requirements=[]
    for item in plan.get("requirements",[]): requirements.append({k:item.get(k) for k in ("id","proposition","evidence_class","producer","context_boundary","required_fields","privacy_safe_capture_rule","acceptance_criterion","rerun_target","priority","routing_target") if item.get(k) is not None})
    return {"status":plan.get("status"),"reason_code":plan.get("reason_code"),"plan_digest":plan.get("plan_digest"),"requirements":requirements,"rerun_policy":plan.get("rerun_policy")}


def disposition_body(dpip_repo,issue,e):
    plain=human_summary(e); disposition={"dpip_issue":issue["number"],"applicability":e["applicability"],"conclusion":e["conclusion"],"human_summary":plain}
    for key in ("affected_interactions","affected_reference_flows","affected_claims","affected_invariants"):
        if e.get(key): disposition[key]=e[key]
    disposition["evidence_summary"]=e["evidence_summary"]
    if e.get("residual_correlation"): disposition["residual_correlation"]=e["residual_correlation"]
    disposition["action"]=e["action"]
    plan=effective_remediation_plan(e)
    if isinstance(plan,dict):
        disposition["evidence_remediation_plan"]=compact_plan(plan)
        if plan.get("status")=="model-gap": disposition["terminal_reason"]="model-gap"
    if isinstance(e.get("assessor_result"),dict): disposition["assessor_result"]=e["assessor_result"]
    payload={"dpip_disposition":disposition}; marker=return_marker(dpip_repo,issue["number"])
    remediation=""
    if disposition.get("evidence_remediation_plan"):
        if disposition.get("terminal_reason")=="model-gap": remediation="\n\n### Evidence-model remediation required\n\nDPIP reached a valid INDETERMINATE result but the material proposition is not yet mapped to a canonical evidence requirement. The structured disposition therefore carries a deterministic model/evidence-contract gap and rerun criterion. This is not a privacy PASS or FAIL."
        else: remediation="\n\n### Evidence remediation required\n\nThe structured disposition below identifies the minimum evidence packages, their producers, privacy-safe capture rules, sufficiency criteria, routing targets, and pinned rerun target. This is the action generated by the INDETERMINATE result; it is not a privacy failure finding."
    return f"{marker}\n## DPIP disposition returned\n\nDPIP examination: {issue['html_url']}\n\n### Plain-language result: {plain['outcome']}\n\n{plain['explanation']}\n\n**What to do:** {plain['action']}{remediation}\n\n<details><summary>Structured DPIP disposition</summary>\n\n```yaml\n{yaml.safe_dump(payload,sort_keys=False).rstrip()}\n```\n\n</details>\n\nDPIP owns the technical conclusion above; this comment closes only the DPIP handoff subflow. Any wider RAHP/security assessment remains independently governed."


def ensure_outbox(dpip_repo,issue_number,comments,payload,digest,dpip_token):
    marker=outbox_marker(issue_number,digest)
    if any(marker in (c.get("body") or "") for c in comments): return False
    body=f"{marker}\n## RAHP return outbox\n\n- status: **pending**\n- payload digest: `{digest}`\n- transport: `DPIP -> RAHP issue disposition`\n\nThis durable outbox marker is written before cross-repository delivery. Scheduled reconciliation may retry it idempotently until an acknowledgement with the same digest exists."
    api("POST",dpip_repo,f"issues/{issue_number}/comments",dpip_token,{"body":body})
    return True


def ensure_ack(dpip_repo,issue_number,comments,digest,rahp_repo,rahp_issue,dpip_token):
    marker=ack_marker(issue_number,digest)
    if any(marker in (c.get("body") or "") for c in comments): return False
    body=f"{marker}\n## RAHP return acknowledged\n\n- status: **delivered**\n- payload digest: `{digest}`\n- destination: `{rahp_repo}#{rahp_issue}`\n\nThe specialist return is durably present at the RAHP source and is safe for idempotent replay."
    api("POST",dpip_repo,f"issues/{issue_number}/comments",dpip_token,{"body":body})
    return True


def process_issue(dpip_repo,default_rahp_repo,issue,dpip_token,rahp_token):
    if not(has_label(issue,SOURCE_LABEL) and has_label(issue,COMPLETE_LABEL)): print(f"SKIP {dpip_repo}#{issue.get('number')}: not a completed RAHP-originated intake"); return False
    source=source_record(issue.get("body") or ""); rahp_repo=str(source.get("repository") or default_rahp_repo); rahp_issue=int(source["issue"])
    comments=api("GET",dpip_repo,f"issues/{issue['number']}/comments?per_page=100",dpip_token) or []; examination=examination_record(comments); problems=validate_examination(examination)
    if problems: raise ValueError("; ".join(problems))
    labels=terminal_labels(examination)
    if labels: api("POST",dpip_repo,f"issues/{issue['number']}/labels",dpip_token,{"labels":labels})
    payload=disposition_body(dpip_repo,issue,examination); digest=outbox_digest(payload)
    ensure_outbox(dpip_repo,issue["number"],comments,payload,digest,dpip_token)
    marker=return_marker(dpip_repo,issue["number"]); source_comments=api("GET",rahp_repo,f"issues/{rahp_issue}/comments?per_page=100",rahp_token) or []
    if any(marker in (c.get("body") or "") for c in source_comments): print(f"EXISTS return for {dpip_repo}#{issue['number']} on {rahp_repo}#{rahp_issue}")
    else: api("POST",rahp_repo,f"issues/{rahp_issue}/comments",rahp_token,{"body":payload}); print(f"RETURNED {dpip_repo}#{issue['number']} to {rahp_repo}#{rahp_issue}")
    api("POST",rahp_repo,f"issues/{rahp_issue}/labels",rahp_token,{"labels":[RAHP_COMPLETE]})
    for label in RAHP_TRANSIENT:
        try: api("DELETE",rahp_repo,f"issues/{rahp_issue}/labels/{urllib.parse.quote(label,safe='')}",rahp_token)
        except urllib.error.HTTPError as exc:
            if exc.code!=404: raise
    latest_comments=api("GET",dpip_repo,f"issues/{issue['number']}/comments?per_page=100",dpip_token) or comments
    ensure_ack(dpip_repo,issue["number"],latest_comments,digest,rahp_repo,rahp_issue,dpip_token)
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
    assert terminal_labels(examination)==[]
    model_gap=dict(examination); model_gap["affected_interactions"]=[]; model_gap["affected_invariants"]=["credential-object-identity-does-not-expand-declared-correlation-scope"]; model_gap["evidence_remediation_plan"]={"plan_digest":"empty","requirements":[],"rerun_policy":"new pinned run"}
    assert not validate_examination(model_gap); gap_plan=effective_remediation_plan(model_gap); assert gap_plan["status"]=="model-gap" and len(gap_plan["requirements"])==1
    assert terminal_labels(model_gap)==["model-gap"]
    rendered_gap=disposition_body("example/dpip",{"number":149,"html_url":"https://example.invalid/149"},model_gap); assert "terminal_reason: model-gap" in rendered_gap and "MODEL-GAP-" in rendered_gap
    digest=outbox_digest(rendered_gap); assert digest==outbox_digest(rendered_gap); assert "rahp-return-outbox:v1:149:" in outbox_marker(149,digest); assert "rahp-return-ack:v1:149:" in ack_marker(149,digest)
    malformed=dict(model_gap); malformed["action"]=""; assert validate_examination(malformed)
    print("PASS rahp_return self-test including #149 model-gap labeling and durable outbox contract"); return 0


def main():
    p=argparse.ArgumentParser(); p.add_argument("--self-test",action="store_true"); p.add_argument("--issue-number",type=int); p.add_argument("--dpip-repository",default=os.getenv("DPIP_REPOSITORY",DEFAULT_DPIP_REPO)); p.add_argument("--rahp-repository",default=os.getenv("RAHP_REPOSITORY",DEFAULT_RAHP_REPO)); a=p.parse_args()
    if a.self_test: return self_test()
    dt=os.getenv("GITHUB_TOKEN",""); rt=os.getenv("RAHP_HANDOFF_TOKEN","")
    if not dt: print("GITHUB_TOKEN is required",file=sys.stderr); return 2
    if not rt: print("RAHP_HANDOFF_TOKEN is not configured; completed DPIP dispositions remain pending in the durable outbox.",file=sys.stderr); return 2
    return run(a.dpip_repository,a.rahp_repository,dt,rt,a.issue_number)
if __name__=="__main__": raise SystemExit(main())
