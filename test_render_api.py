import requests
import json
import sys

BASE_URL = "https://vera-ai-5ffi.onrender.com/v1"
success = True

def print_result(name, res, expected_status=200):
    global success
    status = res.status_code
    try:
        data = res.json()
    except:
        data = res.text
        
    if status == expected_status:
        print(f"✅ [PASS] {name} (Status: {status})")
    else:
        print(f"❌ [FAIL] {name} (Expected {expected_status}, Got {status})")
        print(f"   Response: {data}")
        success = False

print(f"Testing API at: {BASE_URL}\n")

# 1. Health check
print_result("Healthz Endpoint", requests.get(f"{BASE_URL}/healthz"))

# 2. Metadata check
print_result("Metadata Endpoint", requests.get(f"{BASE_URL}/metadata"))

# 3. Context Push check
payload = {
    "scope": "category",
    "context_id": "test_render_category",
    "version": 1,
    "delivered_at": "2026-04-20T00:00:00Z",
    "payload": {"slug": "gyms"}
}
# Push V1
print_result("Context Push (V1)", requests.post(f"{BASE_URL}/context", json=payload))

# Push V1 again (Idempotent)
print_result("Context Push (Idempotent V1)", requests.post(f"{BASE_URL}/context", json=payload))

# Push V0 (Stale)
payload["version"] = 0
print_result("Context Push (Stale V0)", requests.post(f"{BASE_URL}/context", json=payload), expected_status=409)

# Push V2 (Update)
payload["version"] = 2
print_result("Context Push (Update V2)", requests.post(f"{BASE_URL}/context", json=payload))

# 4. Tick check
tick_payload = {
    "now": "2026-04-20T10:00:00Z",
    "available_triggers": []
}
print_result("Tick (Empty)", requests.post(f"{BASE_URL}/tick", json=tick_payload))

# 5. Reply check
reply_payload = {
    "conversation_id": "render_test_conv",
    "merchant_id": "m1",
    "from_role": "merchant",
    "message": "hello",
    "received_at": "2026-04-20T10:01:00Z",
    "turn_number": 1
}
print_result("Reply (Basic)", requests.post(f"{BASE_URL}/reply", json=reply_payload))

if success:
    print("\n🎉 ALL TESTS PASSED! The API is working perfectly.")
else:
    print("\n⚠️ SOME TESTS FAILED.")
    sys.exit(1)
