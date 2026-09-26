import re

with open("bot.py", "r") as f:
    code = f.read()

# Extract from def compose_message(merchant, category, trigger, customer=None):
# to @app.post("/v1/tick")
pattern = re.compile(r'def compose_message\(merchant, category, trigger, customer=None\):.*?@app\.post\("/v1/tick"\)', re.DOTALL)

new_compose = '''def compose_message(merchant, category, trigger, customer=None):
    cat_slug = category.get("slug", "") or merchant.get("category_slug", "")
    m_id = merchant.get("merchant_id", "unknown")
    m_name = merchant.get("identity", {}).get("name", "Merchant")
    owner = merchant.get("identity", {}).get("owner_first_name", "")
    city = merchant.get("identity", {}).get("city", "")
    locality = merchant.get("identity", {}).get("locality", "your area")
    
    perf = merchant.get("performance", {})
    views = perf.get("views", 0)
    ctr = perf.get("ctr", 0.0)
    
    t_kind = trigger.get("kind", "")
    t_payload = trigger.get("payload", {})
    
    offer_text = get_best_offer(merchant)
    
    if cat_slug == "dentists":
        greeting = f"Dr. {owner}" if owner and not owner.startswith("Dr") else f"Doctor"
        action_verb = "book check-ups"
    elif cat_slug == "salons":
        greeting = f"Hi {owner} ✨" if owner else "Hi there ✨"
        action_verb = "book slots"
    elif cat_slug == "gyms":
        greeting = f"Hey {owner} 🏋️" if owner else "Hey Coach"
        action_verb = "drive trials"
    elif cat_slug == "restaurants":
        greeting = f"Hi {owner}," if owner else "Chef,"
        action_verb = "drive orders"
    elif cat_slug == "pharmacies":
        greeting = f"Hello {owner}" if owner else "Hello"
        action_verb = "increase footfalls"
    else:
        greeting = f"Hello {owner}" if owner else "Hello"
        action_verb = "increase footfalls"
        
    body = ""
    cta = "binary_yes_no"
    send_as = "vera"
    rationale = "General optimization"
    urgency = trigger.get("urgency", 3)
    
    if customer:
        c_name = customer.get("identity", {}).get("first_name", "Customer")
        if t_kind == "recall_due":
            due = t_payload.get("service_due", "visit").replace("_", " ")
            slots = t_payload.get("available_slots", [])
            slot_text = slots[0]["label"] if slots else "tomorrow"
            body = f"Hi {c_name}, {m_name} here! It's time for your {due}. Want to book a slot for {slot_text}?"
            rationale = "High-priority direct customer recall"
            urgency = 10
        elif t_kind == "customer_lapsed_hard":
            body = f"Hi {c_name}, {m_name} here! We miss you in {locality}. We have an active '{offer_text}' right now. Reply YES to claim it!"
            rationale = "Direct customer winback"
            urgency = 9
        elif t_kind == "wedding_package_followup":
            days = t_payload.get("days_to_wedding", 30)
            body = f"Hi {c_name}, {days} days to the big day! Want to book your prep session with {m_name}?"
            rationale = "High-conversion bridal followup"
            urgency = 8
        elif t_kind == "trial_followup":
            options = t_payload.get("next_session_options", [])
            slot_text = options[0]["label"] if options else "this weekend"
            body = f"Hi {c_name}, hope you enjoyed your trial at {m_name}! Should I book your next session for {slot_text}?"
            rationale = "Trial conversion followup"
            urgency = 8
        elif t_kind == "chronic_refill_due":
            molecules = t_payload.get("molecule_list", ["medicines"])
            mol_text = molecules[0] if molecules else "medicines"
            body = f"Hi {c_name}, your refill for {mol_text} from {m_name} is due. Shall I schedule delivery?"
            rationale = "Medical refill compliance"
            urgency = 10
        else:
            body = f"Hi {c_name}, {m_name} here from {locality}. We have an update: {offer_text}. Reply YES to claim."
            rationale = "Generic customer outreach"
            urgency = 8
            
        send_as = "merchant_on_behalf"
        supp_key = f"{t_kind}:{c_name}:{m_id}"
        
    else:
        supp_key = f"{t_kind}:{m_id}"
        
        if t_kind == "regulation_change" or t_kind == "compliance_update":
            topic_id = t_payload.get("top_item_id", "")
            topic_title = "a new compliance update"
            deadline = t_payload.get("deadline_iso", "soon")
            digests = category.get("digest", [])
            for d in digests:
                if d.get("id") == topic_id:
                    topic_title = d.get("title", topic_title)
                    break
            body = f"{greeting}, {topic_title} is effective {deadline}. Should I draft a quick summary to help you update your SOPs?"
            rationale = "Compliance/Regulation update"
            urgency = 9
            
        elif t_kind == "research_digest":
            topic_id = t_payload.get("top_item_id", "")
            topic_title = "latest updates"
            digests = category.get("digest", [])
            for d in digests:
                if d.get("id") == topic_id:
                    topic_title = d.get("title", topic_title)
                    break
            body = f"{greeting}, a new update on '{topic_title}' just released that perfectly fits your profile. Should I draft a quick WhatsApp summary for you to share?"
            rationale = "Research demand opportunity"
            urgency = 6
            
        elif t_kind == "perf_dip":
            metric = t_payload.get("metric", "views")
            delta = t_payload.get("delta_pct", 0)
            baseline = t_payload.get("vs_baseline", 0)
            delta_str = str(int(abs(delta) * 100))
            body = f"{greeting}, {metric} in {locality} dipped {delta_str}% this week (vs {baseline} avg). Should we instantly activate '{offer_text}' to recover that traffic today?"
            rationale = "Performance dip recovery"
            urgency = 8
            
        elif t_kind == "perf_spike":
            metric = t_payload.get("metric", "views")
            body = f"{greeting}, huge spike! You hit {views} {metric} recently. Should we run '{offer_text}' right now to capitalize on this momentum?"
            rationale = "Performance spike amplification"
            urgency = 7
            
        elif t_kind == "competitor_spike" or t_kind == "competitor_opened":
            if t_kind == "competitor_opened":
                comp_name = t_payload.get("competitor_name", "A competitor")
                body = f"{greeting}, {comp_name} just opened nearby. Should I send your '{offer_text}' to {views} past customers to defend your base?"
            else:
                body = f"{views} people in {locality} are searching for businesses like yours right now! Should I send them your '{offer_text}' to capture them before competitors do?"
            rationale = "Competitor defense"
            urgency = 8
            
        elif t_kind == "festival_upcoming" or t_kind == "seasonal_moment":
            fest = t_payload.get("festival", t_payload.get("event", "the upcoming festival"))
            body = f"{greeting}, {fest} is almost here! Your profile has {views} views. Should I schedule your '{offer_text}' to go live this weekend to {action_verb}?"
            rationale = "Seasonal/Festival opportunity"
            urgency = 7
            
        elif t_kind == "category_seasonal":
            season = t_payload.get("season", "the season").replace("_", " ")
            body = f"{greeting}, demand shifts are happening for {season}. Should I adjust your GBP profile and push '{offer_text}' to capture this?"
            rationale = "Macro seasonal shift"
            urgency = 6
            
        elif t_kind == "curious_ask_due" or t_kind == "listing_improvement":
            body = f"{views} users in {locality} are active right now. Should I schedule your '{offer_text}' to go live this evening to bring them in?"
            rationale = "General listing optimization"
            urgency = 4
            
        elif t_kind == "active_planning_intent":
            topic = t_payload.get("intent_topic", "your campaign").replace("_", " ")
            msg = t_payload.get("merchant_last_message", "Yes")
            body = f"{greeting}, following up on your request regarding '{topic}'. Should I draft the structure for this now?"
            rationale = "Active merchant conversation followup"
            urgency = 10
            
        elif t_kind == "supply_alert":
            mol = t_payload.get("molecule", "product")
            body = f"{greeting}, there's a supply alert regarding {mol}. Should I pause any active promotions related to this?"
            rationale = "Critical supply chain alert"
            urgency = 9
            
        elif t_kind == "cde_opportunity":
            credits = t_payload.get("credits", 1)
            body = f"{greeting}, a new webinar offering {credits} CDE credits is available. Should I save this to your calendar?"
            rationale = "Professional development opportunity"
            urgency = 5
            
        elif t_kind == "dormant_with_vera":
            body = f"{greeting}, it's been a while since we talked! Your {locality} views are currently {views}. Should I run a quick profile audit?"
            rationale = "Re-engagement outreach"
            urgency = 3
            
        elif t_kind == "gbp_unverified":
            uplift = str(int(t_payload.get("estimated_uplift_pct", 0) * 100))
            body = f"{greeting}, your Google profile is unverified. Verifying can boost {action_verb} by {uplift}%. Should I guide you through it?"
            rationale = "Foundational profile unverified"
            urgency = 9
            
        elif t_kind == "ipl_match_today":
            match = t_payload.get("match", "The match")
            body = f"{greeting}, {match} is happening today! Should I schedule '{offer_text}' to capture the game-time {locality} crowd?"
            rationale = "Hyper-local event opportunity"
            urgency = 7
            
        elif t_kind == "milestone_reached":
            val = t_payload.get("milestone_value", 100)
            body = f"{greeting}, you are about to hit {val} reviews! Should I send '{offer_text}' to your most loyal customers to celebrate?"
            rationale = "Positive reinforcement milestone"
            urgency = 5
            
        elif t_kind == "seasonal_perf_dip":
            delta_str = str(int(abs(t_payload.get("delta_pct", 0)) * 100))
            body = f"{greeting}, views dropped by {delta_str}% due to seasonal shifts. Should we run '{offer_text}' to stabilize your {locality} traffic?"
            rationale = "Expected seasonal dip mitigation"
            urgency = 5
            
        elif t_kind == "winback_eligible":
            lapsed = t_payload.get("lapsed_customers_added_since_expiry", 10)
            body = f"{greeting}, you have {lapsed} recently lapsed customers. Should I send '{offer_text}' to bring them back?"
            rationale = "High-ROI winback target"
            urgency = 7
            
        elif t_kind == "renewal_due":
            days = t_payload.get("days_remaining", 7)
            body = f"{greeting}, your Pro plan expires in {days} days. Should I process your renewal to keep your {views} monthly views growing?"
            rationale = "Subscription retention"
            urgency = 10
            
        else:
            body = f"{greeting}, based on recent activity in {locality} (your views: {views}), running '{offer_text}' can help. Shall I schedule a post for tomorrow?"
            rationale = "Generic fallback"
            urgency = 2

    draft = {
        "should_send": True, "body": body, "cta": cta,
        "send_as": send_as, "suppression_key": supp_key,
        "rationale": rationale, "urgency": urgency
    }
    
    if not validate_grounding(draft["body"], [merchant, category, trigger, customer]):
        return fallback_compose(merchant, category)
        
    return draft

@app.post("/v1/tick")'''

code = pattern.sub(new_compose, code)

with open("bot.py", "w") as f:
    f.write(code)
