import requests
url = "http://localhost:8081/v1"
requests.post(f"{url}/reply", json={"conversation_id": "c100", "merchant_id": "m1", "from_role": "merchant", "message": "hello", "received_at": "...", "turn_number": 1})
# Wait, reply doesn't set state to PROPOSED. We need to tick first to set state!
