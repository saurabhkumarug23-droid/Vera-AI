#!/bin/bash
set -e
echo "A. Compiling..."
python3 -m py_compile bot.py

echo "B. Generating dataset..."
python3 dataset/generate_dataset.py --seed-dir dataset --out expanded

echo "D. Checking Determinism..."
# Testing bot API tick outputs given identical context
cat << 'PY_EOF' > test_determinism.py
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
PY_EOF
python3 test_determinism.py

echo "E. Testing placeholders..."
cat << 'PY_EOF' > test_placeholders.py
import re
from bot import compose_opportunity
from datetime import datetime, timezone

merchant = {"identity": {"name": "M"}, "performance": {"views": 100}}
trigger = {"_meta": {"kind": "generic", "merchant_id": "m1"}, "payload": {"payload": {}}}
category = {"slug": "gyms", "voice": {"salutation_examples": ["Hi {first_name}"]}}
res = compose_opportunity(merchant, category, trigger, None, datetime.now(timezone.utc))
if res:
    assert "{" not in res["body"] and "}" not in res["body"]
    print("Placeholder test passed.")
PY_EOF
python3 test_placeholders.py

echo "Regression checks complete!"
