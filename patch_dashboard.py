import re

with open("bot.py", "r") as f:
    code = f.read()

# 1. Add FileResponse and Mount
if "from fastapi.responses import HTMLResponse, FileResponse" not in code:
    code = code.replace("from fastapi.responses import HTMLResponse", "from fastapi.responses import HTMLResponse, FileResponse")
    code = code.replace("from fastapi import FastAPI, HTTPException, Response", "from fastapi import FastAPI, HTTPException, Response\nfrom fastapi.staticfiles import StaticFiles")

# 2. Add /api/state, /api/chat, and / endpoints
dashboard_endpoints = '''@app.get("/")
def serve_root():
    return FileResponse("static/index.html")

@app.get("/api/state")
def get_dashboard_state():
    merch_list = []
    for mid, mnode in contexts.get("merchant", {}).items():
        if mnode and "payload" in mnode:
            merch_list.append(mnode["payload"])
            
    trigger_list = []
    for tid, tnode in contexts.get("trigger", {}).items():
        if tnode and "payload" in tnode:
            raw = tnode["payload"]
            trigger_list.append({
                "id": raw.get("id", tid),
                "merchant_id": raw.get("merchant_id"),
                "kind": raw.get("kind"),
                "urgency": raw.get("urgency", 5)
            })
            
    return {"merchants": merch_list, "triggers": trigger_list}

@app.get("/api/chat/{merchant_id}")
def get_chat(merchant_id: str):
    chats = []
    # Collect all conversations for this merchant
    for cid, conv in conversations.items():
        if conv.get("merchant_id") == merchant_id:
            for i, h in enumerate(conv.get("history", [])):
                chats.append({
                    "role": h.get("role", "vera"),
                    "message": h.get("message", ""),
                    "time": datetime.utcnow().isoformat() + "Z",
                    "intent": conv.get("state") if i == len(conv["history"])-1 else ""
                })
    return chats

'''

if "@app.get(\"/\")" not in code:
    # insert before @app.get("/v1/healthz")
    code = code.replace('@app.get("/v1/healthz")', dashboard_endpoints + '@app.get("/v1/healthz")')
    
    # Mount static files just after app = FastAPI()
    code = code.replace('app = FastAPI()\n', 'app = FastAPI()\napp.mount("/static", StaticFiles(directory="static"), name="static")\n')

# 3. Rename reply to _reply_internal and wrap it
code = code.replace('@app.post("/v1/reply")\ndef reply(data: ReplyRequest):', '''def _reply_internal(data: ReplyRequest):''')

reply_wrapper = '''@app.post("/v1/reply")
def reply(data: ReplyRequest):
    res = _reply_internal(data)
    # Save Vera's response to history so the dashboard can render it
    if res and res.get("action") == "send" and "body" in res:
        conv_id = data.conversation_id
        if conv_id in conversations:
            conversations[conv_id]["history"].append({
                "role": "vera",
                "message": res["body"]
            })
    return res

'''
code = code.replace('def _reply_internal(data: ReplyRequest):', reply_wrapper + 'def _reply_internal(data: ReplyRequest):')

with open("bot.py", "w") as f:
    f.write(code)
