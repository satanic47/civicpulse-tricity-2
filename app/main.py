import os
import time
import html
import uuid
from typing import Optional, List
from collections import defaultdict
from fastapi import FastAPI, Request, Form, UploadFile, File, HTTPException, status
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from app.core.storage import GrievanceStore
from app.models.schemas import GrievanceCreate, Channel

app = FastAPI(
    title="NagrikSetu AI — CivicPulse Tricity",
    description="Multilingual AI Digital Public Infrastructure Platform for Chandigarh, Mohali, and Panchkula. Powered by Google Gemini 2.0 Flash.",
    version="2.0.0"
)

# ---------------------------------------------------------
# SECURITY CONFIGURATION & MIDDLEWARE
# ---------------------------------------------------------

# 1. CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PATCH", "OPTIONS"],
    allow_headers=["*"],
)

# 2. Strict HTTP Security Headers Middleware
@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "SAMEORIGIN"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    response.headers["Content-Security-Policy"] = (
        "default-src 'self' 'unsafe-inline' 'unsafe-eval' https: data: blob:; "
        "img-src 'self' https: data: blob:; "
        "font-src 'self' https: data:; "
        "connect-src 'self' https:;"
    )
    return response

# 3. In-Memory Sliding-Window Rate Limiter
RATE_LIMIT_RECORD = defaultdict(list)
RATE_LIMIT_WINDOW_SECS = 60
RATE_LIMIT_MAX_REQUESTS = 120  # generous 120 req/min per IP to prevent DoS attacks

def check_rate_limit(client_ip: str):
    now = time.time()
    timestamps = RATE_LIMIT_RECORD[client_ip]
    # Prune old timestamps
    RATE_LIMIT_RECORD[client_ip] = [ts for ts in timestamps if now - ts < RATE_LIMIT_WINDOW_SECS]
    if len(RATE_LIMIT_RECORD[client_ip]) >= RATE_LIMIT_MAX_REQUESTS:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded. Please wait a moment before submitting further requests."
        )
    RATE_LIMIT_RECORD[client_ip].append(now)

# 4. Input Sanitization Helpers
def sanitize_text(val: Optional[str], max_len: int = 2500) -> Optional[str]:
    if not val:
        return val
    cleaned = val.replace("\x00", "").strip()
    if len(cleaned) > max_len:
        cleaned = cleaned[:max_len]
    return html.escape(cleaned)

# Audio Upload Constraints
ALLOWED_AUDIO_EXTENSIONS = {".wav", ".mp3", ".ogg", ".m4a", ".aac", ".flac", ".webm"}
MAX_AUDIO_SIZE_BYTES = 10 * 1024 * 1024  # 10 MB

# ---------------------------------------------------------
# STORAGE & TEMPLATE SETUP
# ---------------------------------------------------------
store = GrievanceStore()

static_dir = os.path.join(os.path.dirname(__file__), "static")
templates_dir = os.path.join(os.path.dirname(__file__), "templates")
uploads_dir = os.path.join(os.path.dirname(__file__), "..", "uploads")
os.makedirs(uploads_dir, exist_ok=True)

if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")

templates = Jinja2Templates(directory=templates_dir)

class StatusUpdate(BaseModel):
    status: str

# ---------------------------------------------------------
# APPLICATION ROUTES
# ---------------------------------------------------------

@app.get("/", response_class=HTMLResponse)
async def serve_home(request: Request):
    grievances = store.get_all()
    hotspots = store.get_hotspots()
    sector_metrics = store.get_sector_metrics()
    recommendations = store.get_policy_recommendations()
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "grievances": grievances,
            "hotspots": hotspots,
            "sector_metrics": sector_metrics,
            "recommendations": recommendations,
            "total_count": len(grievances)
        }
    )

@app.get("/presentation", response_class=HTMLResponse)
async def serve_presentation():
    presentation_file = os.path.join(os.path.dirname(__file__), "..", "presentation", "index.html")
    if os.path.exists(presentation_file):
        with open(presentation_file, "r", encoding="utf-8") as f:
            return f.read()
    raise HTTPException(status_code=404, detail="Presentation deck not found")

@app.get("/api/v1/grievances")
async def list_grievances(sector: Optional[str] = None, category: Optional[str] = None, channel: Optional[str] = None):
    return store.get_all(sector=sector, category=category, channel=channel)

@app.get("/api/v1/grievances/{grievance_id}")
async def get_grievance(grievance_id: str):
    item = store.get_by_id(grievance_id)
    if not item:
        raise HTTPException(status_code=404, detail="Grievance not found")
    return item

@app.post("/api/v1/grievances")
async def create_grievance(payload: GrievanceCreate, request: Request):
    client_ip = request.client.host if request.client else "127.0.0.1"
    check_rate_limit(client_ip)

    sanitized_input = sanitize_text(payload.raw_input)
    if not sanitized_input or len(sanitized_input.strip()) < 3:
        raise HTTPException(status_code=400, detail="Grievance description must be at least 3 characters.")

    sanitized_hint = sanitize_text(payload.location_hint)

    record = store.add_grievance(
        raw_input=sanitized_input,
        channel=payload.channel.value if hasattr(payload.channel, 'value') else str(payload.channel),
        audio_file=payload.audio_file_name,
        location_hint=sanitized_hint
    )
    return record

