import bot

# Setup state
bot.conversations = {"conv_manual": {"merchant_id": "m1", "state": "IDLE", "history": [], "pending_action": {}}}
req = bot.ReplyRequest(conversation_id="conv_manual", merchant_id="m1", from_role="merchant", message="not today", received_at="", turn_number=1)

res = bot.reply(req)
print("Action Result:", res)
print("History Length:", len(bot.conversations["conv_manual"]["history"]))
print("History:", bot.conversations["conv_manual"]["history"])

# Try something that returns "send"
req = bot.ReplyRequest(conversation_id="conv_manual", merchant_id="m1", from_role="merchant", message="what is the price", received_at="", turn_number=2)
res = bot.reply(req)
print("History Length (After Question):", len(bot.conversations["conv_manual"]["history"]))
print("Last message:", bot.conversations["conv_manual"]["history"][-1])
