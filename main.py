from fastapi import FastAPI, Header, HTTPException, Body
from pydantic import BaseModel
import time
import random
import re
import os

# -------------------------
# API KEY
# -------------------------

API_KEY = os.getenv("API_KEY")

app = FastAPI(title="Agentic Scam Honeypot")

# -------------------------
# DATA MODEL
# -------------------------

class ScamMessage(BaseModel):
    conversation_id: str
    message: str

# -------------------------
# SESSION MEMORY
# -------------------------

sessions = {}

# -------------------------
# SCAM DETECTION
# -------------------------

SCAM_KEYWORDS = [
    "blocked", "verify", "urgent", "otp",
    "kyc", "bank", "account", "click",
    "pay", "payment", "suspended"
]

def detect_scam(text: str) -> bool:
    text = text.lower()
    return any(word in text for word in SCAM_KEYWORDS)

# -------------------------
# DYNAMIC HUMAN AGENT
# -------------------------

CONFUSION = [
    "I’m not fully understanding",
    "I might be doing something wrong",
    "I’m a bit confused here",
    "I don’t usually handle these things"
]

ACTIONS = [
    "I tried paying",
    "I clicked the link",
    "I entered the details",
    "I followed the steps"
]

OUTCOMES = [
    "but it failed",
    "and it showed an error",
    "but nothing happened",
    "and it got stuck"
]

HUMAN_FILLERS = [
    "",
    " …",
    " uh",
    " please help",
    " I’m worried"
]

def agent_reply():
    time.sleep(random.uniform(1.5, 3.5))
    return " ".join([
        random.choice(CONFUSION),
        random.choice(ACTIONS),
        random.choice(OUTCOMES),
        random.choice(HUMAN_FILLERS)
    ]).strip()

# -------------------------
# INTELLIGENCE EXTRACTION
# -------------------------

def extract_intelligence(text: str):
    return {
        "upi_ids": re.findall(r"[a-zA-Z0-9.\-_]+@[a-zA-Z]+", text),
        "phishing_urls": re.findall(r"https?://[^\s]+", text),
        "bank_accounts": re.findall(r"\b\d{9,18}\b", text)
    }

# -------------------------
# ROOT (OPTIONAL)
# -------------------------

@app.get("/")
def home():
    return {
        "message": "Agentic Scam Honeypot API is running",
        "usage": "POST /webhook with API key"
    }

# -------------------------
# MAIN API ENDPOINT (POST)
# -------------------------

@app.post("/webhook")
def receive_message(
    data: ScamMessage = Body(
        default=ScamMessage(
            conversation_id="auto_test",
            message=""
        )
    ),
    x_api_key: str = Header(None)
):
    # API key check
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API key")

    # create session if new
    if data.conversation_id not in sessions:
        sessions[data.conversation_id] = {
            "turns": 0,
            "start_time": time.time(),
            "intel": {
                "upi_ids": [],
                "phishing_urls": [],
                "bank_accounts": []
            }
        }

    session = sessions[data.conversation_id]
    session["turns"] += 1

    # scam detection
    is_scam = detect_scam(data.message)

    # intelligence extraction
    extracted = extract_intelligence(data.message)
    for key in extracted:
        session["intel"][key].extend(extracted[key])

    # agent response
    reply = ""
    if is_scam:
        reply = agent_reply()

    return {
        "scam_detected": is_scam,
        "agent_engaged": is_scam,
        "engagement_metrics": {
            "turns": session["turns"],
            "duration_seconds": int(time.time() - session["start_time"])
        },
        "extracted_intelligence": session["intel"],
        "agent_reply": reply
    }

# -------------------------
# HEALTH CHECK (GET)
# -------------------------

@app.get("/webhook")
def webhook_health_check():
    return {
        "status": "ok",
        "message": "Honeypot endpoint is live"
    }
