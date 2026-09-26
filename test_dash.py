import requests

BASE = "http://localhost:8080"
print(requests.get(f"{BASE}/").text[:100])
print(requests.get(f"{BASE}/api/state").json())
print(requests.get(f"{BASE}/api/chat/m_001_drmeera_dentist_delhi").json())
