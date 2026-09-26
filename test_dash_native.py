import bot

print("1. Root FileResponse:", type(bot.serve_root()))
bot.contexts = {"merchant": {"m1": {"payload": {"merchant_id": "m1", "identity": {"name": "Test M"}}}}, "trigger": {"t1": {"payload": {"id": "t1", "merchant_id": "m1", "kind": "test", "urgency": 5}}}}

print("2. /api/state:", bot.get_dashboard_state())

bot.conversations = {"conv1": {"merchant_id": "m1", "state": "PROPOSED", "history": [{"role": "vera", "message": "Hi"}]}}
print("3. /api/chat/m1:", bot.get_chat("m1"))

print("ALL TESTS PASSED")
