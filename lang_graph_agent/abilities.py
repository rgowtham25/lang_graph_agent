# abilities.py code from earlier answer
from __future__ import annotations
from typing import Dict, Any, List
import re
import random

# ---- COMMON server abilities (internal, no external data) ----
def accept_payload(state: Dict[str, Any], log: List[str]) -> Dict[str, Any]:
    log.append("[COMMON] accept_payload: captured initial payload")
    state.setdefault("status", "new")
    return state

def parse_request_text(state: Dict[str, Any], log: List[str]) -> Dict[str, Any]:
    text = state.get("query", "")
    # naive structure: extract words as tokens
    tokens = re.findall(r"[a-zA-Z]+", text.lower())
    state["tokens"] = tokens
    log.append(f"[COMMON] parse_request_text: tokens={tokens[:6]}{'...' if len(tokens)>6 else ''}")
    return state

def normalize_fields(state: Dict[str, Any], log: List[str]) -> Dict[str, Any]:
    # standardize priority
    pri = str(state.get("priority", "")).lower().strip()
    mapping = {"p0":"high", "p1":"high", "p2":"medium", "p3":"low"}
    if pri in mapping: pri = mapping[pri]
    if pri not in {"low","medium","high"}: pri = "medium"
    state["priority"] = pri
    log.append(f"[COMMON] normalize_fields: priority={pri}")
    return state

def add_flags_calculations(state: Dict[str, Any], log: List[str]) -> Dict[str, Any]:
    # simple SLA risk: high priority => higher risk
    risk = {"low": 0.1, "medium": 0.3, "high": 0.7}[state["priority"]]
    state["sla_risk"] = risk
    log.append(f"[COMMON] add_flags_calculations: sla_risk={risk}")
    return state

def store_answer(state: Dict[str, Any], log: List[str]) -> Dict[str, Any]:
    ans = state.get("ask_answer", None)
    if ans:
        state.setdefault("answers", []).append(ans)
        log.append(f"[COMMON] store_answer: stored answer: {ans}")
    else:
        log.append("[COMMON] store_answer: nothing to store")
    return state

def store_data(state: Dict[str, Any], log: List[str]) -> Dict[str, Any]:
    if "kb_result" in state:
        state.setdefault("retrievals", []).append(state["kb_result"])
        log.append("[COMMON] store_data: KB result attached to payload")
    return state

def solution_evaluation(state: Dict[str, Any], log: List[str]) -> Dict[str, Any]:
    # score based on presence of solution keywords
    kb = state.get("kb_result", {})
    score = 60
    if "solution" in kb: score += 20
    if "restart" in str(kb).lower(): score += 10
    if state.get("priority") == "high": score += 5
    state["solution_score"] = min(score, 100)
    log.append(f"[COMMON] solution_evaluation: score={state['solution_score']}")
    return state

def update_payload(state: Dict[str, Any], log: List[str]) -> Dict[str, Any]:
    # record decision
    esc = state.get("escalated", False)
    state.setdefault("decisions", []).append({"escalated": esc, "score": state.get("solution_score", None)})
    log.append(f"[COMMON] update_payload: decisions updated {state['decisions'][-1]}")
    return state

def response_generation(state: Dict[str, Any], log: List[str]) -> Dict[str, Any]:
    if state.get("escalated"):
        resp = f"Hi {state.get('customer_name')}, your ticket {state.get('ticket_id')} has been escalated to a specialist. We will update you shortly."
    else:
        sol = state.get("kb_result", {}).get("solution", "We are investigating your issue.")
        resp = f"Hi {state.get('customer_name')}, based on our checks, please try: {sol}"
    state["response_text"] = resp
    log.append("[COMMON] response_generation: drafted customer reply")
    return state

def output_payload(state: Dict[str, Any], log: List[str]) -> Dict[str, Any]:
    log.append("[COMMON] output_payload: finalized payload ready")
    return state


# ---- ATLAS server abilities (external interactions simulated) ----
def extract_entities(state: Dict[str, Any], log: List[str]) -> Dict[str, Any]:
    text = state.get("query", "").lower()
    product = None
    for p in ["internet", "wifi", "router", "billing", "account", "payment"]:
        if p in text:
            product = p
            break
    if product: state["product"] = product
    log.append(f"[ATLAS] extract_entities: product={product}")
    return state

