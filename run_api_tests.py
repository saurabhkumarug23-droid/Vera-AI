import requests
import json
from datetime import datetime

url = "http://localhost:8081/v1"
print("Healthz:", requests.get(f"{url}/healthz").json())
print("Metadata:", requests.get(f"{url}/metadata").json())

# Context version tests
payload = {"scope": "category", "context_id": "test_c", "version": 1, "delivered_at": "2026-04-20T00:00:00Z", "payload": {}}
r1 = requests.post(f"{url}/context", json=payload)
assert r1.status_code == 200
print("Version 1 ->", r1.json())

r1_again = requests.post(f"{url}/context", json=payload)
assert r1_again.status_code == 200
print("Version 1 again ->", r1_again.json())

payload["version"] = 0
r0 = requests.post(f"{url}/context", json=payload)
assert r0.status_code == 409
assert r0.json()["reason"] == "stale_version"
print("Version 0 ->", r0.json())

payload["version"] = 2
r2 = requests.post(f"{url}/context", json=payload)
assert r2.status_code == 200
print("Version 2 ->", r2.json())

payload["version"] = 1
r1_late = requests.post(f"{url}/context", json=payload)
assert r1_late.status_code == 409
print("Version 1 late ->", r1_late.json())

# Reply tests
print("Reply Yes ->", requests.post(f"{url}/reply", json={"conversation_id": "c1", "merchant_id": "m1", "from_role": "merchant", "message": "yes please", "received_at": "...", "turn_number": 1}).json())
print("Reply Not Today ->", requests.post(f"{url}/reply", json={"conversation_id": "c1", "merchant_id": "m1", "from_role": "merchant", "message": "not today", "received_at": "...", "turn_number": 2}).json())
print("Reply Price ->", requests.post(f"{url}/reply", json={"conversation_id": "c1", "merchant_id": "m1", "from_role": "merchant", "message": "what is the price", "received_at": "...", "turn_number": 3}).json())

print("API Tests Passed!")
