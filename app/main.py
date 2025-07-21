from pathlib import Path
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from prometheus_fastapi_instrumentator import Instrumentator

from .routes import enroll, consent, auth, users
from .routes import caption_ws
from .firebase_client import auth as fb_auth, firebase_admin  # NEW
from firebase_admin import exceptions as fb_exc               # NEW

app = FastAPI()

# ───────────────────────────────────────── basics
@app.get("/")
async def root() -> dict[str, str]:
    return {"status": "ok"}

origins = [
    "http://localhost:5174",
    "http://localhost:8000",
    # production front‑end URLs
    "https://gesahni-git-main-7l7ks-projects.vercel.app",
    "https://gesahni.vercel.app",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

Instrumentator().instrument(app).expose(app)

# sessions directory (for face, voice, etc.)
Path("sessions").mkdir(parents=True, exist_ok=True)
app.mount("/sessions", StaticFiles(directory="sessions"), name="sessions")

# ───────────────────────────────────────── auth middleware
@app.middleware("http")
async def session_middleware(request: Request, call_next):
    token = None
    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        token = auth_header.split(" ", 1)[1]

    if token:
        try:
            decoded = fb_auth.verify_id_token(token, check_revoked=True)
            request.state.user_id = decoded["uid"]
        except (fb_exc.InvalidIdTokenError, fb_exc.RevokedIdTokenError):
            # invalid → treat as anonymous; routes can raise 401/403
            pass

    return await call_next(request)

@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}

# ───────────────────────────────────────── routers
app.include_router(enroll.router,  prefix="/enroll")
app.include_router(consent.router, prefix="/consent")
app.include_router(auth.router,    prefix="/auth")
app.include_router(users.router,   prefix="/users")
app.include_router(caption_ws.router, prefix="/ws")
