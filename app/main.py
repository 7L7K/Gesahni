from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from prometheus_fastapi_instrumentator import Instrumentator
from fastapi.staticfiles import StaticFiles
from pathlib import Path

from .routes import enroll, consent, auth, users
from .utils.session import get_user
from fastapi import Request

app = FastAPI()

origins = ["http://localhost:5173"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

Instrumentator().instrument(app).expose(app)

# Ensure session directory exists
Path("sessions").mkdir(parents=True, exist_ok=True)
app.mount("/sessions", StaticFiles(directory="sessions"), name="sessions")

@app.middleware("http")
async def session_middleware(request: Request, call_next):
    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        token = auth_header.split(" ", 1)[1]
        user = get_user(token)
        if user:
            request.state.user_id = user
    response = await call_next(request)
    return response

@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}

app.include_router(enroll.router, prefix="/enroll")
app.include_router(consent.router, prefix="/consent")
app.include_router(auth.router, prefix="/auth")
app.include_router(users.router, prefix="/users")
