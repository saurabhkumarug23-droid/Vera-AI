import re

with open("bot.py", "r") as f:
    code = f.read()

# Replace push_context
old_push = '''    node = {
        "payload": data.payload,
        "_meta": {
            "version": data.version,
            "delivered_at": data.delivered_at,
            "urgency": data.urgency,
            "suppression_key": data.suppression_key,
            "expires_at": data.expires_at,
            "kind": data.kind,
            "source": data.source,
            "merchant_id": data.merchant_id,
            "customer_id": data.customer_id
        }
    }'''

new_push = '''    node = {
        "payload": data.payload,
        "_meta": {
            "version": data.version,
            "delivered_at": data.delivered_at,
            "urgency": data.payload.get("urgency"),
            "suppression_key": data.payload.get("suppression_key"),
            "expires_at": data.payload.get("expires_at"),
            "kind": data.payload.get("kind"),
            "source": data.payload.get("source"),
            "merchant_id": data.payload.get("merchant_id"),
            "customer_id": data.payload.get("customer_id")
        }
    }'''

code = code.replace(old_push, new_push)

old_compose_start = '''def compose_opportunity(merchant: dict, category: dict, trigger: dict, customer: dict, now: str) -> dict:
    t_meta = trigger.get("_meta", {})
    t_payload = trigger.get("payload", {})
    t_kind = t_meta.get("kind", "")'''

new_compose_start = '''def compose_opportunity(merchant: dict, category: dict, trigger: dict, customer: dict, now: str) -> dict:
    t_meta = trigger.get("_meta", {})
    t_payload = trigger.get("payload", {}).get("payload", {})
    t_kind = t_meta.get("kind", "")'''

code = code.replace(old_compose_start, new_compose_start)

with open("bot.py", "w") as f:
    f.write(code)