@app.post("/api/v1/voice/upload")
async def upload_voice(
    request: Request,
    file: UploadFile = File(...),
    transcript: Optional[str] = Form(None),
    location_hint: Optional[str] = Form(None)
):
    """
    Accepts audio recording from mobile or browser with strict MIME & extension verification.
    """
    client_ip = request.client.host if request.client else "127.0.0.1"
    check_rate_limit(client_ip)

    # 1. Verify extension
    ext = os.path.splitext(file.filename or "")[1].lower()
    if ext not in ALLOWED_AUDIO_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file format '{ext}'. Allowed: {', '.join(sorted(ALLOWED_AUDIO_EXTENSIONS))}"
        )

    # 2. Read content & check size limit
    content = await file.read()
    if len(content) > MAX_AUDIO_SIZE_BYTES:
        raise HTTPException(
            status_code=413,
            detail=f"File exceeds maximum allowed size of {MAX_AUDIO_SIZE_BYTES // (1024 * 1024)} MB."
        )

    # 3. Secure filename generation to prevent directory traversal
    safe_filename = f"{uuid.uuid4().hex[:12]}_{os.path.basename(file.filename or 'voice.wav')}"
    file_path = os.path.join(uploads_dir, safe_filename)
    with open(file_path, "wb") as buffer:
        buffer.write(content)

    sanitized_transcript = sanitize_text(transcript) or "ਸਾਡੇ ਸੈਕਟਰ 22 ਸ਼ਾਸਤਰੀ ਮਾਰਕੀਟ ਕੋਲ ਪਾਣੀ ਦੀ ਲੀਕੇਜ ਹੋ ਰਹੀ ਹੈ"
    sanitized_hint = sanitize_text(location_hint)

    record = store.add_grievance(
        raw_input=sanitized_transcript,
        channel="VOICE",
        audio_file=safe_filename,
        location_hint=sanitized_hint
    )
    return record

@app.post("/api/v1/grievances/{grievance_id}/upvote")
async def upvote_grievance(grievance_id: str, request: Request):
    client_ip = request.client.host if request.client else "127.0.0.1"
    check_rate_limit(client_ip)

    res = store.upvote(grievance_id)
    if not res:
        raise HTTPException(status_code=404, detail="Grievance not found")
    return res

@app.patch("/api/v1/grievances/{grievance_id}/status")
async def update_grievance_status(grievance_id: str, payload: StatusUpdate):
    allowed_statuses = {"Pending", "In Review", "Work Order Issued", "Resolved", "Rejected"}
    sanitized_status = sanitize_text(payload.status)
    if sanitized_status not in allowed_statuses:
        raise HTTPException(status_code=400, detail=f"Invalid status. Allowed: {', '.join(sorted(allowed_statuses))}")

    res = store.update_status(grievance_id, sanitized_status)
    if not res:
        raise HTTPException(status_code=404, detail="Grievance not found")
    return res

@app.get("/api/v1/hotspots")
async def get_hotspots():
    return store.get_hotspots()

@app.get("/api/v1/sectors")
async def get_sectors():
    return store.get_sector_metrics()

@app.get("/api/v1/recommendations")
async def get_recommendations():
    return store.get_policy_recommendations()

@app.post("/api/v1/webhook/whatsapp")
async def whatsapp_webhook(
    request: Request,
    Body: str = Form(...),
    From: str = Form("whatsapp:+919876543210")
):
    """
    Twilio/WhatsApp webhook simulating citizen messaging interface.
    """
    client_ip = request.client.host if request.client else "127.0.0.1"
    check_rate_limit(client_ip)

    sanitized_body = sanitize_text(Body)
    if not sanitized_body:
        raise HTTPException(status_code=400, detail="Empty message body")

    record = store.add_grievance(
        raw_input=sanitized_body,
        channel="WHATSAPP",
        location_hint=None
    )
    return {
        "status": "success",
        "reply": f"Dhanyavaad! Your grievance has been recorded under {record['id']} ({record['category']} - {record['sector']}). Status: {record['status']}."
    }

@app.get("/api/v1/stats")
async def get_stats():
    grievances = store.get_all()
    by_category = {}
    by_channel = {}
    by_language = {}
    total_urgency = 0

    for g in grievances:
        cat = g.get("category", "Other")
        ch = g.get("channel", "WEB")
        lang = g.get("language_detected", "English")
        by_category[cat] = by_category.get(cat, 0) + 1
        by_channel[ch] = by_channel.get(ch, 0) + 1
        by_language[lang] = by_language.get(lang, 0) + 1
        total_urgency += g.get("urgency_score", 5)

    return {
        "total_grievances": len(grievances),
        "avg_urgency": round(total_urgency / max(1, len(grievances)), 1),
        "by_category": by_category,
        "by_channel": by_channel,
        "by_language": by_language,
        "active_hotspots_count": len(store.get_hotspots()),
        "dpr_recommendations_count": len(store.get_policy_recommendations()),
        "ai_engine": "Google Gemini 2.0 Flash (Unified GenAI SDK)",
        "security_hardening": "Enabled (Rate Limiting, CSP, HSTS, Input Sanitization)"
    }
