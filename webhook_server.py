import os
import requests
from fastapi import FastAPI, Request, Response
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="Code2Career Lead Generation Webhook Engine")

VERIFY_TOKEN = os.getenv("META_WEBHOOK_VERIFY_TOKEN", "code2career_secure_token")
ACCESS_TOKEN = os.getenv("INSTAGRAM_ACCESS_TOKEN")
PAGE_ID = os.getenv("INSTAGRAM_USER_ID")
LEAD_MAGNET_URL = os.getenv("LEAD_MAGNET_URL", "https://github.com/RzLetsCode/code2career_marketing_agent?utm_source=ig_dm&utm_medium=chatbot&utm_campaign=lead_magnet")


@app.get("/webhook")
async def verify_webhook(request: Request):
    """Handles Meta webhook verification handshake."""
    mode = request.query_params.get("hub.mode")
    token = request.query_params.get("hub.verify_token")
    challenge = request.query_params.get("hub.challenge")

    if mode and token:
        if mode == "subscribe" and token == VERIFY_TOKEN:
            print("[+] Webhook verified successfully by Meta!")
            return Response(content=challenge, media_type="text/plain")
        return Response(content="Verification failed", status_code=403)
    return Response(content="Invalid request", status_code=400)


@app.post("/webhook")
async def handle_incoming_webhook(request: Request):
    """Captures real-time comment events, checks for keywords, and triggers automated DMs."""
    body = await request.json()
    
    try:
        for entry in body.get("entry", []):
            for change in entry.get("changes", []):
                if change.get("field") == "comments":
                    val = change.get("value", {})
                    comment_text = val.get("text", "").strip().upper()
                    comment_id = val.get("id")
                    from_user = val.get("from", {})
                    user_id = from_user.get("id")
                    user_name = from_user.get("username", "developer")

                    # Target keyword match check (e.g., ARCHITECT, AGENT, REPO)
                    target_keywords = ["ARCHITECT", "AGENT", "REPO", "PIPELINE", "SCALE", "READY"]
                    if any(kw in comment_text for kw in target_keywords):
                        print(f"[+] High-intent lead captured! @{user_name} commented: '{comment_text}'")
                        
                        # 1. Reply publicly to the comment to boost algorithmic reach
                        public_reply_comment(comment_id, f"Check your DMs @{user_name}! Sent you the production repo & checklist 🚀")
                        
                        # 2. Dispatch private lead-magnet DM
                        send_lead_magnet_dm(user_id, user_name)

    except Exception as e:
        print(f"[-] Error processing webhook payload: {e}")

    return {"status": "received"}


def public_reply_comment(comment_id: str, message: str):
    """Sends a public reply to boost post engagement score."""
    url = f"https://graph.facebook.com/v21.0/{comment_id}/replies"
    payload = {
        "message": message,
        "access_token": ACCESS_TOKEN
    }
    requests.post(url, data=payload)


def send_lead_magnet_dm(recipient_id: str, username: str):
    """Sends the automated lead magnet directly to the user's Instagram inbox."""
    url = f"https://graph.facebook.com/v21.0/{PAGE_ID}/messages"
    payload = {
        "recipient": {"id": recipient_id},
        "message": {
            "text": f"Hey {username}! 👋 Thanks for checking out Code2Career_AI.\n\nHere is your requested production-grade architecture starter repository & deployment checklist:\n👉 {LEAD_MAGNET_URL}\n\nLet me know if you hit any snags deploying your agents!"
        },
        "access_token": ACCESS_TOKEN
    }
    res = requests.post(url, json=payload)
    if res.status_code == 200:
        print(f"[+] Successfully delivered lead magnet DM to user {recipient_id}")
    else:
        print(f"[-] Failed to deliver DM: {res.text}")