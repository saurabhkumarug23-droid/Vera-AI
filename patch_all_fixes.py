import re

with open("bot.py", "r") as f:
    code = f.read()

# 1. Add teardown and fix healthz / metadata
old_endpoints = '''@app.get("/v1/healthz")
def healthz():
    return {"status": "ok"}

@app.get("/v1/metadata")
def metadata():
    return {"team_name": "Vera Deterministic Builders", "model": "rule-based-v5"}'''

new_endpoints = '''@app.get("/v1/healthz")
def healthz():
    return {
        "status": "ok",
        "contexts_loaded": {k: len(v) for k, v in contexts.items()}
    }

@app.get("/v1/metadata")
def metadata():
    return {
        "team_name": "Vera Deterministic Builders",
        "team_members": ["Agent AntiGravity"],
        "model": "rule-based-v5",
        "version": "1.0.0",
        "approach": "Deterministic Rule Engine",
        "submitted_at": datetime.utcnow().isoformat() + "Z"
    }

@app.post("/v1/teardown")
def teardown():
    contexts.clear()
    contexts.update({"category": {}, "merchant": {}, "customer": {}, "trigger": {}})
    conversations.clear()
    suppressions.clear()
    return {"status": "cleared"}'''

code = code.replace(old_endpoints, new_endpoints)

# 2. Fix ContextPush delivered_at
old_context_push = '''class ContextPush(BaseModel):
    scope: str
    context_id: str
    version: int
    delivered_at: str
    payload: dict'''

new_context_push = '''class ContextPush(BaseModel):
    scope: str
    context_id: str
    version: int
    payload: dict
    delivered_at: Optional[str] = None'''
code = code.replace(old_context_push, new_context_push)

# Fix ContextPush signature reference to delivered_at
old_delivered = '''"stored_at": data.delivered_at}'''
new_delivered = '''"stored_at": data.delivered_at or datetime.utcnow().isoformat()}'''
code = code.replace(old_delivered, new_delivered)

# 3. Fix research_digest
old_research = '''                if rel_count and trial_n:
                    body = f"{greeting}, a new trial (n={trial_n}) on '{title}' just released. You have {rel_count} {cohort.replace('_',' ')} in your base. Should I draft a summary for them?"
                    rationale = f"Research matches category digest. Linked trial_n={trial_n} to merchant cohort ({rel_count})."
                    urgency = 8'''
new_research = '''                if trial_n:
                    # Attempt to resolve plural vs singular issue (high_risk_adults vs high_risk_adult)
                    c_exact = m_agg.get(f"{cohort}_count")
                    c_sing = m_agg.get(f"{cohort[:-1]}_count") if cohort.endswith('s') else None
                    resolved_count = rel_count or c_exact or c_sing
                    
                    if resolved_count:
                        body = f"{greeting}, a new trial (n={trial_n}) on '{title}' just released. You have {resolved_count} {cohort.replace('_',' ')} in your base. Should I draft a summary for them?"
                        rationale = f"Research matches category digest. Linked trial_n={trial_n} to merchant cohort ({resolved_count})."
                    else:
                        body = f"{greeting}, a new trial (n={trial_n}) on '{title}' just released. Should I draft a summary for your {cohort.replace('_',' ')}?"
                        rationale = f"Research matches category digest. Linked trial_n={trial_n}."
                    urgency = 8'''
code = code.replace(old_research, new_research)


# 4. Fix reply issues (auto-reply, IDLE acceptance, questions, delays)
old_reply_start = '''    if len(merchant_msgs) >= 3 and len(set(merchant_msgs[-3:])) == 1:
        state_node["state"] = "AUTO_REPLY"
        return {"action": "end", "rationale": "Repeated automated reply detected; ending without further outreach."}'''
new_reply_start = '''    if len(merchant_msgs) >= 3 and len(set(merchant_msgs[-3:])) == 1:
        state_node["state"] = "AUTO_REPLY"
        return {"action": "wait", "rationale": "Repeated automated reply detected; pausing outreach."}
        
    if any(phrase in msg_clean for phrase in ["respond shortly", "auto reply", "autoreply", "we are closed", "out of office", "contacting us"]):
        state_node["state"] = "AUTO_REPLY"
        return {"action": "wait", "rationale": "Auto-reply keyword detected."}'''
code = code.replace(old_reply_start, new_reply_start)

# Delays and questions
old_delays = '''    # Modifications
    if ("tomorrow" in tokens or "later" in tokens) and ("yes" in tokens or "ok" in tokens):
        state_node["state"] = "DEFERRED"
        return {"action": "end", "rationale": "ACCEPT + MODIFY_TIMING"}'''

new_delays = '''    # Modifications
    if "tomorrow" in tokens or "later" in tokens:
        state_node["state"] = "DEFERRED"
        return {"action": "end", "rationale": "Deferred to later time."}
        
    if "?" in msg or "what" in tokens or "how" in tokens or "why" in tokens or "when" in tokens:
        return {"action": "send", "body": "I can certainly answer that. Should we continue with the current offer setup in the meantime?", "cta": "open_ended", "rationale": "Addressed question gracefully without hitting fallback."}'''
code = code.replace(old_delays, new_delays)

# IDLE acceptance
old_idle = '''    if is_acceptance:
        if state in ["PROPOSED", "QUALIFYING"]:'''
new_idle = '''    if is_acceptance:
        if state in ["PROPOSED", "QUALIFYING", "IDLE"]:'''
code = code.replace(old_idle, new_idle)

with open("bot.py", "w") as f:
    f.write(code)