def enrich_records(state: Dict[str, Any], log: List[str]) -> Dict[str, Any]:
    # pretend to pull from CRM/SLA system
    pri = state.get("priority", "medium")
    sla = {"low":"24h","medium":"8h","high":"4h"}[pri]
    history = [{"ticket_id":"HIST1001","status":"resolved"},{"ticket_id":"HIST1002","status":"resolved"}]
    state["sla"] = sla
    state["history"] = history
    log.append(f"[ATLAS] enrich_records: sla={sla}, history_count={len(history)}")
    return state

def clarify_question(state: Dict[str, Any], log: List[str]) -> Dict[str, Any]:
    # simulate asking for missing critical field (location)
    if "location" not in state:
        state["ask_prompt"] = "Could you share your location (city) so we can troubleshoot network availability?"
        log.append("[ATLAS] clarify_question: requested location from customer")
    else:
        log.append("[ATLAS] clarify_question: no clarification needed")
    return state

def extract_answer(state: Dict[str, Any], log: List[str]) -> Dict[str, Any]:
    # simulate the customer replying; for demo we auto-fill
    if "ask_prompt" in state:
        state["ask_answer"] = "Bengaluru"
        state["location"] = state["ask_answer"]
        log.append("[ATLAS] extract_answer: captured customer reply 'Bengaluru'")
    else:
        log.append("[ATLAS] extract_answer: no pending question")
    return state

def knowledge_base_search(state: Dict[str, Any], log: List[str]) -> Dict[str, Any]:
    # very simple KB: if router/internet issues -> restart steps
    text = (state.get("query","") + " " + " ".join(state.get("tokens",[]))).lower()
    if any(k in text for k in ["internet","wifi","router","not working","down","slow"]):
        result = {
            "article_id": "KB-2001",
            "title": "Internet down / Router troubleshooting",
            "solution": "Restart your router: power off for 30 seconds, then power on; check cables and LEDs."
        }
    elif "billing" in text or "payment" in text:
        result = {
            "article_id": "KB-3100",
            "title": "Billing inquiry steps",
            "solution": "Verify recent invoices in the portal; if discrepancy persists, raise a billing review ticket."
        }
    else:
        result = {
            "article_id": "KB-0000",
            "title": "General support",
            "solution": "Please provide more details about the issue."
        }
    state["kb_result"] = result
    log.append(f"[ATLAS] knowledge_base_search: found {result['article_id']}")
    return state

def escalation_decision(state: Dict[str, Any], log: List[str]) -> Dict[str, Any]:
    score = state.get("solution_score", 0)
    state["escalated"] = score < 90
    log.append(f"[ATLAS] escalation_decision: escalated={state['escalated']} (score={score})")
    return state

def update_ticket(state: Dict[str, Any], log: List[str]) -> Dict[str, Any]:
    state["status"] = "in-progress" if state.get("escalated") else "resolving"
    log.append(f"[ATLAS] update_ticket: status={state['status']}")
    return state

def close_ticket(state: Dict[str, Any], log: List[str]) -> Dict[str, Any]:
    if not state.get("escalated"):
        state["status"] = "resolved"
        log.append("[ATLAS] close_ticket: ticket closed as resolved")
    else:
        log.append("[ATLAS] close_ticket: left open due to escalation")
    return state

def execute_api_calls(state: Dict[str, Any], log: List[str]) -> Dict[str, Any]:
    # simulate external API (e.g., reset line, push config)
    actions = []
    if state.get("product") in {"internet","wifi","router"} and not state.get("escalated"):
        actions.append("remote_line_reset")
    state["api_actions"] = actions
    log.append(f"[ATLAS] execute_api_calls: actions={actions}")
    return state

def trigger_notifications(state: Dict[str, Any], log: List[str]) -> Dict[str, Any]:
    state["notification_sent"] = True
    log.append("[ATLAS] trigger_notifications: customer notified via email")
    return state
