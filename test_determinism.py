from bot import tick, TickRequest
import bot

# Mock state
bot.contexts = {
    "trigger": {"t1": {"_meta": {"kind": "test", "merchant_id": "m1", "expires_at": "2027-01-01T00:00:00Z"}}},
    "merchant": {"m1": {"payload": {"merchant_id": "m1", "identity": {"name": "test m", "owner_first_name": "Test"}}}},
    "category": {},
    "customer": {}
}
bot.suppressions = set()
bot.conversations = {}

results = set()
for _ in range(100):
    res = tick(TickRequest(now="2026-04-20T00:00:00Z", available_triggers=["t1"]))
    results.add(str(res))
    bot.suppressions = set() # reset
    bot.conversations = {} # reset

assert len(results) == 1
print("Unique outputs == 1 (100 times)")
