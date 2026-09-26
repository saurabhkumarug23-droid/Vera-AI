import os
import sys
import bot

print("1. Testing Context...")
bot.contexts = {"category": {}, "merchant": {}, "customer": {}, "trigger": {}}
c = bot.ContextPush(scope="category", context_id="test_c", version=1, delivered_at="2026-04-20T00:00:00Z", payload={})

class MockResponse:
    status_code = 200

resp = MockResponse()
r1 = bot.push_context(c, resp)
assert resp.status_code == 200
assert r1["accepted"] == True

r1_again = bot.push_context(c, resp)
assert resp.status_code == 200
assert r1_again["accepted"] == True

c.version = 0
r0 = bot.push_context(c, resp)
assert resp.status_code == 409
assert r0["reason"] == "stale_version"

c.version = 2
resp.status_code = 200
r2 = bot.push_context(c, resp)
assert resp.status_code == 200

c.version = 1
r1_late = bot.push_context(c, resp)
assert resp.status_code == 409

print("Context PASS!")

print("2. Testing Review Theme...")
from datetime import datetime, timezone
merchant = {"merchant_id": "m1", "identity": {"name": "M"}, "performance": {"views": 100}}
trigger = {"_meta": {"kind": "review_theme_emerged", "merchant_id": "m1"}, "payload": {"payload": {"theme": "delivery_late", "occurrences_30d": 4, "trend": "rising"}}}
category = {"slug": "gyms", "voice": {"salutation_examples": ["Hi {first_name}"]}}
res = bot.compose_opportunity(merchant, category, trigger, None, datetime.now(timezone.utc))
assert res is not None
assert "4 recent reviews mention delivery late and the theme is rising" in res["body"]
assert res["action_type"] == "DRAFT_RESPONSE"
print("Review Theme PASS!")

print("3. Testing Replies...")
bot.conversations["c1"] = {
    "state": "PROPOSED",
    "merchant_id": "m1",
    "history": [],
    "pending_action": {"action": "DRAFT_RESPONSE", "theme": "delivery issue"}
}
req = bot.ReplyRequest(conversation_id="c1", merchant_id="m1", from_role="merchant", message="yes please", received_at="", turn_number=1)
reply1 = bot.reply(req)
assert reply1["action"] == "send"
assert "Here is a drafted response" in reply1["body"]

bot.conversations["c2"] = {
    "state": "PROPOSED",
    "merchant_id": "m1",
    "history": [],
    "pending_action": {"action": "EXECUTE_CAMPAIGN"}
}
req.conversation_id = "c2"
reply2 = bot.reply(req)
assert reply2["action"] == "end"

bot.conversations["c3"] = {
    "state": "PROPOSED",
    "merchant_id": "m1",
    "history": [],
    "pending_action": {"action": "EXECUTE_CAMPAIGN"}
}
req.conversation_id = "c3"
req.message = "how much does this cost"
reply3 = bot.reply(req)
assert "I don't have the platform fee details" in reply3["body"]

bot.conversations["c4"] = {
    "state": "PROPOSED",
    "merchant_id": "m1",
    "history": [],
    "pending_action": {"action": "EXECUTE_CAMPAIGN", "offer": {"title": "X", "price": "100"}}
}
req.conversation_id = "c4"
req.message = "what is the price"
reply4 = bot.reply(req)
assert "The cost for 'X' is 100." in reply4["body"]

print("Replies PASS!")

print("All internal checks passed!")
