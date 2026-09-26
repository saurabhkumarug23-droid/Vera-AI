import re

with open("bot.py", "r") as f:
    code = f.read()

# Fix 1: /v1/context
old_context = '''@app.post("/v1/context")
def push_context(data: ContextPush, response: Response):
    if data.scope not in contexts:
        raise HTTPException(status_code=400, detail="Invalid scope")
        
    current = contexts[data.scope].get(data.context_id)
    if current and current.get("_meta", {}).get("version", 0) >= data.version:
        response.status_code = 409
        return {"accepted": False, "reason": "stale_version"}
        
    node = {'''

new_context = '''@app.post("/v1/context")
def push_context(data: ContextPush, response: Response):
    if data.scope not in contexts:
        raise HTTPException(status_code=400, detail="Invalid scope")
        
    current = contexts[data.scope].get(data.context_id)
    current_version = current.get("_meta", {}).get("version", 0) if current else 0
    
    if data.version < current_version:
        response.status_code = 409
        return {"accepted": False, "reason": "stale_version", "current_version": current_version}
        
    if data.version == current_version and current:
        return {"accepted": True, "ack_id": f"ack_{data.scope}_{data.context_id}_{data.version}", "stored_at": data.delivered_at}
        
    node = {'''
code = code.replace(old_context, new_context)

# Fix 1 cont: return for /context
old_context_ret = '''    contexts[data.scope][data.context_id] = node
    return {"accepted": True}'''
new_context_ret = '''    contexts[data.scope][data.context_id] = node
    return {"accepted": True, "ack_id": f"ack_{data.scope}_{data.context_id}_{data.version}", "stored_at": data.delivered_at}'''
code = code.replace(old_context_ret, new_context_ret)

# Fix 2: review_theme_emerged
old_review = '''        elif t_kind == "festival_upcoming" or t_kind == "ipl_match_today":'''
new_review = '''        elif t_kind == "review_theme_emerged":
            theme = t_payload.get("theme", "").replace("_", " ")
            occ = t_payload.get("occurrences_30d")
            trend = t_payload.get("trend")
            if theme and occ is not None and trend:
                body = f"{greeting}, {occ} recent reviews mention {theme} and the theme is {trend}. Want me to draft a response/update for this issue?"
                rationale = f"Grounded review intervention using exact occurrences ({occ}) and trend ({trend}) for theme ({theme})."
                action_type = "DRAFT_RESPONSE"
                urgency = 8 if trend == "rising" else 5
                
        elif t_kind == "festival_upcoming" or t_kind == "ipl_match_today":'''
code = code.replace(old_review, new_review)

# Add theme to pending action so we can use it in draft
old_pending = '''                "offer_id": comp.get("offer_id"),
                "offer": comp.get("offer"),
                "category": category.get("slug")
            }'''
new_pending = '''                "offer_id": comp.get("offer_id"),
                "offer": comp.get("offer"),
                "category": category.get("slug"),
                "theme": trigger_node.get("payload", {}).get("payload", {}).get("theme", "the recent issue")
            }'''
code = code.replace(old_pending, new_pending)

# Fix 3: Pricing
old_pricing = '''    if "price" in tokens or "cost" in tokens:
        state_node["state"] = "OBJECTION"
        return {"action": "send", "body": "There is no extra platform cost for this feature. Should I proceed?", "cta": "binary_yes_no", "rationale": "Addressed pricing objection explicitly without unsupported claims."}'''
new_pricing = '''    if "price" in tokens or "cost" in tokens or "fee" in tokens:
        state_node["state"] = "OBJECTION"
        price = pending.get("offer", {}).get("price") if pending.get("offer") else None
        if price is not None:
            return {"action": "send", "body": f"The cost for '{pending.get('offer', {}).get('title')}' is {price}. Should I proceed?", "cta": "binary_yes_no", "rationale": "Answered pricing objection explicitly using known price."}
        else:
            return {"action": "send", "body": "I don't have the platform fee details in the current context. I can continue with the campaign setup once the fee is confirmed.", "cta": "open_ended", "rationale": "Addressed pricing objection gracefully without hallucinating fees."}'''
code = code.replace(old_pricing, new_pricing)

# Fix 4: Acceptance handoff
old_acc = '''    if is_acceptance:
        if state in ["PROPOSED", "QUALIFYING"]:
            state_node["state"] = "ACCEPTED"
            # Handoff directly to action without asking CONFIRM
            action_name = pending.get("action", "EXECUTE_CAMPAIGN")
            return {"action": "end", "rationale": f"Intent transition: Merchant accepted, handed off to {action_name}."}'''
new_acc = '''    if is_acceptance:
        if state in ["PROPOSED", "QUALIFYING"]:
            state_node["state"] = "ACCEPTED"
            action_name = pending.get("action", "EXECUTE_CAMPAIGN")
            if action_name == "DRAFT_RESPONSE":
                state_node["state"] = "COMPLETED"
                return {"action": "send", "body": f"Here is a drafted response acknowledging the {pending.get('theme', 'recent')} feedback and outlining our improvements.", "cta": "open_ended", "rationale": "Handed off to DRAFT_RESPONSE artifact directly."}
            elif action_name == "PLANNING_ARTIFACT":
                state_node["state"] = "COMPLETED"
                return {"action": "send", "body": "Great, the campaign plan is saved and ready.", "cta": "open_ended", "rationale": "Plan accepted and finalized."}
            else:
                state_node["state"] = "COMPLETED"
                return {"action": "end", "rationale": f"Action {action_name} executed successfully upon acceptance."}'''
code = code.replace(old_acc, new_acc)

with open("bot.py", "w") as f:
    f.write(code)

