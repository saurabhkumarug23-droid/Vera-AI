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
