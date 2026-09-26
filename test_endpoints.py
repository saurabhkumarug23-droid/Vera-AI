import requests

BASE = "http://localhost:8080/v1"

# 1. Healthz
r = requests.get(f"{BASE}/healthz")
print("Healthz:", r.json())
assert "contexts_loaded" in r.json()

# 2. Metadata
r = requests.get(f"{BASE}/metadata")
print("Metadata:", r.json())
assert "version" in r.json()
assert "approach" in r.json()
assert "submitted_at" in r.json()
assert "team_members" in r.json()

# 3. ContextPush without delivered_at
payload = {
    "scope": "merchant",
    "context_id": "m1",
    "version": 1,
    "payload": {"name": "Test"}
}
r = requests.post(f"{BASE}/context", json=payload)
print("ContextPush:", r.status_code)
assert r.status_code == 200

# 4. Teardown
r = requests.post(f"{BASE}/teardown")
print("Teardown:", r.json())
assert r.status_code == 200

print("All new endpoint fixes pass.")
